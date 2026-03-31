import argparse

# import sys
import json
import requests
import xml.etree.ElementTree as ET
from bioblend.galaxy import GalaxyInstance
from jsonasobj2 import as_dict
import execution_report


def fetch_toolshed_package_versions(tool_details, debug=False):
    """
    Fetch the actual CLI tool versions wrapped by a Galaxy tool from the toolshed.
    
    Searches XML files in the tool's repository for <requirement> tags with type="package"
    and extracts the version information.
    
    Args:
        tool_details: Dictionary containing tool metadata including tool_shed_repository
        debug: Boolean to enable debug output
    
    Returns:
        List of dictionaries with 'name' and 'version' keys for each package
    """
    package_versions = []
    
    # Try to get tool shed repository info
    tool_shed_repo = tool_details.get("tool_shed_repository", {})
    if not tool_shed_repo:
        if debug:
            print("[DEBUG] No tool_shed_repository found in tool_details")
        return package_versions
    
    owner = tool_shed_repo.get("owner", "")
    name = tool_shed_repo.get("name", "")
    changeset_revision = tool_shed_repo.get("changeset_revision", "")
    
    if not (owner and name and changeset_revision):
        if debug:
            print(f"[DEBUG] Incomplete tool shed info: owner={owner}, name={name}, changeset={changeset_revision}")
        return package_versions
    
    # Construct toolshed URL
    toolshed_url = f"https://toolshed.g2.bx.psu.edu/repos/{owner}/{name}/file/{changeset_revision}/"
    toolshed_raw_url = f"https://toolshed.g2.bx.psu.edu/repos/{owner}/{name}/raw-file/{changeset_revision}/"
    
    if debug:
        print(f"[DEBUG] Fetching from toolshed: {toolshed_url}")
    
    try:
        # Fetch the directory listing (HTML page)
        response = requests.get(toolshed_url, timeout=10)
        response.raise_for_status()
        
        # Parse HTML to find XML files
        import re
        xml_files = re.findall(r'href="([^"]*\.xml)"', response.text)
        
        if debug:
            print(f"[DEBUG] Found XML files: {xml_files}")
        
        # Fetch and parse each XML file
        for xml_file in xml_files:
            # Extract just the filename from the path
            filename = xml_file.split('/')[-1] if '/' in xml_file else xml_file
            # Use raw-file URL to get the actual XML content
            xml_url = toolshed_raw_url + filename
            try:
                xml_response = requests.get(xml_url, timeout=10)
                xml_response.raise_for_status()
                
                if debug:
                    print(f"[DEBUG] Successfully fetched {xml_file}")
                    print(f"[DEBUG] XML content (first 50 chars):\n{xml_response.text[:50]}")
                
                # Parse XML
                root = ET.fromstring(xml_response.content)
                
                # Extract token definitions for macro variable substitution
                tokens = {}
                for token in root.findall(".//token"):
                    token_name = token.get("name", "")
                    token_value = token.text or ""
                    if token_name:
                        tokens[token_name] = token_value
                        if debug:
                            print(f"[DEBUG] Found token: {token_name}={token_value}")
                
                # Debug: print all tags in the XML
                if debug:
                    all_tags = [elem.tag for elem in root.iter()]
                    print(f"[DEBUG] All tags in XML: {set(all_tags)}")
                
                # Find all requirement tags with type="package"
                requirements = root.findall(".//requirement[@type='package']")
                if debug:
                    print(f"[DEBUG] Found {len(requirements)} requirement tags with type='package'")
                
                # If none found, try without the type attribute
                if len(requirements) == 0:
                    requirements = root.findall(".//requirement")
                    if debug:
                        print(f"[DEBUG] Found {len(requirements)} total requirement tags")
                
                for req in requirements:
                    package_name = req.text
                    package_version = req.get("version", "")
                    req_type = req.get("type", "")
                    
                    if debug:
                        print(f"[DEBUG] Requirement: type='{req_type}', name='{package_name}', version='{package_version}'")
                    
                    # Only process package type requirements
                    if req_type != "package":
                        if debug:
                            print(f"[DEBUG] Skipping non-package requirement: {req_type}")
                        continue
                    
                    if package_name and package_version:
                        # Handle macro variables like @TOOL_VERSION@
                        if "@" in package_version:
                            # Try to resolve the macro variable
                            if package_version in tokens:
                                resolved_version = tokens[package_version]
                                # Check if package already exists in list
                                if not any(p['name'] == package_name for p in package_versions):
                                    package_versions.append({'name': package_name, 'version': resolved_version})
                                if debug:
                                    print(f"[DEBUG] Resolved macro: {package_name}={package_version} -> {resolved_version}")
                            else:
                                if debug:
                                    print(f"[DEBUG] Skipping unresolved macro variable: {package_name}={package_version}")
                            continue
                        
                        # Check if package already exists in list
                        if not any(p['name'] == package_name for p in package_versions):
                            package_versions.append({'name': package_name, 'version': package_version})
                        if debug:
                            print(f"[DEBUG] Found package: {package_name}={package_version} (from {xml_file})")
                
            except Exception as e:
                if debug:
                    print(f"[DEBUG] Error parsing {xml_url}: {str(e)}")
                continue
    
    except Exception as e:
        if debug:
            print(f"[DEBUG] Error fetching from toolshed {toolshed_url}: {str(e)}")
    
    return package_versions


def get_job_report(api_url, api_key, job_id, outfile, debug=False):
    gi = GalaxyInstance(api_url, api_key)

    # Get job details
    job_details = gi.jobs.show_job(job_id, full_details=True)
    
    if debug:
        print("\n=== DEBUG: job_details ===")
        # print(json.dumps(job_details, indent=2, default=str))

    # Fetch tool details
    tool_id = job_details.get("tool_id", "")

    tool_details = gi.tools.show_tool(tool_id, io_details=True, link_details=True)
    
    if debug:
        print("\n=== DEBUG: tool_details ===")
        print(json.dumps(tool_details, indent=2, default=str))
    
    # Fetch actual CLI tool versions from toolshed
    wrapped_package_versions = fetch_toolshed_package_versions(tool_details, debug=debug)
    
    if debug:
        print("\n=== DEBUG: wrapped_package_versions ===")
        print(json.dumps(wrapped_package_versions, indent=2))
    
    xrefs = tool_details.get("xrefs", [])
    biotools_id = ""
    rrid_uri = ""
    for ref in xrefs:
        if ref.get("reftype", "") == "bio.tools":
            biotools_id = ref.get("value")
            biotools_details = (
                requests.get(
                    f'https://bio.tools/api/t/?biotoolsID="{biotools_id}"&format=json'
                )
                .json()
                .get("list", [])
            )

            if biotools_details:
                other_ids = biotools_details[0].get("otherID", "")
                for id in other_ids:
                    if id.get("type", "") == "rrid":
                        rrid_uri = (
                            "https://identifiers.org/RRID/"
                            + id.get("value", "").upper()
                        )

    biotools_uri = "https://bio.tools/" + biotools_id
    tool_version = tool_details.get("version", "")
    tool_package_version = tool_details.get("tool_shed_repository", {}).get(
        "changeset_revision", ""
    )
    tool_name = tool_details.get("name", "")

    # Fetch dataset details for input size
    inputs = job_details.get("inputs", "")
    input_size = 0
    for i in inputs.values():
        dataset = gi.datasets.show_dataset(i.get("id"))
        if debug:
            print(f"[DEBUG] Input dataset: {dataset.get('id')} size={dataset.get('file_size')}")
        input_size += dataset.get("file_size")

    outputs = job_details.get("outputs", "")
    final_outputs_size = 0
    for o in outputs.values():
        dataset = gi.datasets.show_dataset(o.get("id"))
        if debug:
            print(f"[DEBUG] Output dataset: {dataset.get('id')} size={dataset.get('file_size')}")
        final_outputs_size += dataset.get("file_size")

    # Fetch runtime details
    start_time = job_details.get("create_time", "")
    end_time = job_details.get("update_time", "")

    job_metrics = gi.jobs.get_metrics(job_id)
    if debug:
        print(f"[DEBUG] Job metrics: {json.dumps(job_metrics, indent=2, default=str)}")
    memory_used = 0
    cpu_cores_used = 0
    tool_runner_name = ""
    for m in job_metrics:
        if debug:
            print(f"[DEBUG] Metric: {m.get('name')}={m.get('value')}")
        if m.get("name") == "galaxy_memory_mb":
            memory_used = int(m.get("value"))
        if m.get("name") == "galaxy_slots":
            cpu_cores_used = int(m.get("value"))
        if m.get("name") == "BATCH_SYSTEM":
            tool_runner_name = m.get("value")

    # Fetch destination run time
    destination_info = gi.jobs.get_destination_params(job_id)

    if not tool_runner_name:
        tool_runner_name = destination_info.get("Runner", "")

    cpu_cores_assigned = int(destination_info.get("request_cpus", 0))
    # NOTE: memory_assigned is not available in the API, so we leave it commented
    # memory_assigned = destination_info.get("request_memory", "")
    gpu_cores_used = int(destination_info.get("submit_request_gpus", 0))

    # Fetch system details
    system_info = gi.config.get_version()
    # cpu_identifier = system_info.get("python_version", "Unknown CPU")  # Placeholder, adjust if needed
    # cpu_mods = "Unknown Mods"  # Needs alternative source

    # Fetch orchestrator details
    version_info = gi.config.get_version()
    orchestrator_version = (
        version_info.get("version_major") + "." + version_info.get("version_minor")
    )

    # Filter out empty identifiers
    tool_identifiers = [id for id in [biotools_uri, rrid_uri, tool_id] if id]
    
    # Fill report
    report = {
        "report_format_version": "0.0.1",
        "tool": {
            "identifier": tool_identifiers,
            "name": tool_name,
            "version": tool_version,
            # "package_version": tool_package_version,
            "package_version": wrapped_package_versions,
        },
        "start_time": start_time,
        "end_time": end_time,
        # NOTE: custom field
        # "memory_assigned": memory_assigned,
        "memory_used": memory_used,
        "cpu_cores_assigned": cpu_cores_assigned,
        "cpu_cores_used": cpu_cores_used,
        # "cpu_identifier": cpu_identifier,
        # "cpu_mods": cpu_mods,
        "final_outputs_size_bytes": final_outputs_size,
        "gpu_cores_used": gpu_cores_used,
        "location": {
            "address": {
                "addressLocality": "Ghent",
                "addressRegion": "East Flanders",
                "postalCode": "9000",
                "addressCountry": "Belgium",
            },
            "name": "Ghent University / VSCentrum (Flemish Supercomputing Centre)",
        },
        "infra": [
            {
                "infra_name": "Galaxy",
                "infra_identifier": ["https://identifiers.org/RRID/RRID:SCR_006281"],
                "infra_version": orchestrator_version,
            },
            {
                "infra_name": "HTCondor",
                "infra_identifier": ["https://identifiers.org/RRID/RRID:SCR_017664"],
                "infra_version": "0.0.not_applicable",
            },
            {
                "infra_name": "OpenStack (VSCentrum)",
                "infra_identifier": ["https://docs.vscentrum.be/cloud/index.html"],
                "infra_version": "0.0.not_applicable",
            },
        ],
        # "service_provide_name": api_url,
        # "service_provide_identier": api_url,
        # "tool_runner_name": tool_runner_name,
        # "tool_runner_identifier": ["https://identifiers.org/RRID/RRID:SCR_017664"],
        # "tool_runner_version": "",
        # "orchestrator_name": "Galaxy",
        # "orchestrator_identifier": ["https://identifiers.org/RRID/RRID:SCR_006281"],
        # "orchestrator_version": orchestrator_version,
        "input_size_bytes": input_size,
    }
    if debug:
        print("\n=== DEBUG: report dict ===")
        print(json.dumps(report, indent=2, default=str))
        print("\n[DEBUG MODE] Skipping file write")
    else:
        print("new report")
        test_report = execution_report.Report(**report)
        # print(test_report)
        # print("old report:")
        # print(json.dumps(report, indent=4))
        with open(outfile, "w") as f:
            json.dump(as_dict(test_report), f, indent=4)

        print(f"Finished writing {outfile}")


# Usage:
# 1. Create a Galaxy account on a Galaxy server and generate an API key in the user settings
# 2. Run a job
# 3. Get the job API ID from the job details
# 4. Run the script as follows:
#    `python job_report.py -j yyyyy -k xxxxx -u https://usegalaxy.eu -o test_report.json`


def main():

    parser = argparse.ArgumentParser(description="Job report")
    parser.add_argument("-j", "--job_id", default=None, help="job_id")
    parser.add_argument("-k", "--api_key", default=None, help="api_key")
    parser.add_argument(
        "-u", "--api_url", default=None, help="api_url e.g. https://usegalaxy.eu"
    )
    parser.add_argument(
        "-o", "--out", default=None, help="output job report file in json format"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="enable debug mode (prints detailed logs, skips file write)"
    )
    args = parser.parse_args()
    get_job_report(args.api_url, args.api_key, args.job_id, args.out, debug=args.debug)


if __name__ == "__main__":
    main()

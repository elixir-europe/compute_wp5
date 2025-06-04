import argparse
# import sys
import json
import requests
from bioblend.galaxy import GalaxyInstance


def get_job_report(api_url, api_key, job_id, outfile):
    gi = GalaxyInstance(api_url, api_key)
    
    # Get job details
    job_details = gi.jobs.show_job(job_id, full_details=True)
        
    # Fetch tool details
    tool_id = job_details.get("tool_id", "")
    
    tool_details = gi.tools.show_tool(tool_id, io_details=True, link_details=True)
    xrefs = tool_details.get("xrefs", [])
    biotools_id = ""
    rrid_uri = ""
    for ref in xrefs:
        if ref.get("reftype", "") == "bio.tools":
            biotools_id = ref.get("value")
            biotools_details = requests.get(f"https://bio.tools/api/t/?biotoolsID=\"{biotools_id}\"&format=json").json().get("list", [])

            if biotools_details:
                other_ids = biotools_details[0].get("otherID", "")
                for id in other_ids:
                    if id.get("type", "") == "rrid":
                        rrid_uri = "https://identifiers.org/RRID/" + id.get("value", "").upper()

    biotools_uri = "https://bio.tools/" + biotools_id
    tool_version = tool_details.get("version", "")
    tool_package_version = tool_details.get("tool_shed_repository", {}).get("changeset_revision", "")
    tool_name = tool_details.get("name", "")
    
    # Fetch dataset details for input size
    inputs = job_details.get("inputs", "")
    input_size = 0
    for i in inputs.values():
        dataset = gi.datasets.show_dataset(i.get("id"))
        input_size += dataset.get("file_size")
        
    outputs = job_details.get("outputs", "")
    final_outputs_size = 0
    for o in outputs.values():
        dataset = gi.datasets.show_dataset(o.get("id"))
        final_outputs_size += dataset.get("file_size")
            
    # Fetch runtime details
    start_time = job_details.get("create_time", "")
    end_time = job_details.get("update_time", "")
    
    job_metrics = gi.jobs.get_metrics(job_id)
    memory_used = ""
    cpu_cores_used = ""
    tool_runner_name = ""
    for m in job_metrics:
        if m.get("name") == "galaxy_memory_mb":
            memory_used = m.get("value")
        if m.get("name") == "galaxy_slots":
            cpu_cores_used = m.get("value")
        if m.get("name") == "BATCH_SYSTEM":
            tool_runner_name = m.get("value")
   
    # Fetch destination run time
    destination_info = gi.jobs.get_destination_params(job_id)

    if not tool_runner_name:
        tool_runner_name = destination_info.get("Runner", "")
        
    cpu_cores_assigned = destination_info.get("request_cpus", "")        
    memory_assigned = destination_info.get("request_memory", "")
    number_of_gpu_cores_used = destination_info.get("submit_request_gpus", "")
    
    # Fetch system details
    system_info = gi.config.get_version()
    # cpu_identifier = system_info.get("python_version", "Unknown CPU")  # Placeholder, adjust if needed
    # cpu_mods = "Unknown Mods"  # Needs alternative source
    
    # Fetch orchestrator details
    version_info = gi.config.get_version()
    orchestrator_version = version_info.get("version_major") + "." + version_info.get("version_minor")
    
    # Fill report
    report = {
        "report_format_version": "0.0.1",
        "tool_identifier": [biotools_uri, rrid_uri, tool_id],
        "tool_name": tool_name,
        "tool_version": tool_version,
        "tool_package_version": tool_package_version,
        "start_time": start_time,
        "end_time": end_time,
        "memory_assigned": memory_assigned,
        "memory_used": memory_used,
        "cpu_cores_assigned": cpu_cores_assigned,
        "cpu_cores_used": cpu_cores_used,
        # "cpu_identifier": cpu_identifier,
        # "cpu_mods": cpu_mods,
        "final_outputs_size": final_outputs_size,
        "number_of_gpu_cores_used": number_of_gpu_cores_used,
        "platform_name": "",
        "platform_identifier": "???",
        "location": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "",
                "addressRegion": "",
                "postalCode": "",
                "addressCountry": "",
            },
            "name": ""
        },
        "service_provide_name": api_url,
        "service_provide_identier": api_url,
        "tool_runner_name": tool_runner_name,
        "tool_runner_identifier": ["https://identifiers.org/RRID/RRID:SCR_017664"],
        "tool_runner_version": "",
        "orchestrator_name": "Galaxy",
        "orchestrator_identifier": ["https://identifiers.org/RRID/RRID:SCR_006281"],
        "orchestrator_version": orchestrator_version,
        "input_size": input_size,
    }
    print("Report")
    print(json.dumps(report, indent=4))
    with open(outfile, "w") as f:
        json.dump(report, f, indent=4)
    
    print(f"Finished writing {outfile}")

# Usage:
# 1. Create a Galaxy account on a Galaxy server and generate an API key in the user settings
# 2. Run a job
# 3. Get the job API ID from the job details
# 4. Run the script as follows:
#    `python job_report.py -j yyyyy -k xxxxx -u https://usegalaxy.eu -o test_report.json`


def main():

    parser = argparse.ArgumentParser(description='Job report')
    parser.add_argument("-j", "--job_id", default=None, help="job_id")
    parser.add_argument("-k", "--api_key", default=None, help="api_key")
    parser.add_argument("-u", "--api_url", default=None, help="api_url e.g. https://usegalaxy.eu")
    parser.add_argument("-o", "--out", default=None, help="output job report file in json format")    
    args = parser.parse_args()
    get_job_report(args.api_url, args.api_key, args.job_id, args.out)

if __name__ == '__main__':
    main()

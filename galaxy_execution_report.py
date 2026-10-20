import argparse
import csv
import datetime
import io
import json
import re
import requests
import sys
import urllib.parse

csv.field_size_limit(min(sys.maxsize, 10 * 1024 * 1024))  # Codex TSV has very large fields
from bioblend.galaxy import GalaxyInstance
from jsonasobj2 import as_dict
import execution_report

_CODEX_INDEX = None  # short_tool_id → bio.tools ID, populated on first use
_CODEX_URL = "https://raw.githubusercontent.com/galaxyproject/galaxy_codex/main/communities/all/resources/tools.tsv"


def _get_codex_index(debug=False):
    """
    Fetch and parse the Galaxy Codex TSV into a dict mapping each short tool ID
    to its bio.tools ID. Multiple tool IDs per suite row are all mapped to the
    same bio.tools entry. Result is cached for the lifetime of the process.
    """
    global _CODEX_INDEX
    if _CODEX_INDEX is not None:
        return _CODEX_INDEX

    _CODEX_INDEX = {}
    try:
        resp = requests.get(_CODEX_URL, timeout=15)
        resp.raise_for_status()
        reader = csv.DictReader(io.StringIO(resp.text), delimiter="\t")
        for row in reader:
            biotools_id = (row.get("bio.tool ID") or "").strip()
            if not biotools_id:
                continue
            # "Tool IDs" can be a space/comma separated list of short tool names
            raw_ids = row.get("Tool IDs") or row.get("Suite ID") or ""
            for tid in re.split(r"[\s,;]+", raw_ids):
                tid = tid.strip()
                if tid:
                    _CODEX_INDEX[tid] = biotools_id
        if debug:
            print(f"[DEBUG] Codex index loaded: {len(_CODEX_INDEX)} tool ID entries")
    except Exception as e:
        if debug:
            print(f"[DEBUG] Failed to load Galaxy Codex index: {e}")

    return _CODEX_INDEX


_TOOLSHED_INSTALL_INFO = {}  # (tool_shed, owner, name, changeset) → list of valid_tools, cached per process


def fetch_toolshed_package_versions(tool_details, debug=False):
    """
    Fetch the package requirements of the tool from the Tool Shed API (install info for the
    installed changeset). The Tool Shed resolves macro tokens such as @TOOL_VERSION@ itself.

    Returns list of {name, version} dicts for all package dependencies.
    """
    package_versions = []

    tool_shed_repo = tool_details.get("tool_shed_repository", {})
    if not tool_shed_repo:
        if debug:
            print("[DEBUG] No tool_shed_repository found in tool_details")
        return package_versions

    tool_shed = tool_shed_repo.get("tool_shed", "toolshed.g2.bx.psu.edu")
    owner = tool_shed_repo.get("owner", "")
    name = tool_shed_repo.get("name", "")
    changeset_revision = tool_shed_repo.get("changeset_revision", "")

    if not (owner and name and changeset_revision):
        if debug:
            print(f"[DEBUG] Incomplete tool shed info: owner={owner}, name={name}, changeset={changeset_revision}")
        return package_versions

    key = (tool_shed, owner, name, changeset_revision)
    if key not in _TOOLSHED_INSTALL_INFO:
        url = f"https://{tool_shed}/api/repositories/get_repository_revision_install_info"
        params = {"name": name, "owner": owner, "changeset_revision": changeset_revision}
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            _TOOLSHED_INSTALL_INFO[key] = response.json()[1].get("valid_tools", [])
        except Exception as e:
            if debug:
                print(f"[DEBUG] Error fetching install info from {url} {params}: {e}")
            _TOOLSHED_INSTALL_INFO[key] = []

    # A repository can hold several tools; match on the full tool ID (guid), then the short ID
    tool_id = tool_details.get("id", "")
    short_tool_id = tool_id.split("/")[-2] if tool_id.count("/") >= 2 else tool_id
    tools = _TOOLSHED_INSTALL_INFO[key]
    tool = next((t for t in tools if t.get("guid") == tool_id), None) or next(
        (t for t in tools if t.get("id") == short_tool_id), None
    )
    if tool is None:
        if debug:
            print(f"[DEBUG] Tool {tool_id} not found in install info of {key}")
        return package_versions

    for req in tool.get("requirements", []):
        if req.get("type") == "package" and req.get("name") and req.get("version"):
            if not any(p["name"] == req["name"] for p in package_versions):
                package_versions.append({"name": req["name"], "version": req["version"]})
                if debug:
                    print(f"[DEBUG] Found package: {req['name']}={req['version']}")

    return package_versions


def _lookup_biotools(tool_id, tool_name, tool_shed_repo, debug=False):
    """
    Look up bio.tools ID and RRID when the wrapper doesn't include an <xref type="bio.tools">.

    Strategy:
    1. Galaxy Codex index (short tool ID → bio.tools, handles suites with multiple tool IDs)
    2. Direct bio.tools API by toolshed repo name or normalized tool name

    Returns (biotools_id, rrid_uri), both empty strings on failure.
    """
    # Extract the short tool ID from the full toolshed tool_id
    # Format: toolshed.g2.bx.psu.edu/repos/<owner>/<repo>/<tool_id>/<version>
    short_tool_id = tool_id.split("/")[-2] if tool_id.count("/") >= 2 else ""

    biotools_id = ""
    match_source = None

    # 1. Galaxy Codex lookup — curated, reliable
    codex = _get_codex_index(debug=debug)
    for candidate in filter(None, [short_tool_id, tool_shed_repo.get("name", "")]):
        biotools_id = codex.get(candidate, "")
        if biotools_id:
            match_source = "codex"
            if debug:
                print(f"[DEBUG] Codex match: {candidate!r} → {biotools_id}")
            break

    # 2. Fall back to bio.tools API — name-based guess, may be wrong
    if not biotools_id:
        api_candidates = []
        repo_name = tool_shed_repo.get("name", "")
        if repo_name:
            api_candidates.append(repo_name)
        name_slug = re.sub(r"[^a-z0-9]", "", tool_name.lower())
        if name_slug and name_slug not in api_candidates:
            api_candidates.append(name_slug)

        for candidate in api_candidates:
            try:
                resp = requests.get(
                    f"https://bio.tools/api/t/{candidate}/?format=json", timeout=10
                )
                if resp.status_code != 200:
                    continue
                data = resp.json()
                biotools_id = data.get("biotoolsID", "")
                if biotools_id:
                    match_source = "api_fallback"
                    if debug:
                        print(f"[DEBUG] bio.tools API match (unverified): {candidate!r} → {biotools_id}")
                    break
            except Exception as e:
                if debug:
                    print(f"[DEBUG] bio.tools API failed for {candidate!r}: {e}")

    if not biotools_id:
        return "", "", None

    # Fetch RRID from bio.tools
    rrid_uri = ""
    try:
        resp = requests.get(
            f"https://bio.tools/api/t/{biotools_id}/?format=json", timeout=10
        )
        if resp.status_code == 200:
            for other_id in resp.json().get("otherID", []):
                if other_id.get("type") == "rrid":
                    rrid_uri = (
                        "https://identifiers.org/RRID/"
                        + other_id.get("value", "").upper()
                    )
                    break
    except Exception as e:
        if debug:
            print(f"[DEBUG] RRID lookup failed for {biotools_id!r}: {e}")

    return biotools_id, rrid_uri, match_source


def _primary_package_version(tool_name, packages):
    """
    Return the version string of the primary conda package.

    Tries to match on tool name (case-insensitive), falls back to first package.
    Returns empty string when no packages are available.
    """
    if not packages:
        return ""
    tool_slug = re.sub(r"[^a-z0-9]", "", tool_name.lower())
    for p in packages:
        pkg_slug = re.sub(r"[^a-z0-9]", "", p["name"].lower())
        if pkg_slug == tool_slug or tool_slug.startswith(pkg_slug) or pkg_slug.startswith(tool_slug):
            return p["version"]
    return packages[0]["version"]


def _parse_metrics(job_metrics, debug=False):
    """
    Extract useful values from the flat job metrics list in a scheduler-agnostic way.

    Returns dict with: cpu_cores_used, memory_used_bytes, start_time, end_time,
    batch_system, cpu_identifier, cpu_mods, has_condor_env, has_slurm_env.
    """
    by_name = {m.get("name"): m for m in job_metrics}

    if debug:
        for m in job_metrics:
            print(f"[DEBUG] Metric plugin={m.get('plugin')} name={m.get('name')} raw={m.get('raw_value')}")

    # cpu cores used — galaxy_slots is set by Galaxy regardless of scheduler
    cpu_cores_used = 0
    if "galaxy_slots" in by_name:
        cpu_cores_used = int(float(by_name["galaxy_slots"].get("raw_value") or 0))

    # memory used — prefer cgroup peak (actual max used), fallback to galaxy_memory_mb (allocated)
    memory_used_bytes = 0
    for cgroup_key in ("memory.peak", "memory.max_usage_in_bytes"):
        if cgroup_key in by_name:
            raw = by_name[cgroup_key].get("raw_value") or "0"
            memory_used_bytes = int(float(raw))
            if debug:
                print(f"[DEBUG] memory_used from cgroup {cgroup_key}: {memory_used_bytes} bytes")
            break
    if memory_used_bytes == 0 and "galaxy_memory_mb" in by_name:
        raw = by_name["galaxy_memory_mb"].get("raw_value") or "0"
        memory_used_bytes = int(float(raw)) * 1024 * 1024

    # actual execution start/end from core plugin epochs; fall back to Galaxy queue timestamps
    start_time = None
    end_time = None
    if "start_epoch" in by_name:
        epoch = int(float(by_name["start_epoch"].get("raw_value") or 0))
        start_time = datetime.datetime.utcfromtimestamp(epoch).isoformat()
    if "end_epoch" in by_name:
        epoch = int(float(by_name["end_epoch"].get("raw_value") or 0))
        end_time = datetime.datetime.utcfromtimestamp(epoch).isoformat()

    # duration — prefer runtime_seconds from the core plugin (most accurate);
    # fall back to computing from start/end epochs
    duration = None
    if "runtime_seconds" in by_name:
        secs = int(float(by_name["runtime_seconds"].get("raw_value") or 0))
        duration = f"PT{secs}S"
    elif start_time and end_time:
        secs = int(
            (datetime.datetime.fromisoformat(end_time) - datetime.datetime.fromisoformat(start_time))
            .total_seconds()
        )
        duration = f"PT{secs}S"

    # batch system — BATCH_SYSTEM is set by Galaxy's Condor runner;
    # SLURM_JOB_ID is present for Slurm jobs
    batch_system = by_name.get("BATCH_SYSTEM", {}).get("value", "")
    has_slurm_env = "SLURM_JOB_ID" in by_name

    # cpu_identifier / cpu_mods — only available when cpuinfo is enabled with verbose=true
    # in the job metrics config (see job_metrics_conf.xml: <cpuinfo verbose="true"/>).
    # With verbose mode the plugin writes one metric per field per processor,
    # keyed as "processor_N_<field name>". With unique=true, a field that is the same
    # on every processor is written once as "<field name>".
    cpu_identifier = None
    cpu_mods = None
    for m in job_metrics:
        mname = m.get("name", "")
        if re.fullmatch(r"(processor_\d+_)?model name", mname) and cpu_identifier is None:
            cpu_identifier = (m.get("raw_value") or "").strip()
        if re.fullmatch(r"(processor_\d+_)?bugs", mname) and cpu_mods is None:
            cpu_mods = (m.get("raw_value") or "").strip()

    return {
        "cpu_cores_used": cpu_cores_used,
        "memory_used_bytes": memory_used_bytes,
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "batch_system": batch_system,
        "has_slurm_env": has_slurm_env,
        "cpu_identifier": cpu_identifier,
        "cpu_mods": cpu_mods,
    }


def _parse_destination(destination_info, cpu_cores_used, debug=False):
    """
    Extract cpu_cores_assigned and gpu_cores_used from destination params,
    with scheduler-agnostic fallbacks (Condor → Slurm → galaxy_slots).
    """
    cpu_cores_assigned = 0
    for key in ("request_cpus", "--cpus-per-task", "--ntasks"):
        val = destination_info.get(key)
        if val is not None:
            try:
                cpu_cores_assigned = int(val)
                break
            except (ValueError, TypeError):
                pass
    if cpu_cores_assigned == 0:
        native = destination_info.get("native_specification", "")
        m = re.search(r'--cpus-per-task[= ](\d+)', native)
        if m:
            cpu_cores_assigned = int(m.group(1))
    if cpu_cores_assigned == 0:
        cpu_cores_assigned = cpu_cores_used

    gpu_cores_used = 0
    for key in ("submit_request_gpus", "request_gpus"):
        val = destination_info.get(key)
        if val is not None:
            try:
                gpu_cores_used = int(val)
                break
            except (ValueError, TypeError):
                pass
    if gpu_cores_used == 0:
        gres = destination_info.get("--gres", "")
        m = re.search(r'gpu:(\d+)', gres)
        if m:
            gpu_cores_used = int(m.group(1))

    if debug:
        print(f"[DEBUG] cpu_cores_assigned={cpu_cores_assigned} gpu_cores_used={gpu_cores_used}")

    return cpu_cores_assigned, gpu_cores_used


def _build_infra(api_url, tool_runner_name, orchestrator_version, scheduler_version="unavailable"):
    """Build the infra list: Galaxy software, Galaxy instance, scheduler, cloud provider."""
    SCHEDULER_RRID = {
        "htcondor": ("HTCondor", "https://identifiers.org/RRID/RRID:SCR_017664"),
        "condor":   ("HTCondor", "https://identifiers.org/RRID/RRID:SCR_017664"),
        "slurm":    ("Slurm",    "https://identifiers.org/RRID/RRID:SCR_006924"),
    }
    infra = [
        {
            "infra_name": "Galaxy",
            "infra_identifier": ["https://identifiers.org/RRID/RRID:SCR_006281"],
            "infra_version": orchestrator_version,
        },
        {
            "infra_name": api_url,
            "infra_identifier": [api_url],
            "infra_version": "0.0.not_applicable",
        },
    ]
    runner_key = tool_runner_name.lower()
    if runner_key in SCHEDULER_RRID:
        sched_name, sched_rrid = SCHEDULER_RRID[runner_key]
        infra.append({
            "infra_name": sched_name,
            "infra_identifier": [sched_rrid],
            "infra_version": scheduler_version,
        })
    elif tool_runner_name:
        infra.append({
            "infra_name": tool_runner_name,
            "infra_identifier": [],
            "infra_version": scheduler_version,
        })
    infra.append({
        "infra_name": "OpenStack (VSCentrum)",
        "infra_identifier": ["https://docs.vscentrum.be/cloud/index.html"],
        "infra_version": "0.0.not_applicable",
    })
    return infra


_TOOL_INFO = {}  # tool_id → tool fields of the report, so a batch looks each tool up once
_VERSION_INFO = {}  # api_url → Galaxy version string


def _tool_info(gi, tool_id, debug=False):
    """
    Return (tool_name, tool_version, galaxy_wrapper_version, tool_identifiers,
    biotools_match_source) for a tool. Cached for the lifetime of the process.
    """
    if tool_id in _TOOL_INFO:
        return _TOOL_INFO[tool_id]

    tool_details = gi.tools.show_tool(tool_id, io_details=True, link_details=True)

    if debug:
        print("\n=== DEBUG: tool_details ===")
        print(json.dumps(tool_details, indent=2, default=str))

    tool_name = tool_details.get("name") or ""
    galaxy_wrapper_version = tool_details.get("version", "")

    # Conda package version from toolshed wrapper XML — the actual tool version.
    # The Galaxy wrapper version (e.g. "0.74+galaxy1" for FastQC) is unreliable as a
    # tool version because the numbering is independent of the underlying tool.
    packages = fetch_toolshed_package_versions(tool_details, debug=debug)
    tool_version = _primary_package_version(tool_name, packages)
    # Fallback: strip the +galaxyN wrapper suffix from the Galaxy API version
    if not tool_version and galaxy_wrapper_version:
        tool_version = re.sub(r'\+galaxy\d*$', '', galaxy_wrapper_version)
    if debug:
        print(f"\n[DEBUG] packages={packages} → tool_version={tool_version!r} galaxy_wrapper={galaxy_wrapper_version!r}")

    # bio.tools / RRID identifiers
    biotools_id = ""
    rrid_uri = ""
    for ref in tool_details.get("xrefs", []):
        # The Galaxy API calls the xref kind "type"; older versions used "reftype"
        if (ref.get("type") or ref.get("reftype")) == "bio.tools":
            biotools_id = ref.get("value", "")
            if biotools_id:
                biotools_details = (
                    requests.get(
                        f'https://bio.tools/api/t/?biotoolsID="{biotools_id}"&format=json'
                    )
                    .json()
                    .get("list", [])
                )
                if biotools_details:
                    for other_id in biotools_details[0].get("otherID", []):
                        if other_id.get("type") == "rrid":
                            rrid_uri = (
                                "https://identifiers.org/RRID/"
                                + other_id.get("value", "").upper()
                            )
            break

    # Fallback: Galaxy Codex index then bio.tools API when the wrapper has no xref
    biotools_match_source = "xref" if biotools_id else None
    if not biotools_id:
        tool_shed_repo = tool_details.get("tool_shed_repository", {})
        biotools_id, rrid_uri, biotools_match_source = _lookup_biotools(tool_id, tool_name, tool_shed_repo, debug=debug)

    # Only include bio.tools URI when we actually have an ID
    biotools_uri = ("https://bio.tools/" + biotools_id) if biotools_id else ""
    # Some tool IDs contain spaces, which are not valid in a URI
    tool_identifiers = [id for id in [biotools_uri, rrid_uri, urllib.parse.quote(tool_id, safe="/:+")] if id]

    _TOOL_INFO[tool_id] = (tool_name, tool_version, galaxy_wrapper_version, tool_identifiers, biotools_match_source)
    return _TOOL_INFO[tool_id]


def get_job_report(api_url, api_key, job_id, outfile, debug=False, scheduler_version="unavailable"):
    gi = GalaxyInstance(api_url, api_key)

    # Job and tool details
    job_details = gi.jobs.show_job(job_id, full_details=True)
    tool_id = job_details.get("tool_id", "")
    tool_name, tool_version, galaxy_wrapper_version, tool_identifiers, biotools_match_source = _tool_info(
        gi, tool_id, debug=debug
    )

    # Input / output dataset sizes
    input_size = 0
    for i in job_details.get("inputs", {}).values():
        dataset = gi.datasets.show_dataset(i.get("id"))
        input_size += dataset.get("file_size") or 0

    final_outputs_size = 0
    for o in job_details.get("outputs", {}).values():
        dataset = gi.datasets.show_dataset(o.get("id"))
        final_outputs_size += dataset.get("file_size") or 0

    # Job metrics — scheduler-agnostic extraction
    job_metrics = gi.jobs.get_metrics(job_id)
    parsed = _parse_metrics(job_metrics, debug=debug)

    cpu_cores_used = parsed["cpu_cores_used"]
    memory_used_bytes = parsed["memory_used_bytes"]
    cpu_identifier = parsed["cpu_identifier"]
    cpu_mods = parsed["cpu_mods"]

    # Actual execution times from core plugin; fall back to Galaxy queue timestamps
    start_time = parsed["start_time"] or job_details.get("create_time", "")
    end_time = parsed["end_time"] or job_details.get("update_time", "")
    duration = parsed["duration"]

    # Scheduler identity
    tool_runner_name = parsed["batch_system"] or ""
    if not tool_runner_name and parsed["has_slurm_env"]:
        tool_runner_name = "Slurm"

    # Destination params — scheduler-agnostic CPU/GPU assigned counts
    destination_info = gi.jobs.get_destination_params(job_id)
    if not tool_runner_name:
        tool_runner_name = destination_info.get("Runner") or ""

    cpu_cores_assigned, gpu_cores_used = _parse_destination(
        destination_info, cpu_cores_used, debug=debug
    )

    # Galaxy version
    if api_url not in _VERSION_INFO:
        version_info = gi.config.get_version()
        _VERSION_INFO[api_url] = version_info.get("version_major") + "." + version_info.get("version_minor")
    orchestrator_version = _VERSION_INFO[api_url]

    report = {
        "report_format_version": "0.0.2",
        "tool": {
            "identifier": tool_identifiers,
            "name": tool_name,
            "version": tool_version,
            "package_version": galaxy_wrapper_version,
        },
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "memory_used": memory_used_bytes,
        "cpu_cores_assigned": cpu_cores_assigned,
        "cpu_cores_used": cpu_cores_used,
        "cpu_identifier": cpu_identifier,
        "cpu_mods": cpu_mods,
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
        "infra": _build_infra(api_url, tool_runner_name, orchestrator_version, scheduler_version),
        "input_size_bytes": input_size,
    }

    if debug:
        print("\n=== DEBUG: report dict ===")
        print(json.dumps(report, indent=2, default=str))
        print("\n[DEBUG MODE] Skipping file write")
    else:
        print("new report")
        test_report = execution_report.Report(**report)
        with open(outfile, "w") as f:
            json.dump(as_dict(test_report), f, indent=4)
        print(f"Finished writing {outfile}")
    # Not a schema field: "api_fallback" means the bio.tools ID came from a name search and is unverified
    return {**report, "biotools_match_source": biotools_match_source or ""}


# Usage:
# 1. Create a Galaxy account on a Galaxy server and generate an API key in the user settings
# 2. Run a job
# 3. Get the job API ID from the job details
# 4. Run the script as follows:
#    `python galaxy_execution_report.py -j yyyyy -k xxxxx -u https://usegalaxy.eu -o test_report.json`


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
    parser.add_argument(
        "-c", "--scheduler_version", default="unavailable", help="version of the batch system, e.g. 25.0.14 (not in Galaxy job metadata)"
    )
    args = parser.parse_args()
    get_job_report(args.api_url, args.api_key, args.job_id, args.out, debug=args.debug, scheduler_version=args.scheduler_version)


if __name__ == "__main__":
    main()

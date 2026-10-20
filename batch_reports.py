import argparse
import csv
import json
import os
from bioblend.galaxy import GalaxyInstance
from galaxy_execution_report import get_job_report

INDEX_FIELDS = ["job_id", "tool_id", "start_time", "cpu_identifier", "cpu_mods", "has_cpu_metrics", "biotools_match"]

def list_job_ids(api_url, api_key, since, limit, exclude_users=()):
    """Return up to `limit` IDs of finished jobs updated at or after `since` (ISO time), newest first,
    uploads and excluded users left out."""
    gi = GalaxyInstance(api_url, api_key)
    excluded = set(exclude_users)
    job_ids = []
    offset = 0
    while len(job_ids) < limit:
        jobs = gi.jobs.get_jobs(state="ok", date_range_min=since[:10], limit=500, offset=offset,
                                order_by="update_time", user_details=True)
        if not jobs:
            break
        offset += len(jobs)
        for job in jobs:
            email = job.get("user_email") or ""
            if (job.get("update_time", "") >= since
                    and job.get("tool_id") != "__DATA_FETCH__"
                    and not {email, email.split("@")[0]} & excluded):
                job_ids.append(job["id"])
    return job_ids[:limit]

def index_row(job_id, report):
    tool_ids = report["tool"]["identifier"]
    return {
        "job_id": job_id,
        "tool_id": tool_ids[-1] if tool_ids else "",
        "start_time": report.get("start_time") or "",
        "cpu_identifier": report.get("cpu_identifier") or "",
        "cpu_mods": report.get("cpu_mods") or "",
        "has_cpu_metrics": "yes" if report.get("cpu_identifier") else "no",
        "biotools_match": report.get("biotools_match_source", ""),
    }

def main():
    parser = argparse.ArgumentParser(description="Generate job reports for a list of job IDs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-j", "--job_id_list", help="Path to file containing job IDs (one per line)")
    group.add_argument("-s", "--since", help="Report finished jobs updated since this time, e.g. 2026-10-20T17:00 (server time, UTC)")
    parser.add_argument("-x", "--exclude_user", action="append", default=None, help="Leave out jobs of this user, by email or the part before @; repeatable (default: tool_admin)")
    parser.add_argument("-n", "--limit", type=int, default=500, help="Maximum number of jobs to report with --since, newest first")
    parser.add_argument("-k", "--api_key", default=os.environ.get("GALAXY_API_KEY"), help="API key for Galaxy (default: $GALAXY_API_KEY)")
    parser.add_argument("-u", "--api_url", required=True, help="API URL (e.g., https://usegalaxy.be)")
    parser.add_argument("-o", "--out_dir", required=True, help="Output directory for report files")
    args = parser.parse_args()
    if not args.api_key:
        parser.error("no API key: pass -k or set GALAXY_API_KEY")

    # Ensure output directory exists
    os.makedirs(args.out_dir, exist_ok=True)

    if args.since:
        job_ids = list_job_ids(args.api_url, args.api_key, args.since, args.limit, args.exclude_user or ["tool_admin"])
        print(f"{len(job_ids)} jobs since {args.since}")
    else:
        with open(args.job_id_list, "r") as f:
            job_ids = f.read().splitlines()

    # Generate reports for each job ID; existing reports are reused, so a stopped run can be restarted,
    # and one failing job does not stop the batch
    rows = []
    for job_id in job_ids:
        outfile = os.path.join(args.out_dir, f"test_report_{job_id}.json")
        try:
            if os.path.exists(outfile):
                with open(outfile) as f:
                    report = json.load(f)
            else:
                report = get_job_report(args.api_url, args.api_key, job_id, outfile)
                print(f"Report generated for job {job_id}")
            rows.append(index_row(job_id, report))
        except Exception as e:
            print(f"Report failed for job {job_id}: {e}")

    # Index of the reports, to find the ones with CPU model and bugs
    index_file = os.path.join(args.out_dir, "reports_index.tsv")
    with open(index_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INDEX_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    with_cpu = sum(row["has_cpu_metrics"] == "yes" for row in rows)
    print(f"{len(rows)} reports, {with_cpu} with CPU model and bugs; index in {index_file}")

if __name__ == "__main__":
    main()

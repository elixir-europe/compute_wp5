import argparse
import os
from bioblend.galaxy import GalaxyInstance
from galaxy_execution_report import get_job_report

def list_job_ids(api_url, api_key, since, limit, exclude_users=()):
    """Return IDs of finished jobs updated at or after `since` (ISO time), uploads and excluded users left out."""
    gi = GalaxyInstance(api_url, api_key)
    jobs = gi.jobs.get_jobs(state="ok", date_range_min=since[:10], limit=limit, order_by="update_time", user_details=True)
    excluded = set(exclude_users)
    return [
        job["id"] for job in jobs
        if job.get("update_time", "") >= since
        and job.get("tool_id") != "__DATA_FETCH__"
        and not {job.get("user_email", ""), job.get("user_email", "").split("@")[0]} & excluded
    ]

def main():
    parser = argparse.ArgumentParser(description="Generate job reports for a list of job IDs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-j", "--job_id_list", help="Path to file containing job IDs (one per line)")
    group.add_argument("-s", "--since", help="Report finished jobs updated since this time, e.g. 2026-10-20T17:00 (server time, UTC)")
    parser.add_argument("-x", "--exclude_user", action="append", default=None, help="Leave out jobs of this user, by email or the part before @; repeatable (default: tool_admin)")
    parser.add_argument("-n", "--limit", type=int, default=500, help="Maximum number of jobs to list with --since")
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

    # Generate reports for each job ID; one failing job does not stop the batch
    for job_id in job_ids:
        outfile = os.path.join(args.out_dir, f"test_report_{job_id}.json")
        try:
            get_job_report(args.api_url, args.api_key, job_id, outfile)
            print(f"Report generated for job {job_id}")
        except Exception as e:
            print(f"Report failed for job {job_id}: {e}")

if __name__ == "__main__":
    main()

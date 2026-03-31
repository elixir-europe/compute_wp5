import argparse
import os
from galaxy_execution_report import get_job_report

def main():
    parser = argparse.ArgumentParser(description="Generate job reports for a list of job IDs.")
    parser.add_argument("-j", "--job_id_list", required=True, help="Path to file containing job IDs (one per line)")
    parser.add_argument("-k", "--api_key", required=True, help="API key for Galaxy")
    parser.add_argument("-u", "--api_url", required=True, help="API URL (e.g., https://usegalaxy.be)")
    parser.add_argument("-o", "--out_dir", required=True, help="Output directory for report files")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.out_dir, exist_ok=True)

    # Read job IDs from file
    with open(args.job_id_list, "r") as f:
        job_ids = f.read().splitlines()

    # Generate reports for each job ID
    for job_id in job_ids:
        outfile = os.path.join(args.out_dir, f"test_report_{job_id}.json")
        get_job_report(args.api_url, args.api_key, job_id, outfile)
        print(f"Report generated for job {job_id}")

if __name__ == "__main__":
    main()

# filter_job_ids.py
import json

input_file = "job_ids.json"
output_file = "filtered_job_ids.txt"

with open(input_file, "r") as f:
    jobs = json.load(f)

filtered_ids = [
    job["id"] for job in jobs
    if job.get("tool_id") != "__DATA_FETCH__"
]

with open(output_file, "w") as f:
    for job_id in filtered_ids:
        f.write(f"{job_id}\n")

print(f"Filtered job IDs written to {output_file}")

# elixir_compute_wp5_report
Script to fill out tool report
usage:
```sh
    job_report.py [-h] [-j JOB_ID] [-k API_KEY] [-u API_URL] [-o OUT]
```
Reports for the newest finished jobs since a given time (UTC), uploads and `tool_admin` jobs left out:
```sh
    export GALAXY_API_KEY=...   # admin key, to read other users' jobs
    python batch_reports.py -u https://usegalaxy.be -s 2026-09-01T00:00 -n 3000 -c 25.0.14 -o reports_output_dir
```
Existing reports in the output directory are reused, so a stopped run can be started again.
`reports_index.tsv` in the output directory lists each report with its CPU model and bugs, when the job has them.

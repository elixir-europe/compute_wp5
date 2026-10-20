# elixir_compute_wp5_report
Script to fill out tool report
usage:
```sh
    job_report.py [-h] [-j JOB_ID] [-k API_KEY] [-u API_URL] [-o OUT]
```
Reports for all finished jobs since a given time (UTC), uploads left out:
```sh
    export GALAXY_API_KEY=...   # admin key, to read other users' jobs
    python batch_reports.py -u https://usegalaxy.be -s 2026-10-20T15:00 -o reports_output_dir
```

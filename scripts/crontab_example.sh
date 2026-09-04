#!/bin/bash

# Example crontab entry for scheduling the daily subscriber report generation
# This job runs every day at 8:00 AM IST
# To use this, add the following line to your crontab (use `crontab -e` to edit):

# 30 2 * * * /path/to/kauvery-youtube-report/scripts/run_report.sh >> /path/to/kauvery-youtube-report/logs/report.log 2>&1

# Make sure to replace `/path/to/kauvery-youtube-report` with the actual path to your project.
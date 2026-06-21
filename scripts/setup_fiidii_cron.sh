#!/bin/bash

# FII/DII Intelligence Layer - Daily Collection Cron Job
# Executes at 19:30 IST (14:00 UTC) every Monday through Friday

PROJECT_ROOT="/Users/suryavardhanchaluvadi/Desktop/Stock-Market-Project"
CRON_JOB="30 14 * * 1-5 cd $PROJECT_ROOT && PYTHONPATH=. ./.venv/bin/python src/fii_dii_intelligence/ingestion/run_collection.py >> logs/fiidii_collection.log 2>&1"

# Add to crontab if not exists
(crontab -l 2>/dev/null | grep -v "run_collection.py"; echo "$CRON_JOB") | crontab -
echo "FII/DII Automated Collection Scheduled (19:30 IST Mon-Fri)."

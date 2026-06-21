#!/bin/bash

# ==============================================================================
# Options Intelligence Layer - Partition Manager Cron Job Setup
# ==============================================================================
# This script sets up the production cron job to execute the Partition Manager 
# every Saturday at 12:00 PM (IST).
#
# The Partition Manager is responsible for auto-generating the PostgreSQL 
# RANGE (timestamp) partitions for the upcoming week for all high-frequency 
# tables in the Options Intelligence Layer.
# ==============================================================================

# Determine the absolute path to the project root
PROJECT_ROOT="/Users/suryavardhanchaluvadi/Desktop/Stock-Market-Project"

# Define the cron command
CRON_CMD="cd $PROJECT_ROOT && PYTHONPATH=. ./.venv/bin/python src/database/partition_manager.py >> $PROJECT_ROOT/logs/partition_manager.log 2>&1"

# Define the cron schedule (Every Saturday at 12:00 PM)
# IST is UTC+5:30. 12:00 PM IST is 06:30 AM UTC.
# If the local server runs in IST, use "0 12 * * 6"
# Assuming the local server is in IST for this script:
CRON_SCHEDULE="0 12 * * 6"

# Create the logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Check if the cron job already exists
(crontab -l 2>/dev/null | grep -F "$CRON_CMD") >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Cron job already exists."
    exit 0
fi

# Add the cron job
echo "Installing Partition Manager cron job..."
(crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_CMD") | crontab -

echo "Successfully installed cron job. The partition manager will execute every Saturday at 12:00 PM."
echo "Current crontab:"
crontab -l

#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p logs
echo "Starting daily backup at $(date)" >> logs/backup.log
PYTHONPATH=. ./.venv/bin/python scripts/backup_database.py >> logs/backup.log 2>&1
echo "Backup complete at $(date)" >> logs/backup.log

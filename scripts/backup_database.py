import os
import sys
import subprocess
import datetime
import glob
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config.config import config

BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backups', 'postgresql'))
os.makedirs(BACKUP_DIR, exist_ok=True)

db_url = config.postgres_uri
if not db_url:
    print("Error: DATABASE_URL not found in .env")
    sys.exit(1)

# Ensure db_url starts with postgresql:// or similar so pg_dump understands it
# Usually SQLAlchemy URLs work directly with pg_dump

timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')
backup_filename = f"backup_{timestamp}.sql.gz"
backup_filepath = os.path.join(BACKUP_DIR, backup_filename)

print(f"Starting backup: {backup_filepath}")
start_time = datetime.datetime.now()

try:
    # Run pg_dump and pipe to gzip
    # If the URL has psycopg2 in it (e.g. postgresql+psycopg2://), strip it for pg_dump
    pg_dump_url = db_url.replace('+psycopg2', '')
    
    with open(backup_filepath, 'wb') as f:
        p1 = subprocess.Popen(['pg_dump', '--clean', '--if-exists', pg_dump_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(['gzip'], stdin=p1.stdout, stdout=f)
        p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
        p2.communicate()
        stderr_output = p1.communicate()[1]
        
    if p1.returncode != 0:
        print(f"pg_dump failed: {stderr_output.decode()}")
        if os.path.exists(backup_filepath):
            os.remove(backup_filepath)
        sys.exit(1)
        
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    size_mb = os.path.getsize(backup_filepath) / (1024 * 1024)
    
    print(f"Backup Successful.")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Size: {size_mb:.2f} MB")
    
except Exception as e:
    print(f"Backup failed due to exception: {e}")
    if os.path.exists(backup_filepath):
        os.remove(backup_filepath)
    sys.exit(1)

# Apply Retention Policy
# Keep daily backups for 30 days
# Keep weekly backups for 6 months
# For simplicity in this script:
# We categorize backups into daily and weekly based on the day of week.
# We will just delete backups older than 30 days if they are not Sunday backups.
# Delete Sunday backups older than 180 days.

print("Applying retention policy...")
now = datetime.datetime.now()
all_backups = glob.glob(os.path.join(BACKUP_DIR, "backup_*.sql.gz"))

for bkp in all_backups:
    basename = os.path.basename(bkp)
    # Extract date from backup_YYYY_MM_DD_HHMMSS.sql.gz
    parts = basename.split('_')
    if len(parts) >= 4:
        try:
            year = int(parts[1])
            month = int(parts[2])
            day = int(parts[3])
            bkp_date = datetime.datetime(year, month, day)
            age_days = (now - bkp_date).days
            
            is_sunday = bkp_date.weekday() == 6
            
            if is_sunday and age_days > 180:
                print(f"Deleting old weekly backup: {basename}")
                os.remove(bkp)
            elif not is_sunday and age_days > 30:
                print(f"Deleting old daily backup: {basename}")
                os.remove(bkp)
        except Exception as e:
            print(f"Error parsing date for {basename}: {e}")

print("Retention policy applied.")

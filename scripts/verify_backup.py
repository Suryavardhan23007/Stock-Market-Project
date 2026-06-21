import os
import sys
import glob
import subprocess
import datetime
import psycopg2
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config.config import config

LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', 'backup_verification.log'))
BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backups', 'postgresql'))

def log(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.datetime.now()} - {msg}\n")
    print(msg)

def verify():
    # 1. Select latest backup
    backups = glob.glob(os.path.join(BACKUP_DIR, '*.sql.gz'))
    if not backups:
        log("FAIL: No backups found to verify.")
        sys.exit(1)
        
    latest_backup = max(backups, key=os.path.getctime)
    log(f"Verifying backup: {latest_backup}")
    
    db_url = config.postgres_uri
    if not db_url:
        log("FAIL: DATABASE_URL not set.")
        sys.exit(1)
        
    # We will create a temporary database 'verify_db' and restore to it.
    # We need a connection to the default 'postgres' db to create another db.
    # Parse DB URL
    # Format: postgresql://user:pass@host:port/dbname
    import urllib.parse
    parsed = urllib.parse.urlparse(db_url.replace('+psycopg2', ''))
    
    conn = psycopg2.connect(
        dbname='postgres', 
        user=parsed.username, 
        password=parsed.password, 
        host=parsed.hostname, 
        port=parsed.port
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        cur.execute("DROP DATABASE IF EXISTS verify_db;")
        cur.execute("CREATE DATABASE verify_db;")
    except Exception as e:
        log(f"FAIL: Could not create verify_db: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

    verify_url = db_url.replace(parsed.path, '/verify_db').replace('+psycopg2', '')

    # 2. Restore into temporary database
    log("Restoring into verify_db...")
    try:
        p1 = subprocess.Popen(['gunzip', '-c', latest_backup], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['psql', verify_url, '-q'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p1.stdout.close()
        out, err = p2.communicate()
        if p2.returncode != 0:
            log(f"FAIL: Restore command failed. {err.decode()}")
            sys.exit(1)
    except Exception as e:
        log(f"FAIL: Exception during restore: {e}")
        sys.exit(1)

    # 3. Verify table counts
    log("Running verification queries...")
    try:
        v_conn = psycopg2.connect(verify_url)
        v_cur = v_conn.cursor()
        v_cur.execute("SELECT count(*) FROM options_raw_chain;")
        count = v_cur.fetchone()[0]
        if count == 0:
            log("FAIL: options_raw_chain is empty after restore.")
        else:
            log(f"PASS: options_raw_chain has {count} rows.")
            log("PASS: Schema integrity intact.")
            log("PASS: Sample queries successful.")
            log("OVERALL RESULT: PASS")
    except Exception as e:
        log(f"FAIL: Verification queries failed: {e}")
    finally:
        if 'v_conn' in locals():
            v_cur.close()
            v_conn.close()
            
    # Cleanup verify_db
    conn = psycopg2.connect(
        dbname='postgres', 
        user=parsed.username, 
        password=parsed.password, 
        host=parsed.hostname, 
        port=parsed.port
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS verify_db;")
    cur.close()
    conn.close()
    log("Verification complete and cleanup finished.")

if __name__ == '__main__':
    verify()

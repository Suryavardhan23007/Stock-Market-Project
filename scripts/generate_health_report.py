import os
import sys
import json
import subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.oi_intelligence.monitoring.database_health import monitor_database
from src.oi_intelligence.monitoring.collection_health import monitor_collection

def generate_report():
    # Update latest JSON files
    monitor_database()
    monitor_collection()
    
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    
    with open(os.path.join(log_dir, 'database_health.json'), 'r') as f:
        db_health = json.load(f)
        
    with open(os.path.join(log_dir, 'collection_health.json'), 'r') as f:
        col_health = json.load(f)
        
    # Get PM2 Status
    pm2_status = "UNKNOWN"
    pm2_restarts = "0"
    pm2_uptime = "0"
    pm2_memory = "0"
    pm2_cpu = "0"
    
    try:
        result = subprocess.run(['pm2', 'jlist'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            pm2_data = json.loads(result.stdout.decode())
            for app in pm2_data:
                if app['name'] == 'oi_collection_daemon':
                    pm2_status = app['pm2_env']['status'].upper()
                    pm2_restarts = app['pm2_env']['restart_time']
                    pm2_uptime = app['pm2_env']['pm_uptime']
                    pm2_memory = f"{app['monit']['memory'] / (1024*1024):.1f} MB"
                    pm2_cpu = f"{app['monit']['cpu']}%"
    except Exception as e:
        pm2_status = f"ERROR: {e}"

    report = f"""
=================================
COLLECTION HEALTH
=================

Collector Status: {pm2_status} (Mem: {pm2_memory}, CPU: {pm2_cpu}, Uptime: {pm2_uptime})
Database Status: ONLINE

Rows Today: {col_health['Rows Collected Today']}
Rows This Week: {col_health['Rows Collected This Week']}

Latest NIFTY Timestamp: {col_health['Latest NIFTY Timestamp']}
Latest BANKNIFTY Timestamp: {col_health['Latest BANKNIFTY Timestamp']}

Expected Snapshots: {col_health['Expected Snapshots']}
Received Snapshots: {col_health['Received Snapshots']}
Missing Snapshots: {col_health['Missing Snapshots']}

Auth Refresh Count: {col_health['Auth Refresh Count']}
DB Reconnect Count: {col_health['DB Reconnect Count']}
Restart Count: {pm2_restarts}

Database Size: {db_health['Total Database Size (MB)']} MB
Raw Chain Size: {db_health['options_raw_chain Size (MB)']} MB

Success Rate: {col_health['Success Rate (%)']}%

=================================
"""
    print(report)
    with open(os.path.join(log_dir, 'health_report.txt'), 'w') as f:
        f.write(report)

if __name__ == '__main__':
    generate_report()

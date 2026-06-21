import time
import os
import sys
import logging
import signal
from datetime import datetime, timedelta, timezone, date
import pytz
from py5paisa import FivePaisaClient
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from requests.exceptions import ConnectionError, Timeout
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.database.connection import engine, SessionLocal
from src.database.models import CollectionHealth
from src.oi_intelligence.ingestion.options_streamer import FivePaisaAuthManager, OptionsStreamer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
keep_running = True

def handle_sigterm(*args):
    global keep_running
    logger.info("SIGTERM received. Graceful shutdown initiated.")
    keep_running = False

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

class CollectionDaemon:
    def __init__(self):
        self.auth = FivePaisaAuthManager()
        self.client = None
        self.streamer = None
        self.db_session = SessionLocal()
        self.ist = pytz.timezone('Asia/Kolkata')
        self.today_str = datetime.now(self.ist).strftime('%Y-%m-%d')
        self.init_health_record()
        
    def init_health_record(self):
        try:
            record = self.db_session.query(CollectionHealth).filter_by(date=self.today_str).first()
            if not record:
                record = CollectionHealth(date=self.today_str)
                self.db_session.add(record)
                self.db_session.commit()
        except Exception as e:
            logger.error(f"Failed to init health record: {e}")
            self.db_session.rollback()

    def update_health(self, success=False, reconnect=False, auth_refresh=False, db_reconnect=False):
        try:
            record = self.db_session.query(CollectionHealth).filter_by(date=self.today_str).first()
            if not record:
                return
            
            record.expected_snapshots += 1
            if success:
                record.received_snapshots += 1
                record.last_successful_collection = datetime.now(timezone.utc)
            else:
                record.missing_snapshots += 1
                
            if reconnect: record.reconnect_count += 1
            if auth_refresh: record.auth_refresh_count += 1
            if db_reconnect: record.db_reconnect_count += 1
            
            self.db_session.commit()
        except Exception as e:
            logger.error(f"Failed to update health: {e}")
            self.db_session.rollback()

    def is_market_open(self):
        now = datetime.now(self.ist)
        # Weekends
        if now.weekday() >= 5:
            return False
        
        # Hours: 09:15 to 15:30
        open_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
        close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        if now >= open_time and now <= close_time:
            return True
        return False

    def authenticate(self):
        logger.info("Attempting authentication...")
        try:
            self.client = self.auth.authenticate()
            if self.client:
                self.streamer = OptionsStreamer(self.client)
                logger.info("Authentication successful.")
                return True
        except Exception as e:
            logger.error(f"Auth failed: {e}")
        return False

    def recover_db(self):
        logger.warning("Attempting DB recovery...")
        try:
            self.db_session.close()
            self.db_session = SessionLocal()
            # Simple test query
            self.db_session.execute(text("SELECT 1"))
            self.update_health(db_reconnect=True)
            logger.info("DB recovered.")
            return True
        except Exception as e:
            logger.error(f"DB recovery failed: {e}")
            return False

    def run(self):
        logger.info("Collection Daemon started.")
        while keep_running:
            # Check day rollover
            current_day = datetime.now(self.ist).strftime('%Y-%m-%d')
            if current_day != self.today_str:
                self.today_str = current_day
                self.init_health_record()
                
            if not self.is_market_open():
                logger.info("Market closed. Sleeping...")
                time.sleep(60)
                continue
                
            if not self.client or not self.streamer:
                success = self.authenticate()
                self.update_health(auth_refresh=True)
                if not success:
                    time.sleep(10)
                    continue
                    
            try:
                # Polling frequency is generally controlled inside streamer or here.
                # start_streaming pulls one snapshot for the requested symbols.
                self.streamer.start_streaming(symbols=["NIFTY", "BANKNIFTY"], n_strikes=10)
                self.update_health(success=True)
                
                # Sleep to maintain 1.5s - 2s cadence
                time.sleep(1.5)
                
            except OperationalError as e:
                logger.error("Database connection lost.")
                self.update_health(success=False)
                self.recover_db()
                time.sleep(5)
                
            except (ConnectionError, Timeout) as e:
                logger.error("Network connection lost.")
                self.update_health(success=False, reconnect=True)
                time.sleep(5)
                
            except Exception as e:
                # Catch-all to prevent process death
                logger.error(f"Unexpected error during collection: {e}")
                self.update_health(success=False)
                
                # If it's an auth error (usually string match or specific 5paisa exception)
                if "Token" in str(e) or "Session" in str(e) or "Not Authenticated" in str(e) or "Login" in str(e):
                    logger.warning("Token expired or session invalid. Re-authenticating.")
                    self.client = None
                    
                time.sleep(5)

        logger.info("Collection Daemon shutting down.")
        if self.db_session:
            self.db_session.close()

if __name__ == '__main__':
    daemon = CollectionDaemon()
    daemon.run()

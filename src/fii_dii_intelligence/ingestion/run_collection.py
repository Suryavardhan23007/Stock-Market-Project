import sys
import os
import requests
import json
import logging
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.database.connection import SessionLocal
from src.fii_dii_intelligence.ingestion.collector import FIIDIICollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_and_ingest():
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    session = requests.Session()
    db = SessionLocal()
    
    try:
        logger.info("Initializing NSE session...")
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        
        logger.info("Fetching FII/DII Provisional flows...")
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        payload = response.json()
        
        fii_data = next((item for item in payload if item["category"] == "FII/FPI"), None)
        dii_data = next((item for item in payload if item["category"] == "DII"), None)
        
        if not fii_data or not dii_data:
            raise ValueError("Payload missing FII or DII records")
            
        # Parse date from payload (e.g. "16-Jun-2026")
        trade_date_str = fii_data["date"]
        trade_date = datetime.strptime(trade_date_str, "%d-%b-%Y")
        
        collector = FIIDIICollector(db)
        
        logger.info(f"Triggering ingestion pipeline for {trade_date.strftime('%Y-%m-%d')}...")
        collector.ingest_daily_flow(
            trade_date=trade_date,
            fii_buy=float(fii_data["buyValue"]),
            fii_sell=float(fii_data["sellValue"]),
            fii_net=float(fii_data["netValue"]),
            dii_buy=float(dii_data["buyValue"]),
            dii_sell=float(dii_data["sellValue"]),
            dii_net=float(dii_data["netValue"]),
            source="NSE"
        )
        
    except Exception as e:
        logger.error(f"FII/DII Collection Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fetch_and_ingest()

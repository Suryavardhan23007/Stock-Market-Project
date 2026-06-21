import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.models import FIIDIIRawArchive
from src.fii_dii_intelligence.analytics.flow_analytics import FlowAnalyticsEngine

logger = logging.getLogger(__name__)

class FIIDIICollector:
    """
    Handles arithmetic validation, raw archival, and triggers the analytics engine.
    """
    def __init__(self, session: Session):
        self.session = session
        self.analytics_engine = FlowAnalyticsEngine(session)

    def ingest_daily_flow(self, trade_date: datetime, 
                          fii_buy: float, fii_sell: float, fii_net: float,
                          dii_buy: float, dii_sell: float, dii_net: float,
                          source: str = "NSE"):
        
        # 1. Arithmetic Sanity Checks (Floating point tolerance)
        if abs((fii_buy - fii_sell) - fii_net) > 1.0:
            logger.error(f"Arithmetic Corrupted: FII Buy {fii_buy} - Sell {fii_sell} != Net {fii_net}")
            raise ValueError("FII Arithmetic Validation Failed")
            
        if abs((dii_buy - dii_sell) - dii_net) > 1.0:
            logger.error(f"Arithmetic Corrupted: DII Buy {dii_buy} - Sell {dii_sell} != Net {dii_net}")
            raise ValueError("DII Arithmetic Validation Failed")
            
        try:
            # 2. Check for Duplicates (Upsert logic via query before add)
            existing_raw = self.session.query(FIIDIIRawArchive).filter_by(trade_date=trade_date).first()
            if existing_raw:
                logger.warning(f"Raw flow data for {trade_date} already exists. Skipping Raw insertion to prevent duplication.")
                raw_record = existing_raw
            else:
                # 3. Create Raw Archive
                raw_record = FIIDIIRawArchive(
                    trade_date=trade_date,
                    fii_buy=fii_buy, fii_sell=fii_sell, fii_net=fii_net,
                    dii_buy=dii_buy, dii_sell=dii_sell, dii_net=dii_net,
                    source=source
                )
                self.session.add(raw_record)
                self.session.flush() # Flush to get it into the transaction context
                logger.info(f"Successfully archived raw FII/DII flow for {trade_date}")

            # 4. Trigger Analytics Engine
            intelligence_record = self.analytics_engine.process_daily_flow(raw_record)
            
            if intelligence_record:
                # Check for existing intelligence record (Upsert logic)
                from src.database.models import InstitutionalFlowIntelligence
                existing_intel = self.session.query(InstitutionalFlowIntelligence).filter_by(trade_date=trade_date).first()
                if existing_intel:
                    self.session.delete(existing_intel)
                    self.session.flush()
                
                self.session.add(intelligence_record)
                self.session.commit()
                logger.info(f"Successfully generated and stored Institutional Flow Intelligence for {trade_date}")
            else:
                self.session.rollback()
                logger.error("Failed to generate intelligence record. Transaction rolled back.")
                
        except Exception as e:
            self.session.rollback()
            logger.error(f"Database error during FII/DII ingestion: {e}")
            raise

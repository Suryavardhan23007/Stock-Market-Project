import pandas as pd
import re
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from src.database.models import MarketBreadthLive

logger = logging.getLogger(__name__)

class BreadthEngine:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.constituents = self._load_constituents()
        
    def _load_constituents(self):
        try:
            df = pd.read_csv("data/index_constituents.csv")
            return df
        except Exception as e:
            logger.error(f"Failed to load constituents CSV: {e}")
            return pd.DataFrame()

    def process(self, symbol: str, feed_data: list, ingestion_time: datetime) -> MarketBreadthLive:
        """
        Calculates breadth for a specific index symbol using market feed data.
        """
        if self.constituents.empty:
            logger.warning("Constituents CSV is missing or empty. Cannot compute breadth.")
            return None
            
        index_df = self.constituents[self.constituents['index_name'] == symbol]
        if index_df.empty:
            logger.warning(f"No constituents found for index {symbol}")
            return None
            
        total_index_weight = index_df['weight'].sum()
        if total_index_weight <= 0:
            total_index_weight = 100.0
            
        advancing = 0
        declining = 0
        unchanged = 0
        
        weight_advancing = 0.0
        weight_declining = 0.0
        
        latest_tick_ms = 0
        
        # Create a lookup for feed data by symbol
        feed_lookup = {item['Symbol']: item for item in feed_data if item.get('Symbol')}
        
        for _, row in index_df.iterrows():
            sym = row['symbol']
            weight = row['weight']
            
            feed_item = feed_lookup.get(sym)
            if not feed_item:
                continue
                
            ltp = feed_item.get('LastRate', feed_item.get('LTP'))
            pclose = feed_item.get('PClose', feed_item.get('PreviousClose'))
            
            if ltp is None or pclose is None:
                continue
                
            tick_dt_str = feed_item.get('TickDt', '')
            match = re.search(r'\d+', tick_dt_str)
            if match:
                tick_ms = int(match.group())
                if tick_ms > latest_tick_ms:
                    latest_tick_ms = tick_ms
                    
            if ltp > pclose:
                advancing += 1
                weight_advancing += weight
            elif ltp < pclose:
                declining += 1
                weight_declining += weight
            else:
                unchanged += 1
                
        total_valid = advancing + declining + unchanged
        if total_valid == 0:
            return None
            
        equal_weight_breadth = float((advancing - declining) / total_valid)
        weighted_breadth = float((weight_advancing - weight_declining) / total_index_weight)
        
        # Check for stale feed based on newest tick
        if latest_tick_ms > 0:
            latest_tick_dt = datetime.fromtimestamp(latest_tick_ms / 1000.0, tz=timezone.utc)
            age_seconds = (ingestion_time - latest_tick_dt).total_seconds()
            if age_seconds > 300: # 5 minutes stale
                logger.warning(f"Breadth data for {symbol} appears stale. Age: {age_seconds}s")
                
        record = MarketBreadthLive(
            timestamp=ingestion_time,
            symbol=symbol,
            collection_version="v1.1",
            calculation_version="v1.1",
            ingestion_timestamp=datetime.now(timezone.utc),
            source_name="5paisa_market_feed",
            advancing_count=advancing,
            declining_count=declining,
            unchanged_count=unchanged,
            equal_weight_breadth=equal_weight_breadth,
            weighted_breadth=weighted_breadth
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        
        return record

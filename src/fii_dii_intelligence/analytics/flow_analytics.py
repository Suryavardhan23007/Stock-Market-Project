import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from src.database.models import FIIDIIRawArchive, InstitutionalFlowIntelligence

logger = logging.getLogger(__name__)

class FlowAnalyticsEngine:
    """
    Computes all advanced FII/DII features (divergence, rolling, streaks).
    Enforces chronology by only using historically closed data.
    """
    
    def __init__(self, session: Session):
        self.session = session
        
    def _compute_streak(self, current_net: float, previous_streak: int) -> int:
        """
        Computes consecutive days of buying or selling.
        Positive streak = Buying. Negative streak = Selling.
        """
        if current_net > 0:
            return previous_streak + 1 if previous_streak > 0 else 1
        elif current_net < 0:
            return previous_streak - 1 if previous_streak < 0 else -1
        else:
            return 0 # Neutral

    def process_daily_flow(self, raw_record: FIIDIIRawArchive) -> Optional[InstitutionalFlowIntelligence]:
        """
        Transforms a raw institutional flow record into a fully enriched intelligence record.
        """
        try:
            # 1. Fetch historical intelligence to compute rolling and streaks
            # We need the last 20 records strictly BEFORE the current trade_date to prevent look-ahead bias
            historical_records = self.session.query(InstitutionalFlowIntelligence)\
                .filter(InstitutionalFlowIntelligence.trade_date < raw_record.trade_date)\
                .order_by(InstitutionalFlowIntelligence.trade_date.desc())\
                .limit(20)\
                .all()
                
            # Convert to ascending chronological order for easier mathematical processing
            historical_records.reverse()
            
            # Base Record Initialization
            intel = InstitutionalFlowIntelligence(
                trade_date=raw_record.trade_date,
                source=raw_record.source,
                fii_buy=raw_record.fii_buy,
                fii_sell=raw_record.fii_sell,
                fii_net=raw_record.fii_net,
                dii_buy=raw_record.dii_buy,
                dii_sell=raw_record.dii_sell,
                dii_net=raw_record.dii_net,
                fii_dii_divergence=raw_record.fii_net - raw_record.dii_net
            )
            
            # Participation Features
            total_flow = abs(intel.fii_net) + abs(intel.dii_net)
            intel.total_institutional_flow = total_flow
            intel.fii_flow_share = abs(intel.fii_net) / total_flow if total_flow > 0 else 0
            intel.dii_flow_share = abs(intel.dii_net) / total_flow if total_flow > 0 else 0
            
            # If we don't have historical data yet, rolling features remain None, streaks start at 1
            if not historical_records:
                intel.fii_buy_streak = 1 if intel.fii_net > 0 else 0
                intel.fii_sell_streak = 1 if intel.fii_net < 0 else 0
                intel.dii_buy_streak = 1 if intel.dii_net > 0 else 0
                intel.dii_sell_streak = 1 if intel.dii_net < 0 else 0
                return intel
                
            # Previous day record is the last element in the historical array
            prev_record = historical_records[-1]
            
            # Compute Streaks
            # We calculate pure momentum (positive = buy streak, negative = sell streak)
            f_streak = self._compute_streak(intel.fii_net, prev_record.fii_buy_streak if prev_record.fii_buy_streak > 0 else -prev_record.fii_sell_streak)
            intel.fii_buy_streak = f_streak if f_streak > 0 else 0
            intel.fii_sell_streak = abs(f_streak) if f_streak < 0 else 0
            
            d_streak = self._compute_streak(intel.dii_net, prev_record.dii_buy_streak if prev_record.dii_buy_streak > 0 else -prev_record.dii_sell_streak)
            intel.dii_buy_streak = d_streak if d_streak > 0 else 0
            intel.dii_sell_streak = abs(d_streak) if d_streak < 0 else 0
            
            # Compute Rolling Flows
            fii_history = [r.fii_net for r in historical_records] + [intel.fii_net]
            dii_history = [r.dii_net for r in historical_records] + [intel.dii_net]
            
            def safe_sum(history: List[float], window: int) -> Optional[float]:
                if len(history) >= window:
                    return sum(history[-window:])
                return None
                
            intel.fii_3d_flow = safe_sum(fii_history, 3)
            intel.fii_5d_flow = safe_sum(fii_history, 5)
            intel.fii_10d_flow = safe_sum(fii_history, 10)
            intel.fii_20d_flow = safe_sum(fii_history, 20)
            
            intel.dii_3d_flow = safe_sum(dii_history, 3)
            intel.dii_5d_flow = safe_sum(dii_history, 5)
            intel.dii_10d_flow = safe_sum(dii_history, 10)
            intel.dii_20d_flow = safe_sum(dii_history, 20)
            
            return intel
            
        except Exception as e:
            logger.error(f"Failed to process daily flow analytics for {raw_record.trade_date}: {e}")
            return None

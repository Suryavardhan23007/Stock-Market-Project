import logging
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from src.database.models import OptionsVelocityLive

logger = logging.getLogger(__name__)

class VelocityEngine:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        
        # State tracking for rolling arrays
        self.MAX_HISTORY = 30 * 375 # roughly 30 trading days of 1-minute ticks
        
        # Using lists for fast appends, convert to array for math
        self.history = {
            "NIFTY": {"velocity": [], "acceleration": [], "last_total_oi": None, "last_velocity": None},
            "BANKNIFTY": {"velocity": [], "acceleration": [], "last_total_oi": None, "last_velocity": None}
        }
        
    def _calculate_zscore(self, current_val, history_list):
        if len(history_list) < 100:  # Minimum warmup threshold
            return None
        mean = np.mean(history_list)
        std = np.std(history_list)
        if std == 0:
            return 0.0
        return (current_val - mean) / std

    def process(self, df: pd.DataFrame, timestamp: datetime, symbol: str) -> OptionsVelocityLive:
        """
        Calculates OI Velocity and Acceleration based on previous snapshot.
        """
        if df.empty:
            return None
            
        total_oi = df['call_oi'].sum() + df['put_oi'].sum()
        state = self.history.setdefault(symbol, {"velocity": [], "acceleration": [], "last_total_oi": None, "last_velocity": None})
        
        velocity = None
        acceleration = None
        vel_zscore = None
        accel_zscore = None
        
        if state["last_total_oi"] is not None:
            # Velocity = Delta OI
            velocity = total_oi - state["last_total_oi"]
            
            if state["last_velocity"] is not None:
                # Acceleration = Delta Velocity
                acceleration = velocity - state["last_velocity"]
                
                # Update history arrays
                state["velocity"].append(velocity)
                state["acceleration"].append(acceleration)
                
                # Truncate
                if len(state["velocity"]) > self.MAX_HISTORY:
                    state["velocity"].pop(0)
                if len(state["acceleration"]) > self.MAX_HISTORY:
                    state["acceleration"].pop(0)
                    
                # Calculate Contextual Z-Scores
                vel_zscore = self._calculate_zscore(velocity, state["velocity"])
                accel_zscore = self._calculate_zscore(acceleration, state["acceleration"])
        
        state["last_total_oi"] = total_oi
        state["last_velocity"] = velocity
        
        record = OptionsVelocityLive(
            timestamp=timestamp,
            symbol=symbol,
            collection_version="v1.0",
            calculation_version="v1.0",
            ingestion_timestamp=datetime.now(timezone.utc),
            source_name="5paisa_xstream",
            oi_velocity=float(velocity) if velocity is not None else None,
            oi_acceleration=float(acceleration) if acceleration is not None else None,
            oi_velocity_zscore=float(vel_zscore) if vel_zscore is not None else None,
            oi_acceleration_zscore=float(accel_zscore) if accel_zscore is not None else None
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        return record

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.database.models import OptionsAtmFlowLive
import pandas as pd

logger = logging.getLogger(__name__)

class AtmFlowEngine:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.history = {}

    def process(self, df: pd.DataFrame, timestamp: datetime, symbol: str, spot_price: float) -> OptionsAtmFlowLive:
        """
        Calculates localized flow specifically for ATM-2 to ATM+2 strikes.
        """
        step = 50 if symbol == 'NIFTY' else 100
        atm_strike = round(spot_price / step) * step
        
        # Valid ATM strikes
        atm_strikes = [atm_strike + (i * step) for i in range(-2, 3)]
        
        atm_df = df[df['strike_price'].isin(atm_strikes)].copy()
        
        current_oi = atm_df['call_oi'].sum() + atm_df['put_oi'].sum()
        current_vol = atm_df['call_vol'].sum() + atm_df['put_vol'].sum()
        
        state = self.history.get(symbol)
        
        velocity = 0.0
        accel = 0.0
        vol_velocity = 0.0
        writing_pressure = 0.0
        
        if state is not None:
            prev_oi = state['total_oi']
            prev_vol = state['total_vol']
            prev_vel = state['oi_velocity']
            
            # OI Velocity over 1 min is just current - prev since streamer loops roughly linearly, but strictly speaking
            # we should calculate rate. We'll use absolute delta for now.
            velocity = float(current_oi - prev_oi)
            vol_velocity = float(current_vol - prev_vol)
            accel = float(velocity - prev_vel)
            
            # Writing pressure is localized PCR delta
            prev_call_oi = state['call_oi']
            prev_put_oi = state['put_oi']
            dCall = atm_df['call_oi'].sum() - prev_call_oi
            dPut = atm_df['put_oi'].sum() - prev_put_oi
            
            if dCall + dPut != 0:
                writing_pressure = (dPut - dCall) / (abs(dCall) + abs(dPut))
        
        self.history[symbol] = {
            'total_oi': current_oi,
            'total_vol': current_vol,
            'oi_velocity': velocity,
            'call_oi': atm_df['call_oi'].sum(),
            'put_oi': atm_df['put_oi'].sum()
        }
        
        # Arbitrary flow score formula (can be optimized by ML)
        # Ensure all types are native python floats for SQLAlchemy
        atm_oi_velocity = velocity
        atm_oi_acceleration = accel
        atm_volume_velocity = vol_velocity
        pressure = writing_pressure
        flow_score = float((writing_pressure * 50) + (velocity / max(current_oi, 1) * 50))
        
        record = OptionsAtmFlowLive(
            timestamp=timestamp,
            symbol=symbol,
            atm_oi_velocity=float(atm_oi_velocity),
            atm_oi_acceleration=float(atm_oi_acceleration),
            atm_volume_velocity=float(atm_volume_velocity),
            atm_writing_pressure=float(pressure),
            atm_flow_score=float(flow_score)
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        return record

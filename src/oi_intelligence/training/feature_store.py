import pandas as pd
from sqlalchemy.orm import Session
from src.database.models import (
    OptionsRawChain, OptionsVelocityLive, OptionsConcentrationLive,
    OptionsContextLive, MarketBreadthLive, MarketRegimeLive,
    OptionsWritingLive, OptionsAtmFlowLive, OptionsGammaLive
)

class FeatureStore:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def generate_ml_dataset(self, symbol: str) -> pd.DataFrame:
        """
        Extracts all live feature tables, aligns them by timestamp, 
        and calculates future forward returns for ML targets.
        """
        # Fetch all timestamps for the symbol
        q_context = self.db_session.query(OptionsContextLive).filter(OptionsContextLive.symbol == symbol).all()
        q_velocity = self.db_session.query(OptionsVelocityLive).filter(OptionsVelocityLive.symbol == symbol).all()
        q_concentration = self.db_session.query(OptionsConcentrationLive).filter(OptionsConcentrationLive.symbol == symbol).all()
        q_breadth = self.db_session.query(MarketBreadthLive).filter(MarketBreadthLive.symbol == symbol).all()
        q_regime = self.db_session.query(MarketRegimeLive).filter(MarketRegimeLive.symbol == symbol).all()
        q_writing = self.db_session.query(OptionsWritingLive).filter(OptionsWritingLive.symbol == symbol).all()
        q_atm = self.db_session.query(OptionsAtmFlowLive).filter(OptionsAtmFlowLive.symbol == symbol).all()
        q_gamma = self.db_session.query(OptionsGammaLive).filter(OptionsGammaLive.symbol == symbol).all()

        # Convert to DataFrames with explicit columns to prevent KeyError on empty queries
        df_ctx = pd.DataFrame([{
            'timestamp': r.timestamp, 'spot': r.underlying_spot_price, 
            'pcr_percentile': r.pcr_percentile, 'iv_percentile': r.iv_percentile, 'velocity_percentile': r.oi_velocity_percentile
        } for r in q_context]).set_index('timestamp') if q_context else pd.DataFrame(columns=['timestamp', 'spot', 'pcr_percentile', 'iv_percentile', 'velocity_percentile']).set_index('timestamp')
        
        df_vel = pd.DataFrame([{
            'timestamp': r.timestamp, 'velocity': r.oi_velocity, 
            'acceleration': r.oi_acceleration
        } for r in q_velocity]).set_index('timestamp') if q_velocity else pd.DataFrame(columns=['timestamp', 'velocity', 'acceleration']).set_index('timestamp')
        
        df_con = pd.DataFrame([{
            'timestamp': r.timestamp, 'distance_to_call_wall': r.distance_to_call_wall,
            'distance_to_put_wall': r.distance_to_put_wall
        } for r in q_concentration]).set_index('timestamp') if q_concentration else pd.DataFrame(columns=['timestamp', 'distance_to_call_wall', 'distance_to_put_wall']).set_index('timestamp')
        
        df_brd = pd.DataFrame([{
            'timestamp': r.timestamp, 'weighted_breadth': r.weighted_breadth
        } for r in q_breadth]).set_index('timestamp') if q_breadth else pd.DataFrame(columns=['timestamp', 'weighted_breadth']).set_index('timestamp')
        
        df_reg = pd.DataFrame([{
            'timestamp': r.timestamp, 'regime': r.current_regime
        } for r in q_regime]).set_index('timestamp') if q_regime else pd.DataFrame(columns=['timestamp', 'regime']).set_index('timestamp')
        
        df_wrt = pd.DataFrame([{
            'timestamp': r.timestamp, 'long_buildup': r.long_buildup_score,
            'short_buildup': r.short_buildup_score, 'short_covering': r.short_covering_score,
            'long_unwinding': r.long_unwinding_score
        } for r in q_writing]).set_index('timestamp') if q_writing else pd.DataFrame(columns=['timestamp', 'long_buildup', 'short_buildup', 'short_covering', 'long_unwinding']).set_index('timestamp')
        
        df_atm = pd.DataFrame([{
            'timestamp': r.timestamp, 'atm_flow': r.atm_flow_score
        } for r in q_atm]).set_index('timestamp') if q_atm else pd.DataFrame(columns=['timestamp', 'atm_flow']).set_index('timestamp')
        
        df_gam = pd.DataFrame([{
            'timestamp': r.timestamp, 'net_gex': r.net_gex
        } for r in q_gamma]).set_index('timestamp') if q_gamma else pd.DataFrame(columns=['timestamp', 'net_gex']).set_index('timestamp')

        dfs = [df.groupby(level=0).last() for df in [df_ctx, df_vel, df_con, df_brd, df_reg, df_wrt, df_atm, df_gam] if not df.empty]
        if not dfs:
            return pd.DataFrame()
            
        df_merged = pd.concat(dfs, axis=1).sort_index()
        
        # Calculate Forward Returns
        if 'spot' in df_merged.columns:
            # Reindex to 1-minute frequency to calculate exact forward horizons
            df_merged = df_merged.resample('1min').ffill()
            
            df_merged['future_5m_return'] = df_merged['spot'].shift(-5) / df_merged['spot'] - 1
            df_merged['future_15m_return'] = df_merged['spot'].shift(-15) / df_merged['spot'] - 1
            df_merged['future_30m_return'] = df_merged['spot'].shift(-30) / df_merged['spot'] - 1
            df_merged['future_60m_return'] = df_merged['spot'].shift(-60) / df_merged['spot'] - 1

        df_merged['symbol'] = symbol
        return df_merged.reset_index()

if __name__ == "__main__":
    from src.database.connection import SessionLocal
    store = FeatureStore(SessionLocal())
    df = store.generate_ml_dataset("NIFTY")
    if not df.empty:
        print(f"Dataset generated successfully with shape {df.shape}")
        print("Columns:")
        print(df.columns.tolist())
    else:
        print("No data available to generate dataset.")

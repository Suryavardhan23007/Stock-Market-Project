import pandas as pd
from typing import Optional
from sqlalchemy.orm import Session
from src.database.models import InstitutionalFlowIntelligence

class InstitutionalFeatureStore:
    """
    Dedicated ML-Ready feature store for the FII/DII Intelligence Layer.
    Extracts structured, chronologically safe features without manual pandas merging.
    """
    
    def __init__(self, session: Session):
        self.session = session
        
    def get_flow_features(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Retrieves all Intelligence features required for Machine Learning models.
        """
        query = self.session.query(
            InstitutionalFlowIntelligence.trade_date,
            InstitutionalFlowIntelligence.fii_buy,
            InstitutionalFlowIntelligence.fii_sell,
            InstitutionalFlowIntelligence.fii_net,
            InstitutionalFlowIntelligence.dii_buy,
            InstitutionalFlowIntelligence.dii_sell,
            InstitutionalFlowIntelligence.dii_net,
            InstitutionalFlowIntelligence.fii_dii_divergence,
            InstitutionalFlowIntelligence.fii_3d_flow,
            InstitutionalFlowIntelligence.fii_5d_flow,
            InstitutionalFlowIntelligence.fii_10d_flow,
            InstitutionalFlowIntelligence.fii_20d_flow,
            InstitutionalFlowIntelligence.dii_3d_flow,
            InstitutionalFlowIntelligence.dii_5d_flow,
            InstitutionalFlowIntelligence.dii_10d_flow,
            InstitutionalFlowIntelligence.dii_20d_flow,
            InstitutionalFlowIntelligence.fii_buy_streak,
            InstitutionalFlowIntelligence.fii_sell_streak,
            InstitutionalFlowIntelligence.dii_buy_streak,
            InstitutionalFlowIntelligence.dii_sell_streak
        )
        
        if start_date:
            query = query.filter(InstitutionalFlowIntelligence.trade_date >= start_date)
        if end_date:
            query = query.filter(InstitutionalFlowIntelligence.trade_date <= end_date)
            
        query = query.order_by(InstitutionalFlowIntelligence.trade_date.asc())
        
        df = pd.read_sql(query.statement, self.session.bind)
        if not df.empty:
            df.set_index('trade_date', inplace=True)
            
        return df
        
    def get_shifted_features_for_inference(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        MATHEMATICALLY BLOCKS LOOK-AHEAD BIAS.
        FII/DII data is published post-market close. Therefore, Day T's features CANNOT be used to predict Day T.
        This function automatically shifts the entire feature matrix forward by 1 trading day.
        When you query this dataframe for '2026-06-16', the row will strictly contain the features from '2026-06-15'.
        """
        df = self.get_flow_features(start_date, end_date)
        if not df.empty:
            # Shift all columns by 1 to align T-1 features with T's index
            df = df.shift(1)
            # Drop the first row since it will now be NaN
            df = df.dropna(how='all')
            
        return df

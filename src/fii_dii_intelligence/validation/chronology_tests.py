import pandas as pd
import logging

logger = logging.getLogger(__name__)

def validate_feature_chronology(df: pd.DataFrame, target_prediction_date: str) -> bool:
    """
    STRICT CHRONOLOGY ENFORCEMENT.
    Guarantees that no FII/DII features from `target_prediction_date` (T) 
    are allowed to exist when predicting `target_prediction_date`.
    Only features up to T-1 are allowed.
    """
    
    if df.empty:
        return True
        
    # Check if target_prediction_date is in the feature index
    target_date = pd.to_datetime(target_prediction_date)
    
    # Get the latest date present in the feature store DataFrame
    latest_feature_date = df.index.max()
    
    if latest_feature_date >= target_date:
        logger.error(f"CHRONOLOGY VIOLATION! The feature store contains data for {latest_feature_date}, "
                     f"but the target prediction date is {target_date}. "
                     f"This leaks post-close flow data into a same-day prediction model.")
        return False
        
    logger.info("Chronology validation passed: No same-day lookahead bias detected.")
    return True

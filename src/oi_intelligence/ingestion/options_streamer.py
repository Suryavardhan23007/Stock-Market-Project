import os
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

import pyotp
from py5paisa import FivePaisaClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FivePaisaAuthManager:
    """
    Handles authentication using TOTP for newer versions of py5paisa.
    """
    def __init__(self):
        load_dotenv()
        self.app_name = os.getenv("FIVEPAISA_APP_NAME")
        self.app_source = os.getenv("FIVEPAISA_APP_SOURCE")
        self.user_id = os.getenv("FIVEPAISA_USER_ID")
        self.password = os.getenv("FIVEPAISA_PASSWORD")
        self.user_key = os.getenv("FIVEPAISA_USER_KEY")
        self.encryption_key = os.getenv("FIVEPAISA_ENCRYPTION_KEY")
        
        # New auth requirements
        self.client_code = os.getenv("FIVEPAISA_CLIENT_CODE")
        self.totp_secret = os.getenv("FIVEPAISA_TOTP_SECRET")
        self.mpin = os.getenv("FIVEPAISA_MPIN")

    def authenticate(self):
        """
        Authenticates and returns the Py5Paisa Client.
        """
        cred = {
            "APP_NAME": self.app_name,
            "APP_SOURCE": self.app_source,
            "USER_ID": self.user_id,
            "PASSWORD": self.password,
            "USER_KEY": self.user_key,
            "ENCRYPTION_KEY": self.encryption_key
        }

        try:
            client = FivePaisaClient(cred=cred)
            
            # Use TOTP flow instead of old email/dob flow
            if self.totp_secret:
                totp = pyotp.TOTP(self.totp_secret)
                pin = totp.now()
                # Newer py5paisa uses get_totp_session
                client.get_totp_session(self.client_code, pin, self.mpin)
                logger.info("Successfully authenticated with 5paisa via TOTP.")
                return client
            else:
                logger.error("FIVEPAISA_TOTP_SECRET not found in .env")
                return None
                
        except Exception as e:
            logger.error(f"Failed to authenticate with 5paisa: {str(e)}")
            return None

import urllib.request
import pandas as pd
from datetime import datetime, timedelta

import urllib.request
import pandas as pd
from datetime import datetime, timedelta, timezone
from src.database.connection import SessionLocal
from src.database.models import OptionsRawChain, SymbolConfig, DataQualityLog
from src.oi_intelligence.validation.snapshot_integrity_engine import SnapshotIntegrityEngine
from src.oi_intelligence.analytics.concentration_engine import ConcentrationEngine
from src.oi_intelligence.analytics.velocity_engine import VelocityEngine
from src.oi_intelligence.analytics.statistics_engine import StatisticsEngine
from src.oi_intelligence.analytics.context_engine import ContextEngine
from src.oi_intelligence.analytics.regime_engine import RegimeEngine
from src.oi_intelligence.analytics.writing_engine import WritingEngine
from src.oi_intelligence.analytics.atm_flow_engine import AtmFlowEngine
from src.oi_intelligence.analytics.gamma_engine import GammaEngine

class OptionsStreamer:
    """
    Live streaming daemon that captures Options Data from 5paisa.
    """
    def __init__(self, client):
        self.client = client
        self.subscriptions = []
        self.scrip_master = None
        self.last_snapshot_time = None
        
        # Load Configs from DB
        self.db_session = SessionLocal()
        self.config_cache = self._load_configs()
        self.integrity_engine = SnapshotIntegrityEngine(self.db_session, self.config_cache.get("NIFTY", {}))
        self.concentration_engine = ConcentrationEngine(self.db_session, self.config_cache.get("NIFTY", {}))
        self.velocity_engine = VelocityEngine(self.db_session)
        self.statistics_engine = StatisticsEngine(self.db_session, self.config_cache.get("NIFTY", {}))
        self.context_engine = ContextEngine(self.db_session)
        self.regime_engine = RegimeEngine(self.db_session)
        self.writing_engine = WritingEngine(self.db_session)
        self.atm_flow_engine = AtmFlowEngine(self.db_session)
        self.gamma_engine = GammaEngine(self.db_session)
        from src.oi_intelligence.analytics.breadth_engine import BreadthEngine
        self.breadth_engine = BreadthEngine(self.db_session)
        # ScripMaster fetching has been deprecated and removed.

    def _load_configs(self):
        configs = self.db_session.query(SymbolConfig).all()
        return {c.symbol: {
            'atm_zone_width': c.atm_zone_width,
            'liquidity_threshold': c.liquidity_threshold,
            'wall_significance_threshold': c.wall_significance_threshold,
            'coverage_threshold': c.coverage_threshold
        } for c in configs}
    
    def parse_option_chain_payload(self, options_list, expiry_date):
        if not options_list or not isinstance(options_list, list):
            return pd.DataFrame()
            
        rows = []
        for opt in options_list:
            def safe_float(val):
                try: return float(val) if val is not None else 0.0
                except: return 0.0
            def safe_int(val):
                try: return int(val) if val is not None else 0
                except: return 0
                
            if opt.get('CPType') == 'CE':
                call_oi = safe_int(opt.get('OpenInterest', 0))
                put_oi = 0
                call_vol = safe_int(opt.get('Volume', 0))
                put_vol = 0
                ce_premium = safe_float(opt.get('LastRate', 0))
                pe_premium = 0.0
                ce_prev_close = safe_float(opt.get('PreviousClose', 0))
                pe_prev_close = 0.0
                ce_chg_oi = safe_int(opt.get('ChangeInOI', 0))
                pe_chg_oi = 0
                ce_scrip = safe_int(opt.get('ScripCode', 0))
                pe_scrip = 0
            else:
                call_oi = 0
                put_oi = safe_int(opt.get('OpenInterest', 0))
                call_vol = 0
                put_vol = safe_int(opt.get('Volume', 0))
                ce_premium = 0.0
                pe_premium = safe_float(opt.get('LastRate', 0))
                ce_prev_close = 0.0
                pe_prev_close = safe_float(opt.get('PreviousClose', 0))
                ce_chg_oi = 0
                pe_chg_oi = safe_int(opt.get('ChangeInOI', 0))
                ce_scrip = 0
                pe_scrip = safe_int(opt.get('ScripCode', 0))

            bid = 0.0
            ask = 0.0
            
            rows.append({
                'strike_price': safe_float(opt.get('StrikeRate', opt.get('StrikePrice', 0))),
                'call_oi': call_oi,
                'put_oi': put_oi,
                'call_vol': call_vol,
                'put_vol': put_vol,
                'ce_premium': ce_premium,
                'pe_premium': pe_premium,
                'ce_previous_close': ce_prev_close,
                'pe_previous_close': pe_prev_close,
                'ce_change_in_oi': ce_chg_oi,
                'pe_change_in_oi': pe_chg_oi,
                'ce_scrip_code': ce_scrip,
                'pe_scrip_code': pe_scrip,
                'bid': bid,
                'ask': ask,
                'spread': ask - bid if ask > bid else 0.0,
                'expiry_date': expiry_date
            })
            
        df_raw = pd.DataFrame(rows)
        if df_raw.empty:
            return df_raw
            
        df_merged = df_raw.groupby('strike_price').agg({
            'call_oi': 'sum',
            'put_oi': 'sum',
            'call_vol': 'sum',
            'put_vol': 'sum',
            'ce_premium': 'max',
            'pe_premium': 'max',
            'ce_previous_close': 'max',
            'pe_previous_close': 'max',
            'ce_change_in_oi': 'max',
            'pe_change_in_oi': 'max',
            'ce_scrip_code': 'max',
            'pe_scrip_code': 'max',
            'bid': 'max',
            'ask': 'max',
            'spread': 'max',
            'expiry_date': 'first'
        }).reset_index()
        
        df_merged['premium'] = df_merged[['ce_premium', 'pe_premium']].max(axis=1)
        
        return df_merged

    def process_snapshot(self, symbol, spot_price, payload_list, timestamp, expiry_date):
        """
        Main processing loop triggered per snapshot.
        """
        self.integrity_engine.config = self.config_cache.get(symbol, {})
        
        df = self.parse_option_chain_payload(payload_list, expiry_date)
        
        # 1. Integrity Check
        integrity_record = self.integrity_engine.validate_snapshot(
            df=df,
            timestamp=timestamp,
            symbol=symbol,
            underlying_spot_price=spot_price,
            last_snapshot_time=self.last_snapshot_time
        )
        
        self.last_snapshot_time = timestamp
        
        # Phase Gate: Stop if unhealthy
        if integrity_record.data_health_status != "HEALTHY":
            logger.warning(f"Snapshot rejected: {integrity_record.data_health_status}")
            self.db_session.add(DataQualityLog(
                timestamp=timestamp, event_type=integrity_record.data_health_status,
                description=f"Snapshot aborted due to {integrity_record.data_health_status}",
                severity="WARNING"
            ))
            self.db_session.commit()
            return
            
        # 2. Archival of Raw Chain
        ingestion_ts = datetime.now(timezone.utc)
        records = []
        for _, row in df.iterrows():
            records.append(OptionsRawChain(
                timestamp=timestamp,
                symbol=symbol,
                collection_version="v1.0",
                calculation_version="v1.0",
                ingestion_timestamp=ingestion_ts,
                source_name="5paisa_xstream",
                expiry_date=row['expiry_date'],
                strike_price=row['strike_price'],
                call_oi=row['call_oi'],
                put_oi=row['put_oi'],
                call_vol=row['call_vol'],
                put_vol=row['put_vol'],
                ce_premium=row['ce_premium'],
                pe_premium=row['pe_premium'],
                ce_previous_close=row['ce_previous_close'],
                pe_previous_close=row['pe_previous_close'],
                ce_change_in_oi=row['ce_change_in_oi'],
                pe_change_in_oi=row['pe_change_in_oi'],
                ce_scrip_code=row['ce_scrip_code'],
                pe_scrip_code=row['pe_scrip_code'],
                bid=row['bid'],
                ask=row['ask'],
                spread=row['spread'],
                premium=row['premium']
            ))
        
        self.db_session.bulk_save_objects(records)
        self.db_session.commit()
        logger.info(f"Archived {len(records)} strikes for {symbol} at {timestamp}")
        # 3. Trigger downstream ML calculations (Phase 3/4/5)
        self.concentration_engine.config = self.config_cache.get(symbol, {})
        self.statistics_engine.config = self.config_cache.get(symbol, {})
        
        concentration_record = self.concentration_engine.process(df, timestamp, symbol, spot_price)
        velocity_record = self.velocity_engine.process(df, timestamp, symbol)
        stat_record = self.statistics_engine.process(df, timestamp, symbol, spot_price, expiry_date)
        
        pcr = stat_record.pcr if stat_record else None
        iv = stat_record.iv if stat_record else None
        vix = stat_record.vix if stat_record else None
        vel = velocity_record.oi_velocity if velocity_record else None
        
        context_record = self.context_engine.process(timestamp, symbol, pcr, iv, vix, vel)
        
        # Get latest breadth if available
        from src.database.models import MarketBreadthLive
        breadth_record = self.db_session.query(MarketBreadthLive).filter_by(symbol=symbol).order_by(MarketBreadthLive.id.desc()).first()
        
        regime_record = self.regime_engine.process(timestamp, symbol, context_record, concentration_record, breadth_record)
        if regime_record:
            logger.info(f"--- TRACE: Regime --- \nRaw Regime: {regime_record.current_regime}")

        # New Institutional Features
        writing_record = self.writing_engine.process(df, timestamp, symbol)
        atm_flow_record = self.atm_flow_engine.process(df, timestamp, symbol, spot_price)
        gamma_record = self.gamma_engine.process(df, timestamp, symbol, spot_price, expiry_date)
        
        if gamma_record:
            logger.info(f"--- TRACE: Gamma --- \nRegime: {gamma_record.gamma_regime} | Net GEX: {gamma_record.net_gex}")

    def fetch_and_process_breadth(self, timestamp: datetime):
        if not self.breadth_engine.constituents.empty:
            req_list = []
            for _, row in self.breadth_engine.constituents.iterrows():
                req_list.append({"Exch": "N", "ExchType": "C", "Symbol": row['symbol']})
            if req_list:
                try:
                    all_feed_data = []
                    # py5paisa has a 50 scrip limit per MarketFeed request
                    chunk_size = 50
                    for i in range(0, len(req_list), chunk_size):
                        chunk = req_list[i:i + chunk_size]
                        feed_data = self.client.fetch_market_feed(chunk)
                        if feed_data:
                            if isinstance(feed_data, dict) and 'Data' in feed_data:
                                all_feed_data.extend(feed_data['Data'])
                            elif isinstance(feed_data, list):
                                all_feed_data.extend(feed_data)
                                
                    # Process independently
                    for idx_sym in ["NIFTY", "BANKNIFTY"]:
                        record = self.breadth_engine.process(idx_sym, all_feed_data, timestamp)
                        if record:
                            logger.info(f"--- TRACE: Breadth ({idx_sym}) --- \nAdv: {record.advancing_count}, Dec: {record.declining_count}, Unc: {record.unchanged_count}, WgtBr: {record.weighted_breadth}")
                except Exception as e:
                    logger.error(f"Failed to fetch market feed for breadth: {e}")

    def start_streaming(self, symbols=None, n_strikes=20):
        if symbols is None:
            symbols = ["NIFTY", "BANKNIFTY"]
            
        # Initial health
        self.integrity_engine.update_system_health("CONNECTED", "CONNECTING", self.last_snapshot_time)
        
        try:
            timestamp = datetime.now(timezone.utc)
            
            for symbol in symbols:
                # 1. Fetch Expiry and Spot using V2 API
                expiries = self.client.get_expiry("N", symbol)
                if not expiries or 'lastrate' not in expiries:
                    logger.error(f"Failed to fetch Spot Price/Expiries for {symbol}")
                    self.integrity_engine.update_system_health("API_FAILURE", "DISCONNECTED", self.last_snapshot_time)
                    continue
                    
                spot_price = expiries['lastrate'][0]['LTP']
                logger.info(f"Current {symbol} Spot: {spot_price}")
                
                if 'Expiry' not in expiries or len(expiries['Expiry']) == 0:
                    logger.error(f"No expiries found for {symbol}")
                    self.integrity_engine.update_system_health("API_FAILURE", "DISCONNECTED", self.last_snapshot_time)
                    continue
                    
                first_expiry_str = expiries['Expiry'][0]['ExpiryDate']
                import re
                match = re.search(r'\d+', first_expiry_str)
                if not match:
                    logger.error("Failed to parse expiry timestamp")
                    continue
                    
                timestamp_ms = int(match.group())
                # Convert to aware datetime for DB
                nearest_expiry = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
                
                # 2. Fetch full option chain directly
                logger.info(f"Fetching Option Chain for {symbol} at expiry {nearest_expiry}")
                chain = self.client.get_option_chain("N", symbol, timestamp_ms)
                
                self.integrity_engine.update_system_health("HEALTHY", "CONNECTED", self.last_snapshot_time)
                
                if chain and 'Options' in chain:
                    options_list = chain['Options']
                    
                    # Filter to n_strikes around ATM
                    step = 50 if symbol == 'NIFTY' else 100
                    atm_strike = round(spot_price / step) * step
                    valid_strikes = set([atm_strike + (i * step) for i in range(-n_strikes, n_strikes + 1)])
                    
                    filtered_options = [opt for opt in options_list if opt.get('StrikeRate') in valid_strikes]
                    
                    # 3. Process Snapshot (pass the EXACT same timestamp for both symbols so they align natively!)
                    self.process_snapshot(symbol, spot_price, filtered_options, timestamp, nearest_expiry)
                    
                    # 6. Fetch and process breadth
                    self.fetch_and_process_breadth(timestamp)
                else:
                    logger.warning(f"Empty chain received from broker for {symbol}.")
                
        except Exception as e:
            logger.error(f"Stream failure: {e}")
            self.integrity_engine.update_system_health("EXCEPTION", "ERROR", self.last_snapshot_time)

if __name__ == "__main__":
    auth = FivePaisaAuthManager()
    client = auth.authenticate()
    if client:
        streamer = OptionsStreamer(client)
        streamer.start_streaming(symbols=["NIFTY", "BANKNIFTY"], n_strikes=10)

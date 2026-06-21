from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index, UniqueConstraint
from sqlalchemy.sql import func
from src.database.connection import Base

class MarketCandle(Base):
    """
    Stores 1-minute OHLCV candles for indices (Sensex, Bank Nifty)
    and any individual stocks/instruments.
    """
    __tablename__ = "market_candles"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False, default=0.0)

    # Composite index and unique constraint
    __table_args__ = (
        UniqueConstraint('symbol', 'timestamp', name='uq_symbol_timestamp'),
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )

class NewsArticle(Base):
    """
    Stores raw ingested financial news and global news articles.
    """
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    article = Column(Text, nullable=True)
    url = Column(String, nullable=True, unique=True)
    category = Column(String, nullable=True)  # Banking, Corporate, General
    related_entities = Column(Text, nullable=True) # JSON list or string of entities
    
    # Metadata fields
    event_type = Column(String, nullable=True)
    country = Column(String, nullable=True, default="India")
    sector = Column(String, nullable=True)
    
    # Ingestion status flags
    processed = Column(Boolean, nullable=False, default=False)
    sentiment_label = Column(String, nullable=True)
    sentiment_score = Column(Float, nullable=True)

class PaperTrade(Base):
    """
    Ledger for recording mock paper trades to validate model predictions
    and performance.
    """
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False)      # BUY or SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True, default=0.0)  # Calculated profit/loss
    status = Column(String, nullable=False, default="COMPLETED") # COMPLETED, FILLED

class MacroIndicator(Base):
    """
    Stores historical macroeconomic and global market indicators
    (RBI Repo rate, US Fed rate, CPI, Brent Crude, Gold, DXY, VIX, S&P 500).
    """
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    key = Column(String, nullable=False, index=True) # e.g. "INDIA_REPO_RATE", "INDIA_CPI", "US_FED_RATE", "OIL_BRENT", "GOLD_USD", "DXY", "SP500", "INDIA_VIX"
    value = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint('timestamp', 'key', name='uq_timestamp_key'),
    )

class StructuredEvent(Base):
    """
    Structured events database converted from raw news articles.
    """
    __tablename__ = "structured_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)  # RATE_HIKE, RATE_CUT, GDP_RELEASE, etc.
    country = Column(String, nullable=False, index=True)
    sector = Column(String, nullable=True, index=True)
    magnitude = Column(Float, nullable=True)
    entities_involved = Column(Text, nullable=True)
    entities = Column(Text, nullable=True)
    source = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Market reaction labels (Returns over multiple horizons for Sensex, Nifty 50, and Bank Nifty)
    banknifty_return_1m = Column(Float, nullable=True)
    banknifty_return_5m = Column(Float, nullable=True)
    banknifty_return_15m = Column(Float, nullable=True)
    banknifty_return_30m = Column(Float, nullable=True)
    banknifty_return_1h = Column(Float, nullable=True)
    banknifty_return_1d = Column(Float, nullable=True)

    nifty_return_1m = Column(Float, nullable=True)
    nifty_return_5m = Column(Float, nullable=True)
    nifty_return_15m = Column(Float, nullable=True)
    nifty_return_30m = Column(Float, nullable=True)
    nifty_return_1h = Column(Float, nullable=True)
    nifty_return_1d = Column(Float, nullable=True)

    sensex_return_1m = Column(Float, nullable=True)
    sensex_return_5m = Column(Float, nullable=True)
    sensex_return_15m = Column(Float, nullable=True)
    sensex_return_30m = Column(Float, nullable=True)
    sensex_return_1h = Column(Float, nullable=True)
    sensex_return_1d = Column(Float, nullable=True)

class EconomicCalendarData(Base):
    """
    Economic calendar database events for India and global entities.
    """
    __tablename__ = "economic_calendar"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String, nullable=False, index=True)
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    country = Column(String, nullable=False, index=True)
    
    # Backwards compatible columns
    forecast_value = Column(String, nullable=True)
    actual_value = Column(String, nullable=True)
    previous_value = Column(String, nullable=True)
    importance_level = Column(String, nullable=True, index=True)

    # Redesigned calendar columns
    event_type = Column(String, nullable=True, index=True)
    forecast = Column(String, nullable=True)
    actual = Column(String, nullable=True)
    previous = Column(String, nullable=True)
    importance = Column(String, nullable=True, index=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)


class CorporateAnnouncement(Base):
    """
    Corporate filings collected directly from exchanges.
    """
    __tablename__ = "corporate_announcements"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)  # EARNINGS, DIVIDEND, BUYBACK, etc.
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    filing_date = Column(DateTime(timezone=True), nullable=False, index=True)
    exchange_source = Column(String, nullable=False) # NSE, BSE
    description = Column(Text, nullable=True)

class RegulatoryEvent(Base):
    """
    Exchange and regulatory circulars.
    """
    __tablename__ = "regulatory_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    circular_number = Column(String, nullable=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=False, index=True) # RBI, SEBI, NSE, BSE
    affected_sector = Column(String, nullable=True, index=True)
    related_entities = Column(Text, nullable=True)

class CommodityEvent(Base):
    """
    Events related to Brent Crude, Gold, Natural Gas.
    """
    __tablename__ = "commodity_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    commodity_name = Column(String, nullable=False, index=True) # Crude Oil, Gold, Natural Gas
    event_type = Column(String, nullable=False, index=True)
    headline = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=False)
    potential_impact = Column(String, nullable=True)

class GeopoliticalEvent(Base):
    """
    Geopolitical developments (wars, elections, trade wars).
    """
    __tablename__ = "geopolitical_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)  # WAR, SANCTION, ELECTION, etc.
    countries_involved = Column(String, nullable=False, index=True)
    event_start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    event_severity = Column(String, nullable=False, index=True) # HIGH, MEDIUM, LOW
    related_commodities = Column(String, nullable=True)
    potential_market_impact = Column(String, nullable=True)
    description = Column(Text, nullable=True)

class CurrencyEvent(Base):
    """
    Currency pairs movements and related news.
    """
    __tablename__ = "currency_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    currency_pair = Column(String, nullable=False, index=True) # USD/INR, DXY
    headline = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=False)
    value_impact = Column(String, nullable=True)

class CentralBankEvent(Base):
    """
    Central bank notifications and monetary reports.
    """
    __tablename__ = "central_bank_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    central_bank = Column(String, nullable=False, index=True) # RBI, Federal Reserve, ECB, BoE, BoJ
    event_type = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=False)
    policy_action = Column(String, nullable=True)

class InstitutionalFlow(Base):
    """
    Institutional investment flows (FII and DII activity) from NSDL/CDSL.
    """
    __tablename__ = "institutional_flows"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    fii_net_buy = Column(Float, nullable=True)
    fii_net_sell = Column(Float, nullable=True)
    dii_net_buy = Column(Float, nullable=True)
    dii_net_sell = Column(Float, nullable=True)
    category = Column(String, nullable=False, index=True) # e.g. EQUITY, DEBT, HYBRID
    source = Column(String, nullable=False, index=True)  # NSDL, CDSL

class AMFIData(Base):
    """
    Mutual fund flows and industry AUM metrics from AMFI.
    """
    __tablename__ = "amfi_flows"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(DateTime(timezone=True), nullable=False, index=True)
    category = Column(String, nullable=False, index=True) # e.g. EQUITY_ELSS, INCOME_DEBT
    net_inflow = Column(Float, nullable=True)
    aum = Column(Float, nullable=True)
    source = Column(String, nullable=False, default="AMFI")

class BankingRelations(Base):
    """
    Investor relations filings, transcripts, and financial stability reports for target banks.
    """
    __tablename__ = "banking_relations"

    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String, nullable=False, index=True) # SBI, HDFC Bank, ICICI Bank, Axis Bank, Kotak Mahindra Bank, IndusInd Bank, RBI
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True) # EARNINGS_TRANSCRIPT, RBI_FSR, RBI_ANNUAL
    content = Column(Text, nullable=True)
    url = Column(String, nullable=True)

class OptionsIntelligence(Base):
    """
    Options intelligence indicators (IV, OI, PCR, Max Pain) for Nifty 50 and Bank Nifty.
    """
    __tablename__ = "options_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True) # NIFTY, BANKNIFTY
    implied_volatility = Column(Float, nullable=True)
    open_interest = Column(Float, nullable=True)
    change_in_oi = Column(Float, nullable=True)
    pcr = Column(Float, nullable=True)
    max_pain = Column(Float, nullable=True)
    india_vix = Column(Float, nullable=True)
    spot_close = Column(Float, nullable=True)


from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import BigInteger, PrimaryKeyConstraint

class SymbolConfig(Base):
    __tablename__ = "symbol_config"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, unique=True, index=True)
    atm_zone_width = Column(Float, nullable=False)
    liquidity_threshold = Column(Float, nullable=False)
    wall_significance_threshold = Column(Float, nullable=False)
    coverage_threshold = Column(Float, nullable=False)

class OptionsRawChain(Base):
    __tablename__ = "options_raw_chain"
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
        {'postgresql_partition_by': 'RANGE (timestamp)'}
    )
    id = Column(Integer, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    collection_version = Column(String, nullable=False)
    calculation_version = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), nullable=False)
    source_name = Column(String, nullable=False)
    
    expiry_date = Column(DateTime(timezone=True), nullable=False, index=True)
    strike_price = Column(Float, nullable=False, index=True)
    call_oi = Column(BigInteger, nullable=True)
    put_oi = Column(BigInteger, nullable=True)
    call_vol = Column(BigInteger, nullable=True)
    put_vol = Column(BigInteger, nullable=True)
    
    # Restored Raw Broker Fields
    ce_premium = Column(Float, nullable=True)
    pe_premium = Column(Float, nullable=True)
    ce_previous_close = Column(Float, nullable=True)
    pe_previous_close = Column(Float, nullable=True)
    ce_change_in_oi = Column(BigInteger, nullable=True)
    pe_change_in_oi = Column(BigInteger, nullable=True)
    ce_scrip_code = Column(BigInteger, nullable=True)
    pe_scrip_code = Column(BigInteger, nullable=True)

    bid = Column(Float, nullable=True)
    ask = Column(Float, nullable=True)
    spread = Column(Float, nullable=True)
    premium = Column(Float, nullable=True)
    
    # Greeks (NULL placeholders for Phase B)
    delta = Column(Float, nullable=True)
    gamma = Column(Float, nullable=True)
    theta = Column(Float, nullable=True)
    vega = Column(Float, nullable=True)

class SystemHealthLive(Base):
    __tablename__ = "system_health_live"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    api_status = Column(String, nullable=False)
    db_status = Column(String, nullable=False)
    partition_status = Column(String, nullable=False)
    websocket_status = Column(String, nullable=False)
    last_snapshot_time = Column(DateTime(timezone=True), nullable=True)

class SnapshotIntegrityLive(Base):
    __tablename__ = "snapshot_integrity_live"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    collection_version = Column(String, nullable=False)
    calculation_version = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), nullable=False)
    source_name = Column(String, nullable=False)
    
    strikes_expected = Column(Integer, nullable=True)
    strikes_received = Column(Integer, nullable=True)
    chain_coverage_pct = Column(Float, nullable=True)
    total_call_oi = Column(BigInteger, nullable=True)
    total_put_oi = Column(BigInteger, nullable=True)
    total_call_volume = Column(BigInteger, nullable=True)
    total_put_volume = Column(BigInteger, nullable=True)
    
    session_state = Column(String, nullable=False) # PRE_MARKET, MARKET_OPEN, MARKET_CLOSED, POST_MARKET, HOLIDAY
    data_health_status = Column(String, nullable=False)
    data_age_seconds = Column(Integer, nullable=True)
    
    underlying_spot_price = Column(Float, nullable=True)
    atm_zone_low = Column(Float, nullable=True)
    atm_zone_high = Column(Float, nullable=True)

class OptionsVelocityLive(Base):
    __tablename__ = "options_velocity_live"
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
        {'postgresql_partition_by': 'RANGE (timestamp)'}
    )
    id = Column(Integer, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    collection_version = Column(String, nullable=False)
    calculation_version = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), nullable=False)
    source_name = Column(String, nullable=False)
    
    oi_velocity = Column(Float, nullable=True)
    oi_acceleration = Column(Float, nullable=True)
    oi_velocity_zscore = Column(Float, nullable=True)
    oi_acceleration_zscore = Column(Float, nullable=True)

class MarketBreadthLive(Base):
    __tablename__ = "market_breadth_live"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    collection_version = Column(String, nullable=False)
    calculation_version = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), nullable=False)
    source_name = Column(String, nullable=False)
    
    advancing_count = Column(Integer, nullable=True)
    declining_count = Column(Integer, nullable=True)
    unchanged_count = Column(Integer, nullable=True)
    equal_weight_breadth = Column(Float, nullable=True)
    weighted_breadth = Column(Float, nullable=True)

class OptionsConcentrationLive(Base):
    __tablename__ = "options_concentration_live"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    collection_version = Column(String, nullable=False)
    calculation_version = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), nullable=False)
    source_name = Column(String, nullable=False)
    
    call_wall_strike = Column(Float, nullable=True)
    put_wall_strike = Column(Float, nullable=True)
    call_wall_pct = Column(Float, nullable=True)
    put_wall_pct = Column(Float, nullable=True)
    
    previous_call_wall = Column(Float, nullable=True)
    previous_put_wall = Column(Float, nullable=True)
    call_wall_shift = Column(Float, nullable=True)
    put_wall_shift = Column(Float, nullable=True)
    
    distance_to_call_wall = Column(Float, nullable=True)
    distance_to_put_wall = Column(Float, nullable=True)
    call_wall_duration_minutes = Column(Integer, nullable=True)
    put_wall_duration_minutes = Column(Integer, nullable=True)

class MarketRegimeLive(Base):
    __tablename__ = "market_regime_live"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    collection_version = Column(String, nullable=False)
    calculation_version = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), nullable=False)
    source_name = Column(String, nullable=False)
    
    previous_regime = Column(String, nullable=True)
    current_regime = Column(String, nullable=True)
    transition_timestamp = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    stability_score = Column(Float, nullable=True)

class OptionsStatisticsLive(Base):
    __tablename__ = "options_statistics_live"
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
        {'postgresql_partition_by': 'RANGE (timestamp)'}
    )
    id = Column(Integer, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    collection_version = Column(String, nullable=False)
    calculation_version = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), nullable=False)
    source_name = Column(String, nullable=False)
    
    underlying_spot_price = Column(Float, nullable=True)
    atm_zone_low = Column(Float, nullable=True)
    atm_zone_high = Column(Float, nullable=True)
    days_to_expiry = Column(Integer, nullable=True)
    expiry_type = Column(String, nullable=True) # WEEKLY, MONTHLY
    
    total_call_oi = Column(BigInteger, nullable=True)
    total_put_oi = Column(BigInteger, nullable=True)
    pcr = Column(Float, nullable=True)
    iv = Column(Float, nullable=True)
    vix = Column(Float, nullable=True)
    warmup_status = Column(String, nullable=False) # COLD_START, PARTIAL_HISTORY, READY

class OptionsContextLive(Base):
    __tablename__ = "options_context_live"
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
        {'postgresql_partition_by': 'RANGE (timestamp)'}
    )
    id = Column(Integer, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    collection_version = Column(String, nullable=False)
    calculation_version = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), nullable=False)
    source_name = Column(String, nullable=False)
    
    underlying_spot_price = Column(Float, nullable=True)
    atm_zone_low = Column(Float, nullable=True)
    atm_zone_high = Column(Float, nullable=True)
    market_open_timestamp = Column(DateTime(timezone=True), nullable=True)
    market_close_timestamp = Column(DateTime(timezone=True), nullable=True)
    minutes_since_open = Column(Integer, nullable=True)
    minutes_until_close = Column(Integer, nullable=True)
    
    pcr_percentile = Column(Float, nullable=True)
    pcr_zscore = Column(Float, nullable=True)
    oi_velocity_percentile = Column(Float, nullable=True)
    oi_acceleration_percentile = Column(Float, nullable=True)
    iv_percentile = Column(Float, nullable=True)
    vix_percentile = Column(Float, nullable=True)
    breadth_percentile = Column(Float, nullable=True)
    regime_stability_percentile = Column(Float, nullable=True)

class DataQualityLog(Base):
    __tablename__ = "data_quality_log"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True) # MISSING_SNAPSHOT, DISCONNECT, API_FAILURE, STALE_FEED, INSUFFICIENT_DATA, LOW_CHAIN_COVERAGE, OI_STALENESS_WARNING
    description = Column(Text, nullable=True)
    severity = Column(String, nullable=False, default="INFO")

class OptionsWritingLive(Base):
    __tablename__ = "options_writing_live"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    
    long_buildup_score = Column(Float, nullable=True)
    short_buildup_score = Column(Float, nullable=True)
    short_covering_score = Column(Float, nullable=True)
    long_unwinding_score = Column(Float, nullable=True)

class OptionsAtmFlowLive(Base):
    __tablename__ = "options_atm_flow_live"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    
    atm_oi_velocity = Column(Float, nullable=True)
    atm_oi_acceleration = Column(Float, nullable=True)
    atm_volume_velocity = Column(Float, nullable=True)
    atm_writing_pressure = Column(Float, nullable=True)
    atm_flow_score = Column(Float, nullable=True)

class OptionsGammaLive(Base):
    __tablename__ = "options_gamma_live"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    
    total_call_gex = Column(Float, nullable=True)
    total_put_gex = Column(Float, nullable=True)
    net_gex = Column(Float, nullable=True)
    gamma_regime = Column(String, nullable=True)

class CollectionHealth(Base):
    """
    Tracks collection performance and gap detection.
    """
    __tablename__ = "collection_health"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False, index=True) # YYYY-MM-DD format
    expected_snapshots = Column(Integer, nullable=False, default=0)
    received_snapshots = Column(Integer, nullable=False, default=0)
    missing_snapshots = Column(Integer, nullable=False, default=0)
    last_successful_collection = Column(DateTime(timezone=True), nullable=True)
    reconnect_count = Column(Integer, nullable=False, default=0)
    auth_refresh_count = Column(Integer, nullable=False, default=0)
    db_reconnect_count = Column(Integer, nullable=False, default=0)

class FIIDIIRawArchive(Base):
    """
    Preserves raw institutional flow data exactly as reported by the exchange before any feature engineering.
    """
    __tablename__ = "fii_dii_raw_archive"

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)
    
    fii_buy = Column(Float, nullable=False, default=0.0)
    fii_sell = Column(Float, nullable=False, default=0.0)
    fii_net = Column(Float, nullable=False, default=0.0)
    
    dii_buy = Column(Float, nullable=False, default=0.0)
    dii_sell = Column(Float, nullable=False, default=0.0)
    dii_net = Column(Float, nullable=False, default=0.0)
    
    source = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), default=func.now())

class InstitutionalFlowIntelligence(Base):
    """
    Structured institutional participation intelligence including all divergence, rolling, participation, and streak features.
    """
    __tablename__ = "institutional_flow_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)
    
    # 1. Raw Flow Features
    fii_buy = Column(Float, nullable=False, default=0.0)
    fii_sell = Column(Float, nullable=False, default=0.0)
    fii_net = Column(Float, nullable=False, default=0.0)
    dii_buy = Column(Float, nullable=False, default=0.0)
    dii_sell = Column(Float, nullable=False, default=0.0)
    dii_net = Column(Float, nullable=False, default=0.0)

    # 2. Divergence Features
    fii_dii_divergence = Column(Float, nullable=True) # fii_net - dii_net

    # 3. Rolling Flow Features
    fii_3d_flow = Column(Float, nullable=True)
    fii_5d_flow = Column(Float, nullable=True)
    fii_10d_flow = Column(Float, nullable=True)
    fii_20d_flow = Column(Float, nullable=True)
    dii_3d_flow = Column(Float, nullable=True)
    dii_5d_flow = Column(Float, nullable=True)
    dii_10d_flow = Column(Float, nullable=True)
    dii_20d_flow = Column(Float, nullable=True)

    # 4. Participation Features
    total_institutional_flow = Column(Float, nullable=True) # abs(fii_net) + abs(dii_net)
    fii_flow_share = Column(Float, nullable=True) # abs(fii_net) / total_institutional_flow
    dii_flow_share = Column(Float, nullable=True) # abs(dii_net) / total_institutional_flow

    # 5. Streak Features
    fii_buy_streak = Column(Integer, default=0)
    fii_sell_streak = Column(Integer, default=0)
    dii_buy_streak = Column(Integer, default=0)
    dii_sell_streak = Column(Integer, default=0)

    source = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime(timezone=True), default=func.now())

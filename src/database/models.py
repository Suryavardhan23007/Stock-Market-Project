from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index, UniqueConstraint
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




import json
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal, init_db
from src.database.models import (
    NewsArticle, EconomicCalendarData, CorporateAnnouncement,
    RegulatoryEvent, StructuredEvent, CentralBankEvent,
    GeopoliticalEvent, BankingRelations
)

def extract_structured_events():
    """
    Connects to the database and converts raw news, calendar releases,
    corporate filings, and regulatory events into the StructuredEvent schema.
    """
    db: Session = SessionLocal()
    print("[INFO] Running Structured Event Extractor...")
    
    stored = 0
    
    # 1. Convert News Articles (major geopolitics and macro headlines)
    print("Processing NewsArticles -> StructuredEvents...")
    news_items = db.query(NewsArticle).all()
    for item in news_items:
        # Determine target structured event type
        ev_type = "general"
        headline_lower = item.headline.lower()
        
        if "repo rate cut" in headline_lower or "slashes interest rates" in headline_lower or "fed cuts rates" in headline_lower:
            ev_type = "RATE_CUT"
        elif "mpc raises policy repo rate" in headline_lower or "hikes interest rates" in headline_lower:
            ev_type = "RATE_HIKE"
        elif "inflation" in headline_lower or "cpi" in headline_lower:
            ev_type = "INFLATION_RELEASE"
        elif "gdp" in headline_lower:
            ev_type = "GDP_RELEASE"
        elif "invades" in headline_lower or "conflict" in headline_lower:
            ev_type = "WAR"
        elif "sanctions" in headline_lower:
            ev_type = "SANCTION"
        elif "trade war" in headline_lower or "trade disputes" in headline_lower:
            ev_type = "TRADE_WAR"
        elif "election" in headline_lower:
            ev_type = "ELECTION"
        elif "crude oil" in headline_lower or "oil supply" in headline_lower:
            ev_type = "OIL_SHOCK"
        elif "peak margin" in headline_lower or "front margin" in headline_lower:
            ev_type = "REGULATORY_CHANGE"
        elif "stimulus" in headline_lower or "tax cut" in headline_lower or "budget" in headline_lower:
            ev_type = "ECONOMIC_CRISIS"
            
        # Check duplicate in structured_events
        existing = db.query(StructuredEvent).filter(
            StructuredEvent.timestamp == item.timestamp,
            StructuredEvent.headline == item.headline if hasattr(StructuredEvent, 'headline') else StructuredEvent.description == item.headline
        ).first()
        
        # Or look up by desc
        existing = db.query(StructuredEvent).filter(
            StructuredEvent.timestamp == item.timestamp,
            StructuredEvent.description == item.headline
        ).first()
        
        if not existing:
            # Estimate magnitude if possible
            magnitude = 0.0
            if "75 bps" in headline_lower or "75 basis points" in headline_lower:
                magnitude = 0.75
            elif "40 bps" in headline_lower or "40 basis points" in headline_lower:
                magnitude = 0.40
            elif "25 bps" in headline_lower or "25 basis points" in headline_lower:
                magnitude = 0.25
            elif "100 bps" in headline_lower or "100 basis points" in headline_lower:
                magnitude = 1.00
                
            db_ev = StructuredEvent(
                timestamp=item.timestamp,
                event_type=ev_type,
                country=item.country or "Global",
                sector=item.sector or "General",
                magnitude=magnitude,
                entities_involved=item.source,
                source=item.source,
                description=item.headline
            )
            db.add(db_ev)
            stored += 1

    # 2. Convert Economic Calendar Data
    print("Processing EconomicCalendarData -> StructuredEvents...")
    calendar_items = db.query(EconomicCalendarData).all()
    for item in calendar_items:
        ev_type = "general"
        name_lower = item.event_name.lower()
        if "repo rate" in name_lower or "interest rate" in name_lower:
            if "cut" in name_lower or "decisions" in name_lower or "cut" in item.actual_value:
                ev_type = "RATE_CUT"
            else:
                ev_type = "RATE_HIKE"
        elif "cpi" in name_lower or "inflation" in name_lower:
            ev_type = "INFLATION_RELEASE"
        elif "gdp" in name_lower:
            ev_type = "GDP_RELEASE"
            
        existing = db.query(StructuredEvent).filter(
            StructuredEvent.timestamp == item.event_date,
            StructuredEvent.description == item.event_name
        ).first()
        
        if not existing:
            # Parse magnitude from actual value string e.g. "6.00%" -> 6.00
            magnitude = 0.0
            try:
                mag_str = item.actual_value.replace("%", "").strip()
                magnitude = float(mag_str)
            except Exception:
                pass
                
            db_ev = StructuredEvent(
                timestamp=item.event_date,
                event_type=ev_type,
                country=item.country,
                sector="Banking" if "rate" in name_lower else "General",
                magnitude=magnitude,
                entities_involved="Central Bank",
                source="Economic Calendar",
                description=item.event_name
            )
            db.add(db_ev)
            stored += 1

    # 3. Convert Corporate Announcements
    print("Processing CorporateAnnouncements -> StructuredEvents...")
    corp_items = db.query(CorporateAnnouncement).all()
    for item in corp_items:
        ev_type = "CORPORATE_ACTION"
        if item.event_type == "EARNINGS":
            ev_type = "EARNINGS"
        elif item.event_type == "DIVIDEND":
            ev_type = "CORPORATE_ACTION"
        elif item.event_type == "MANAGEMENT_CHANGE":
            ev_type = "REGULATORY_CHANGE"
            
        existing = db.query(StructuredEvent).filter(
            StructuredEvent.timestamp == item.event_date,
            StructuredEvent.description == item.description
        ).first()
        
        if not existing:
            db_ev = StructuredEvent(
                timestamp=item.event_date,
                event_type=ev_type,
                country="India",
                sector="Banking",
                magnitude=0.0,
                entities_involved=item.company_name,
                source=item.exchange_source,
                description=item.description
            )
            db.add(db_ev)
            stored += 1

    # 4. Convert Regulatory Events
    print("Processing RegulatoryEvents -> StructuredEvents...")
    reg_items = db.query(RegulatoryEvent).all()
    for item in reg_items:
        existing = db.query(StructuredEvent).filter(
            StructuredEvent.timestamp == item.timestamp,
            StructuredEvent.description == item.title
        ).first()
        
        if not existing:
            db_ev = StructuredEvent(
                timestamp=item.timestamp,
                event_type="REGULATORY_CHANGE",
                country="India",
                sector=item.affected_sector or "General",
                magnitude=0.0,
                entities_involved=item.related_entities or item.source,
                entities=item.related_entities or item.source,
                source=item.source,
                description=item.title
            )
            db.add(db_ev)
            stored += 1

    # 5. Convert Central Bank Events
    print("Processing CentralBankEvents -> StructuredEvents...")
    cb_items = db.query(CentralBankEvent).all()
    for item in cb_items:
        existing = db.query(StructuredEvent).filter(
            StructuredEvent.timestamp == item.timestamp,
            StructuredEvent.description == item.title
        ).first()
        
        if not existing:
            ev_type = "policy_announcement"
            if item.policy_action == "RATE_HIKE":
                ev_type = "RATE_HIKE"
            elif item.policy_action == "RATE_CUT":
                ev_type = "RATE_CUT"
                
            country_map = {
                "Federal Reserve": "US",
                "ECB": "Eurozone",
                "BoE": "UK",
                "BoJ": "Japan",
                "RBI": "India"
            }
            country = country_map.get(item.central_bank, "Global")
            
            db_ev = StructuredEvent(
                timestamp=item.timestamp,
                event_type=ev_type,
                country=country,
                sector="Banking",
                magnitude=0.0,
                entities_involved=item.central_bank,
                entities=item.central_bank,
                source=item.source,
                description=item.title
            )
            db.add(db_ev)
            stored += 1

    # 6. Convert Geopolitical Events
    print("Processing GeopoliticalEvents -> StructuredEvents...")
    geo_items = db.query(GeopoliticalEvent).all()
    for item in geo_items:
        existing = db.query(StructuredEvent).filter(
            StructuredEvent.timestamp == item.event_start_date,
            StructuredEvent.description == item.description
        ).first()
        
        if not existing:
            db_ev = StructuredEvent(
                timestamp=item.event_start_date,
                event_type=item.event_type,
                country=item.countries_involved,
                sector="General",
                magnitude=1.0 if item.event_severity == "HIGH" else 0.5,
                entities_involved=item.countries_involved,
                entities=item.countries_involved,
                source="Geopolitical Feed",
                description=item.description
            )
            db.add(db_ev)
            stored += 1

    # 7. Convert Banking Relations (earnings transcripts, FSR, annual reports)
    print("Processing BankingRelations -> StructuredEvents...")
    bank_items = db.query(BankingRelations).all()
    for item in bank_items:
        existing = db.query(StructuredEvent).filter(
            StructuredEvent.timestamp == item.timestamp,
            StructuredEvent.description == item.content[:200]
        ).first()
        
        if not existing:
            ev_type = "banking_relations"
            if item.event_type == "EARNINGS_TRANSCRIPT":
                ev_type = "EARNINGS"
            elif item.event_type == "RBI_FSR":
                ev_type = "REGULATORY_CHANGE"
            elif item.event_type == "RBI_ANNUAL":
                ev_type = "RBI_ANNUAL"
                
            db_ev = StructuredEvent(
                timestamp=item.timestamp,
                event_type=ev_type,
                country="India" if item.institution in ["RBI", "SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "IndusInd Bank"] else "Global",
                sector="Banking",
                magnitude=0.0,
                entities_involved=item.institution,
                entities=item.institution,
                source="Banking IR",
                description=item.content[:200]
            )
            db.add(db_ev)
            stored += 1
            
    if stored > 0:
        db.commit()
        print(f"[SUCCESS] Extracted and committed {stored} new structured events!")
    else:
        print("[INFO] No new structured events extracted.")
        
    db.close()

if __name__ == "__main__":
    init_db()
    extract_structured_events()

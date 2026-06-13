from src.database.connection import SessionLocal
from src.database.models import (
    RegulatoryEvent,
    EconomicCalendarData,
    CorporateAnnouncement,
    OptionsIntelligence,
    InstitutionalFlow,
    BankingRelations,
    NewsArticle,
    StructuredEvent
)

db = SessionLocal()
tables = {
    "regulatory_events": RegulatoryEvent,
    "economic_calendar": EconomicCalendarData,
    "corporate_announcements": CorporateAnnouncement,
    "options_intelligence": OptionsIntelligence,
    "institutional_flows": InstitutionalFlow,
    "banking_relations": BankingRelations,
    "news_articles": NewsArticle,
    "structured_events": StructuredEvent
}

print("=== CURRENT DATABASE RECORD COUNTS ===")
for name, model in tables.items():
    try:
        cnt = db.query(model).count()
        print(f"{name}: {cnt} records")
        if cnt > 0:
            first = db.query(model).order_by(model.id.asc()).first()
            last = db.query(model).order_by(model.id.desc()).first()
            # print timestamps
            if hasattr(first, "timestamp") and first.timestamp:
                print(f"  - Earliest: {first.timestamp}")
            elif hasattr(first, "event_date") and first.event_date:
                print(f"  - Earliest: {first.event_date}")
            elif hasattr(first, "date") and first.date:
                print(f"  - Earliest: {first.date}")
            
            if hasattr(last, "timestamp") and last.timestamp:
                print(f"  - Latest: {last.timestamp}")
            elif hasattr(last, "event_date") and last.event_date:
                print(f"  - Latest: {last.event_date}")
            elif hasattr(last, "date") and last.date:
                print(f"  - Latest: {last.date}")
    except Exception as e:
        print(f"{name}: error reading: {e}")
db.close()

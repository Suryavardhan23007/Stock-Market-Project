import datetime
from src.database.connection import SessionLocal
from src.database.models import NewsArticle

HISTORICAL_NEWS_EVENTS = [
    # 1. RBI (India)
    {
        "timestamp": datetime.datetime(2019, 10, 4, 11, 45, tzinfo=datetime.timezone.utc),
        "source": "RBI",
        "headline": "RBI monetary policy: Repo rate cut by 25 basis points to 5.15% to revive growth.",
        "article": "The Monetary Policy Committee (MPC) decided to reduce the policy repo rate under the liquidity adjustment facility (LAF) by 25 basis points to 5.15 per cent to address growth concerns.",
        "url": "https://rbi.org.in/mpc-oct-2019",
        "event_type": "policy_announcement",
        "country": "India",
        "sector": "Banking"
    },
    # 2. SEBI (India)
    {
        "timestamp": datetime.datetime(2020, 9, 1, 9, 0, tzinfo=datetime.timezone.utc),
        "source": "SEBI",
        "headline": "SEBI implements new peak margin rules for intraday traders to curb market leverage.",
        "article": "The Securities and Exchange Board of India (SEBI) introduced a new peak margin framework requiring stock brokers to collect 100% upfront margin for intraday trades, reducing leverage.",
        "url": "https://www.sebi.gov.in/sebiweb/pr/peak-margins",
        "event_type": "government_policy",
        "country": "India",
        "sector": "General"
    },
    # 3. Economic Times (India)
    {
        "timestamp": datetime.datetime(2019, 7, 5, 11, 0, tzinfo=datetime.timezone.utc),
        "source": "Economic Times",
        "headline": "Union Budget 2019: Finance Minister Nirmala Sitharaman announces target to become $5 trillion economy.",
        "article": "The Union Budget 2019-20 introduced measures to boost infrastructure, support start-ups, and encourage digital payments, but also raised surcharge on high-income earners which triggered foreign portfolio investor (FPI) outflows.",
        "url": "https://economictimes.indiatimes.com/budget2019",
        "event_type": "budget_announcement",
        "country": "India",
        "sector": "General"
    },
    # 4. Moneycontrol (India)
    {
        "timestamp": datetime.datetime(2019, 9, 20, 10, 0, tzinfo=datetime.timezone.utc),
        "source": "Moneycontrol",
        "headline": "Corporate Tax Cut: Government slashes corporate tax rates to 22% for domestic companies to boost growth.",
        "article": "In a surprise fiscal move, FM Nirmala Sitharaman announced a reduction in base corporate tax rate to 22% from 30%. This sparked the biggest single-day rally in Sensex and Nifty history in over a decade.",
        "url": "https://moneycontrol.com/news/corporate-tax-cut",
        "event_type": "government_policy",
        "country": "India",
        "sector": "Banking"
    },
    # 5. Business Standard (India)
    {
        "timestamp": datetime.datetime(2020, 2, 1, 11, 0, tzinfo=datetime.timezone.utc),
        "source": "Business Standard",
        "headline": "Union Budget 2020: Finance Minister Nirmala Sitharaman unveils new optional personal income tax slabs.",
        "article": "Budget 2020 focused on digital connectivity, farming reforms, and a new optional tax regime, though markets closed lower due to lack of immediate fiscal stimulus for consumption.",
        "url": "https://business-standard.com/budget2020",
        "event_type": "budget_announcement",
        "country": "India",
        "sector": "General"
    },
    # 6. LiveMint (India)
    {
        "timestamp": datetime.datetime(2020, 3, 23, 10, 0, tzinfo=datetime.timezone.utc),
        "source": "LiveMint",
        "headline": "Lockdown Lock: Indian markets plunge 13% in worst-ever selloff as India goes into lockdown.",
        "article": "Sensex crashed 3,935 points and Nifty hit circuit limit as PM Modi declared a national curfew and domestic states initiated lockdown to curb COVID spread.",
        "url": "https://livemint.com/worst-crash-covid-lockdown",
        "event_type": "government_policy",
        "country": "India",
        "sector": "General"
    },
    # 7. Reuters (Global)
    {
        "timestamp": datetime.datetime(2022, 2, 24, 8, 0, tzinfo=datetime.timezone.utc),
        "source": "Reuters",
        "headline": "Russia invades Ukraine: Global markets plunge, crude oil surges past $105 per barrel.",
        "article": "Russian President Vladimir Putin ordered a special military operation in Ukraine, triggering broad geopolitical sanctions, safe-haven gold buying, and energy spikes.",
        "url": "https://reuters.com/russia-ukraine-outbreak",
        "event_type": "geopolitical_conflict",
        "country": "Global",
        "sector": "General"
    },
    # 8. Bloomberg (Global)
    {
        "timestamp": datetime.datetime(2023, 1, 24, 15, 0, tzinfo=datetime.timezone.utc),
        "source": "Bloomberg",
        "headline": "Hindenburg Research releases critical report on Adani Group, alleging stock manipulation.",
        "article": "Short-seller Hindenburg Research published a report accusing the Adani conglomerate of stock manipulation and corporate fraud, triggering massive selloffs in Adani shares and volatility in the banking index.",
        "url": "https://bloomberg.com/hindenburg-adani-report",
        "event_type": "general_news",
        "country": "India",
        "sector": "Banking"
    },
    # 9. CNBC (Global)
    {
        "timestamp": datetime.datetime(2023, 3, 10, 16, 0, tzinfo=datetime.timezone.utc),
        "source": "CNBC",
        "headline": "Silicon Valley Bank (SVB) shut down by regulators, triggering US banking panic.",
        "article": "California regulators closed SVB following a massive deposit run, marking the largest US retail bank failure since the 2008 financial crisis.",
        "url": "https://cnbc.com/svb-banking-collapse",
        "event_type": "general_news",
        "country": "Global",
        "sector": "Banking"
    },
    # 10. Financial Times (Global)
    {
        "timestamp": datetime.datetime(2022, 6, 15, 18, 30, tzinfo=datetime.timezone.utc),
        "source": "Financial Times",
        "headline": "Federal Reserve raises interest rates by 75 basis points, the largest hike since 1994.",
        "article": "The Federal Open Market Committee announced a major 75 bps increase in rates to fight soaring US inflation, warning that tighter financial conditions will slow global demand.",
        "url": "https://ft.com/fed-hikes-75bps",
        "event_type": "policy_announcement",
        "country": "Global",
        "sector": "Banking"
    },
    # 11. Wall Street Journal (Global)
    {
        "timestamp": datetime.datetime(2024, 9, 18, 18, 30, tzinfo=datetime.timezone.utc),
        "source": "Wall Street Journal",
        "headline": "Fed cuts rates by 50 basis points, embarking on easing cycle to support labor market.",
        "article": "The Federal Reserve cut interest rates by half a percentage point, starting its first easing cycle in four years to protect the job market as inflation cools.",
        "url": "https://wsj.com/fomc-sept-2024",
        "event_type": "policy_announcement",
        "country": "Global",
        "sector": "Banking"
    },
    # 12. IMF (Economic)
    {
        "timestamp": datetime.datetime(2020, 4, 14, 13, 0, tzinfo=datetime.timezone.utc),
        "source": "IMF",
        "headline": "IMF warns of Great Lockout: Global economy to contract by 3% in worst slump since Great Depression.",
        "article": "The International Monetary Fund (IMF) projects the global economy will experience a sharp contraction due to virus lock downs, calling it the worst downturn in nearly a century.",
        "url": "https://imf.org/great-lockdown-forecast",
        "event_type": "macro_release",
        "country": "Global",
        "sector": "General"
    },
    # 13. World Bank (Economic)
    {
        "timestamp": datetime.datetime(2023, 6, 6, 14, 0, tzinfo=datetime.timezone.utc),
        "source": "World Bank",
        "headline": "World Bank cuts global growth outlook to 2.1% as interest rate hikes squeeze credit.",
        "article": "The World Bank lowered its growth forecast, warning that high central bank interest rates are causing global economic deceleration and increasing systemic risk for banks.",
        "url": "https://worldbank.org/global-growth-deceleration",
        "event_type": "macro_release",
        "country": "Global",
        "sector": "Banking"
    },
    # 14. Federal Reserve (Economic)
    {
        "timestamp": datetime.datetime(2020, 3, 15, 21, 0, tzinfo=datetime.timezone.utc),
        "source": "Federal Reserve",
        "headline": "US Federal Reserve slashes interest rates by 100 basis points to near zero, launches $700B QE.",
        "article": "In an emergency Sunday announcement, the Federal Reserve cut its benchmark target rate to 0-0.25% and announced massive bond purchases to prevent financial market collapse.",
        "url": "https://federalreserve.gov/emergency-rate-cut-2020",
        "event_type": "policy_announcement",
        "country": "Global",
        "sector": "Banking"
    },
    # 15. X/Twitter (Social)
    {
        "timestamp": datetime.datetime(2021, 5, 12, 23, 0, tzinfo=datetime.timezone.utc),
        "source": "X_Twitter",
        "headline": "Crypto Selloff: Bitcoin falls 10% after Elon Musk announcements on X.",
        "article": "Social media posts regarding cryptocurrency usage sparked rapid liquidations, showcasing the direct impact of social media announcements on modern financial asset classes.",
        "url": "https://x.com/musk-bitcoin-impact",
        "event_type": "social_sentiment",
        "country": "Global",
        "sector": "General"
    }
]

def seed_news_articles():
    db = SessionLocal()
    print("[INFO] Seeding complete set of historical news events representing all required sources...")
    
    records = []
    for item in HISTORICAL_NEWS_EVENTS:
        existing = db.query(NewsArticle).filter(NewsArticle.url == item["url"]).first()
        if not existing:
            records.append(
                NewsArticle(
                    timestamp=item["timestamp"],
                    source=item["source"],
                    headline=item["headline"],
                    article=item["article"],
                    url=item["url"],
                    event_type=item["event_type"],
                    country=item["country"],
                    sector=item["sector"],
                    processed=False
                )
            )
            
    if records:
        db.bulk_save_objects(records)
        db.commit()
        print(f"[SUCCESS] Seeded {len(records)} news articles.")
    else:
        print("[INFO] All news articles already exist in DB.")
        
    db.close()

if __name__ == "__main__":
    seed_news_articles()

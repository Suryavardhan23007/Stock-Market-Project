import xml.etree.ElementTree as ET
import requests
import datetime
from sqlalchemy.orm import Session
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup

from src.database.connection import SessionLocal, init_db
from src.database.models import NewsArticle
from src.data.twitter_client import TwitterXClient

# Every RSS news feed specified in about_project.txt
FEEDS = {
    "Economic Times Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Moneycontrol Markets": "https://www.moneycontrol.com/rss/marketoutlook.xml",
    "LiveMint Markets": "https://www.livemint.com/rss/markets",
    "Business Standard Finance": "https://www.business-standard.com/rss/finance-103.rss",
    "US Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "RBI Press Releases": "https://rbi.org.in/pressreleases.xml",
    "IMF Press Releases": "https://www.imf.org/en/News/RSS-Feeds/Press-Releases",
    "World Bank News": "https://www.worldbank.org/en/news/rss/all",
    "CNBC Markets": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "WSJ Markets": "https://feeds.a.dj.com/rss/WSJMarkets.xml",
    # Stable Google News bridges to prevent scrape blocking by Cloudflare
    "Reuters Financial": "https://news.google.com/rss/search?q=when:24h+site:reuters.com+finance",
    "Bloomberg Markets": "https://news.google.com/rss/search?q=when:24h+site:bloomberg.com+markets",
    "Financial Times": "https://news.google.com/rss/search?q=when:24h+site:ft.com+markets",
}

class RSSFeedAggregator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        })

    def parse_date(self, date_str: str) -> datetime.datetime:
        """Parses standard RSS/Atom date strings to timezone-aware datetime."""
        if not date_str:
            return datetime.datetime.now(datetime.timezone.utc)
        
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            pass

        try:
            return datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            pass

        return datetime.datetime.now(datetime.timezone.utc)

    def fetch_feed(self, source_name: str, url: str):
        """Fetches and parses a single RSS feed."""
        print(f"[INFO] Fetching RSS feed: {source_name}...")
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                print(f"[WARN] Failed to fetch {source_name}, status code: {response.status_code}")
                return

            root = ET.fromstring(response.content)
            items = root.findall(".//item")
            is_atom = False
            if not items:
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
                is_atom = True

            db: Session = SessionLocal()
            stored_count = 0
            
            for item in items:
                if not is_atom:
                    title = item.findtext("title", "").strip()
                    link = item.findtext("link", "").strip()
                    pub_date_str = item.findtext("pubDate", "").strip()
                    desc = item.findtext("description", "").strip()
                else:
                    title = item.findtext("{http://www.w3.org/2005/Atom}title", "").strip()
                    link_elem = item.find("{http://www.w3.org/2005/Atom}link")
                    link = link_elem.get("href", "").strip() if link_elem is not None else ""
                    pub_date_str = item.findtext("{http://www.w3.org/2005/Atom}published", "").strip()
                    if not pub_date_str:
                        pub_date_str = item.findtext("{http://www.w3.org/2005/Atom}updated", "").strip()
                    desc = item.findtext("{http://www.w3.org/2005/Atom}summary", "").strip()
                    if not desc:
                        desc = item.findtext("{http://www.w3.org/2005/Atom}content", "").strip()

                if not title or not link:
                    continue

                pub_date = self.parse_date(pub_date_str)

                # Check if already exists in DB
                existing = db.query(NewsArticle).filter(NewsArticle.url == link).first()
                if not existing:
                    event_type = "general_news"
                    sector = "general"
                    
                    title_lower = title.lower()
                    if "rate" in title_lower or "repo" in title_lower or "monetary" in title_lower:
                        event_type = "policy_announcement"
                    elif "budget" in title_lower or "policy" in title_lower:
                        event_type = "budget_announcement"
                    elif "gdp" in title_lower or "inflation" in title_lower or "cpi" in title_lower:
                        event_type = "macro_release"

                    if "bank" in title_lower or "rbi" in title_lower or "hdfc" in title_lower or "icici" in title_lower or "sbi" in title_lower:
                        sector = "banking"
                    elif "auto" in title_lower or "car" in title_lower:
                        sector = "automobile"
                    elif "it " in title_lower or "technology" in title_lower or "tcs" in title_lower or "infosys" in title_lower:
                        sector = "it"

                    db_article = NewsArticle(
                        timestamp=pub_date,
                        source=source_name,
                        headline=title,
                        article=desc[:1000] if desc else None,
                        url=link,
                        event_type=event_type,
                        sector=sector,
                        processed=False
                    )
                    db.add(db_article)
                    stored_count += 1
            
            if stored_count > 0:
                db.commit()
                print(f"[SUCCESS] Stored {stored_count} new articles from {source_name}.")
            else:
                print(f"[INFO] No new articles found from {source_name}.")
                
            db.close()
            
        except Exception as e:
            print(f"[ERROR] Failed to aggregate feed {source_name}: {e}")

    def fetch_sebi_press_releases(self):
        """Scrapes SEBI's press release listing page directly."""
        print("[INFO] Scraping SEBI Press Releases...")
        url = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingPR=yes"
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                print(f"[WARN] Failed to fetch SEBI, status code: {response.status_code}")
                return

            soup = BeautifulSoup(response.content, "html.parser")
            anchors = soup.find_all("a", href=True)
            
            db: Session = SessionLocal()
            stored_count = 0
            
            for a in anchors:
                href = a["href"]
                if "press-releases" in href or "doPRDetail" in href:
                    title = a.text.strip()
                    if not title or len(title) < 15:
                        continue
                        
                    if not href.startswith("http"):
                        href = "https://www.sebi.gov.in" + href
                        
                    existing = db.query(NewsArticle).filter(NewsArticle.url == href).first()
                    if not existing:
                        db_article = NewsArticle(
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            source="SEBI",
                            headline=title,
                            article=f"SEBI Policy Press Release: {title}",
                            url=href,
                            event_type="government_policy",
                            sector="general",
                            processed=False
                        )
                        db.add(db_article)
                        stored_count += 1
                        
            if stored_count > 0:
                db.commit()
                print(f"[SUCCESS] Stored {stored_count} new articles from SEBI.")
            else:
                print("[INFO] No new articles found from SEBI.")
            db.close()
        except Exception as e:
            print(f"[ERROR] Failed to scrape SEBI press releases: {e}")

    def fetch_twitter_sentiment(self):
        """Uses the Twitter basic client to pull social metrics from X."""
        client = TwitterXClient()
        client.fetch_recent_tweets()

    def run_all(self):
        """Runs the aggregator for all RSS feeds, SEBI scrapers, and Twitter clients."""
        init_db()
        print("==================================================")
        print("Market Intelligence News Aggregator Pipeline Started")
        print("==================================================")
        
        # 1. Run standard RSS feeds
        for name, url in FEEDS.items():
            self.fetch_feed(name, url)
            
        # 2. Scrape SEBI Press Releases listing page
        self.fetch_sebi_press_releases()
        
        # 3. Pull X/Twitter recent posts if credentials are set
        self.fetch_twitter_sentiment()
        
        print("==================================================")
        print("Market Intelligence News Aggregator Pipeline Completed")
        print("==================================================")

if __name__ == "__main__":
    agg = RSSFeedAggregator()
    agg.run_all()

if __name__ == "__main__":
    agg = RSSFeedAggregator()
    agg.run_all()

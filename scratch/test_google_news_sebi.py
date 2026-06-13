import requests
import xml.etree.ElementTree as ET

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

queries = {
    "SEBI Google News": "https://news.google.com/rss/search?q=site:sebi.gov.in",
    "RBI Google News": "https://news.google.com/rss/search?q=site:rbi.org.in"
}

for name, url in queries.items():
    print(f"Requesting: {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"  - Status Code: {r.status_code}")
        root = ET.fromstring(r.content)
        items = root.findall(".//item")
        print(f"  - Found {len(items)} items.")
        if items:
            print("  - Sample headline:")
            print(f"    * {items[0].findtext('title')}")
    except Exception as e:
        print(f"  - Failed: {e}")

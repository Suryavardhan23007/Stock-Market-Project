import requests
import xml.etree.ElementTree as ET

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://news.google.com/rss/search?q=site:sebi.gov.in+after:2022-01-01+before:2022-12-31"
print(f"Requesting: {url}...")
try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"  - Status Code: {r.status_code}")
    root = ET.fromstring(r.content)
    items = root.findall(".//item")
    print(f"  - Found {len(items)} items.")
    if items:
        print("  - Sample headlines:")
        for idx, item in enumerate(items[:5]):
            print(f"    * {item.findtext('title')} ({item.findtext('pubDate')})")
except Exception as e:
    print(f"  - Failed: {e}")

import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

urls = {
    "SEBI PR": "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingPR=yes",
    "RBI PR": "https://rbi.org.in/pressreleases.xml",
    "NSE Announcements": "https://www.nseindia.com/api/corporate-announcements?index=equities",
    "Moneycontrol Sitemap": "https://www.moneycontrol.com/sitemap_index.xml",
    "Economic Times Archive": "https://economictimes.indiatimes.com/archive.cms"
}

for name, url in urls.items():
    print(f"Testing connection to {name}: {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"  - Status Code: {r.status_code}")
        print(f"  - Length: {len(r.content)} bytes")
    except Exception as e:
        print(f"  - Failed: {e}")

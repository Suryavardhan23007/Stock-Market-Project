import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    # Exclude 'br' from encoding
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
}

session = requests.Session()
print("GET home page...")
session.get("https://www.nseindia.com", headers=headers, timeout=10)

url = "https://www.nseindia.com/api/corporate-announcements?index=equities&from_date=01-06-2023&to_date=10-06-2023"
print(f"GET {url}...")
try:
    r = session.get(url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Content-Encoding: {r.headers.get('Content-Encoding')}")
    data = r.json()
    print(f"Successfully parsed JSON. Number of records: {len(data)}")
    if data:
        print("First record:")
        print(data[0])
except Exception as e:
    print(f"Failed: {e}")

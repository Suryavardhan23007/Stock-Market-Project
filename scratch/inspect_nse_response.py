import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br"
}

session = requests.Session()
print("GET home page to establish session...")
session.get("https://www.nseindia.com", headers=headers, timeout=10)

url = "https://www.nseindia.com/api/corporate-announcements?index=equities&from_date=01-06-2023&to_date=10-06-2023"
print(f"GET {url}...")
try:
    r = session.get(url, headers=headers, timeout=10)
    print(f"Response URL: {r.url}")
    print(f"Status Code: {r.status_code}")
    print(f"Headers: {dict(r.headers)}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print("\nText Snippet:")
    print(r.text[:1000])
except Exception as e:
    print(f"Failed: {e}")

import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

session = requests.Session()
# Establish session first
print("Establishing session with NSE homepage...")
session.get("https://www.nseindia.com", headers=headers, timeout=10)

url = "https://www.nseindia.com/api/corporate-announcements?index=equities&from_date=01-06-2023&to_date=10-06-2023"
print(f"Requesting: {url}...")
try:
    r = session.get(url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Length: {len(r.content)} bytes")
    data = r.json()
    print(f"Type: {type(data)}")
    print(f"Number of records: {len(data)}")
    if data and isinstance(data, list):
        print("First record snippet:")
        print(data[0])
except Exception as e:
    print(f"Failed: {e}")

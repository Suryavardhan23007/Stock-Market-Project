import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

tests = [
    {"year": "2024", "month": "January", "day": "2024-01-01"},
    {"year": "2023", "month": "June", "day": "2023-06-01"},
    {"year": "2022", "month": "May", "day": "2022-05-04"},
    {"year": "2021", "month": "December", "day": "2021-12-01"},
    {"year": "2019", "month": "March", "day": "2019-03-01"}
]

for t in tests:
    url = f"https://economictimes.indiatimes.com/archivelist_include.cms?year={t['year']}&month={t['month']}&day={t['day']}"
    print(f"Requesting: {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"  - Status Code: {r.status_code}")
        print(f"  - Length: {len(r.content)} bytes")
        snippet = r.content[:200].decode('utf-8', errors='ignore').strip()
        print(f"  - Snippet: '{snippet}'")
    except Exception as e:
        print(f"  - Error: {e}")

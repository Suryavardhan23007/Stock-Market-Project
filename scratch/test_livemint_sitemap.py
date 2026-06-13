import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://www.livemint.com/sitemap.xml"
print(f"Requesting Livemint Sitemap Index: {url}...")
try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"  - Status Code: {r.status_code}")
    print(f"  - Length: {len(r.content)} bytes")
    snippet = r.content[:500].decode('utf-8', errors='ignore').strip()
    print(f"  - Snippet:\n{snippet}")
except Exception as e:
    print(f"  - Failed: {e}")

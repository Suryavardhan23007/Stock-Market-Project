import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://www.business-standard.com/robots.txt"
print(f"Requesting: {url}...")
try:
    r = requests.get(url, headers=headers, timeout=10)
    print(r.text[:2000])
except Exception as e:
    print(f"Failed: {e}")

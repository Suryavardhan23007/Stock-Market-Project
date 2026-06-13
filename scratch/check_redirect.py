import requests

url = "https://economictimes.indiatimes.com/archive/year-2024,month-1.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
print(f"Request URL: {url}")
print(f"Response URL: {r.url}")
print(f"History: {r.history}")
print(f"Status Code: {r.status_code}")

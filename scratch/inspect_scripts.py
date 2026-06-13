import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archive/year-2024,month-1.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

scripts = soup.find_all("script")
print(f"Total script tags: {len(scripts)}")
for idx, s in enumerate(scripts):
    src = s.get("src")
    text = s.text.strip()
    if src:
        print(f"Script {idx}: src='{src}'")
    elif text:
        print(f"Script {idx}: inline ({len(text)} chars)")
        if "calender" in text or "archive" in text or "year" in text:
            print(f"  Matches keyword! Snippet:\n{text[:500]}")
            print("-" * 50)

import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archive.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

print("Found links on archive.cms:")
links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "archive" in href or "archivelist" in href:
        links.append((a.text.strip(), href))
        
for t, h in links[:30]:
    print(f"  - {t}: {h}")

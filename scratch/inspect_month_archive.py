import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archive/year-2024,month-1.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "starttime" in href:
        links.append((a.text.strip(), href))
        
print(f"Found {len(links)} links with 'starttime' inside month archive:")
for t, h in links[:35]:
    print(f"  - {t}: {h}")

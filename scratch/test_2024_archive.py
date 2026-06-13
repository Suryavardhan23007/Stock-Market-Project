import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2024,month-1,starttime-45292.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

page_content = soup.find(id="pageContent")
if page_content:
    print("=== 2024-01-01 pageContent text ===")
    print(page_content.text.strip()[:1000])
    
    # Print all links inside pageContent
    print("\n=== 2024-01-01 pageContent links ===")
    for a in page_content.find_all("a", href=True):
        print(f"  - Link: '{a.text.strip()}' -> '{a['href']}'")
else:
    print("pageContent not found.")

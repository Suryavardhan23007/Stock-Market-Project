import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2023,month-1,starttime-44951.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

page_content = soup.find(id="pageContent")
if page_content:
    print("=== Page Content Text ===")
    print(page_content.text.strip()[:300])
else:
    print("pageContent not found.")
    
# Let's find any breadcrumb or date header in the body
h1 = soup.find("h1")
if h1:
    print(f"H1: {h1.text.strip()}")

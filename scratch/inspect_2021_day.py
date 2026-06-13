import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2021,month-12,starttime-44531.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

page_content = soup.find(id="pageContent")
if page_content:
    print("Found pageContent for Dec 1, 2021.")
    print("Page Content HTML Snippet:")
    print(str(page_content)[:2000])
else:
    print("pageContent NOT found.")

# Find all articleshow links on the entire page
all_articleshow = [a['href'] for a in soup.find_all("a", href=True) if "/articleshow/" in a["href"]]
print(f"Total articleshow links on the entire page: {len(all_articleshow)}")
for l in all_articleshow[:10]:
    print(f"  - {l}")

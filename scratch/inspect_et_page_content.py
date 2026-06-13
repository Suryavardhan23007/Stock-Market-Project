import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2019,month-3,starttime-43525.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

page_content = soup.find(id="pageContent")
if page_content:
    print("Found section#pageContent")
    # Let's see some divs or lists inside it
    # Print the hierarchy of divs or other tags
    for tag in page_content.find_all(recursive=False):
        print(f"Direct Child: {tag.name}.{'.'.join(tag.get('class', []))} id={tag.get('id', '')}")
        
    # Let's find all links inside page_content
    links = []
    for a in page_content.find_all("a", href=True):
        links.append((a.text.strip(), a["href"]))
    print(f"\nFound {len(links)} total links inside pageContent.")
    if links:
        print("First 10 links in pageContent:")
        for t, h in links[:10]:
            print(f"  - {t}: {h}")
else:
    print("section#pageContent not found.")

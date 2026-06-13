import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2019,month-3,starttime-43525.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

# Find all tables
tables = soup.find_all("table")
print(f"Total tables: {len(tables)}")
for i, t in enumerate(tables):
    print(f"Table {i}:")
    print(f"  Parent: {t.parent.name}.{'.'.join(t.parent.get('class', []))} id={t.parent.get('id', '')}")
    links = t.find_all("a", href=True)
    print(f"  Links inside: {len(links)}")
    articleshow_links = [l for l in links if "/articleshow/" in l["href"]]
    print(f"  Articleshow links inside: {len(articleshow_links)}")
    if articleshow_links:
        print("  Sample articleshow links:")
        for l in articleshow_links[:3]:
            print(f"    * {l.text.strip()} -> {l['href']}")
            
# Let's check for any ul/li listing that contains articleshow
ul_lists = soup.find_all("ul")
print(f"\nTotal UL lists: {len(ul_lists)}")
for i, ul in enumerate(ul_lists[:10]):
    links = ul.find_all("a", href=True)
    articleshow_links = [l for l in links if "/articleshow/" in l["href"]]
    if articleshow_links:
        print(f"UL {i} (Parent: {ul.parent.name}.{'.'.join(ul.parent.get('class', []))}) has {len(articleshow_links)} articleshow links.")
        print("  Sample:")
        for l in articleshow_links[:2]:
            print(f"    * {l.text.strip()} -> {l['href']}")

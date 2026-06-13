import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2019,month-3,starttime-43525.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

links = soup.find_all("a", href=True)
articleshow_links = [l for l in links if "/articleshow/" in l["href"]]
print(f"Total articleshow links: {len(articleshow_links)}")

# Group by parent tag hierarchy
groups = {}
for l in articleshow_links:
    path = []
    curr = l.parent
    while curr and curr.name != "[document]":
        path.append(curr.name)
        curr = curr.parent
    path_str = " -> ".join(reversed(path))
    groups[path_str] = groups.get(path_str, 0) + 1

print("\nLink count by parent hierarchy:")
for k, v in groups.items():
    print(f"  - {k}: {v} links")

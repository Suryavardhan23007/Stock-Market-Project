import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2019,month-3,starttime-43525.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

# Find the main container of the archive links.
# Usually it is a <table> or <ul> inside a specific section.
# Let's inspect elements with text containing articleshow and see their parents.
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/articleshow/" in href:
        # Print parent elements path
        parent_names = []
        curr = a.parent
        while curr and curr.name != "[document]":
            parent_names.append(curr.name)
            if curr.get("class"):
                parent_names[-1] += f".{'.'.join(curr.get('class'))}"
            if curr.get("id"):
                parent_names[-1] += f"#{curr.get('id')}"
            curr = curr.parent
        print(f"Link: {a.text[:40]}... -> URL: {href}")
        print(f"  Parent hierarchy: {' -> '.join(reversed(parent_names))}")
        print("-" * 40)
        break

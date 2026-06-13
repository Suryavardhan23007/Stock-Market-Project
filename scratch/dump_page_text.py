import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2019,month-3,starttime-43525.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

# Print all anchor tags on the page that do not have class or style to see if there are standard links.
all_anchors = soup.find_all("a", href=True)
print(f"Total anchors on page: {len(all_anchors)}")

# Print first 20 anchors
for idx, a in enumerate(all_anchors[:50]):
    print(f"Anchor {idx}: text='{a.text.strip()}' -> href='{a['href']}'")

import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2019,month-3,starttime-43525.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

# Print all elements that look like a list of news articles
# Usually, they are in a table or ul list inside the pageContent section.
# Let's print the plain text of pageContent to see if the list is empty.
page_content = soup.find(id="pageContent")
if page_content:
    print("=== pageContent text ===")
    print(page_content.text.strip()[:2000])
    
    # Print all links inside pageContent
    print("\n=== pageContent links ===")
    for a in page_content.find_all("a", href=True):
        print(f"  - Link: '{a.text.strip()}' -> '{a['href']}'")
else:
    print("pageContent not found.")

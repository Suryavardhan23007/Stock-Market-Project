import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2019,month-3,starttime-43525.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

table = soup.find(id="pageContent").find("table") if soup.find(id="pageContent") else None
if table:
    print("Found table inside pageContent.")
    # Print the table outer HTML (first 1000 characters)
    html_str = str(table)
    print(html_str[:1500])
    
    # Check if there are links
    links = table.find_all("a", href=True)
    print(f"\nNumber of links in table: {len(links)}")
    for l in links[:10]:
        print(f"  - Link text: '{l.text.strip()}' -> href: '{l['href']}'")
else:
    print("No table found inside pageContent.")

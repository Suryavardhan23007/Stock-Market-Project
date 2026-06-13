import datetime
import requests
from bs4 import BeautifulSoup

def get_et_serial_date(d: datetime.date) -> int:
    # 1900-01-01 is 1 in Excel, but Excel incorrectly treats 1900 as a leap year
    # So we use a known anchor
    anchor_date = datetime.date(2022, 1, 1)
    anchor_serial = 44562
    delta = d - anchor_date
    return anchor_serial + delta.days

# Test for March 1, 2019
test_date = datetime.date(2019, 3, 1)
serial = get_et_serial_date(test_date)
print(f"Date: {test_date}, Year: {test_date.year}, Month: {test_date.month}, Serial: {serial}")

# Let's request the page for March 1, 2019
url = f"https://economictimes.indiatimes.com/archivelist/year-{test_date.year},month-{test_date.month},starttime-{serial}.cms"
print(f"Requesting: {url}...")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Content Length: {len(r.content)}")
    
    # Parse and extract some links
    soup = BeautifulSoup(r.content, "html.parser")
    # ET archive lists links inside a table or UL with class "content" or similar. Let's find links containing /articleshow/
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/articleshow/" in href:
            links.append((a.text.strip(), href))
            
    print(f"Found {len(links)} articleshow links.")
    if links:
        print("First 5 links:")
        for t, h in links[:5]:
            print(f"  - {t}: {h}")
except Exception as e:
    print(f"Error: {e}")

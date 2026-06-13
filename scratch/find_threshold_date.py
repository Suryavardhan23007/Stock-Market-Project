import datetime
import requests
from bs4 import BeautifulSoup

ref_date = datetime.date(1899, 12, 30)

# Check the 1st of every month from Jan 2024 back to Jan 2019
start_date = datetime.date(2024, 1, 1)
end_date = datetime.date(2019, 1, 1)

current = start_date
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Running historical threshold diagnostics...")
while current >= end_date:
    serial = (current - ref_date).days
    url = f"https://economictimes.indiatimes.com/archivelist/year-{current.year},month-{current.month},starttime-{serial}.cms"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.content, "html.parser")
        page_content = soup.find(id="pageContent")
        links = []
        if page_content:
            for a in page_content.find_all("a", href=True):
                if "/articleshow/" in a["href"]:
                    links.append(a.text.strip())
        print(f"Date: {current} (Serial: {serial}) -> found {len(links)} links.")
    except Exception as e:
        print(f"Date: {current} -> Error: {e}")
        
    # Go back 1 month
    # Subtracting days: if current is 1st of month, going back 5 days will get to previous month, then set day to 1
    prev_month_date = current - datetime.timedelta(days=5)
    current = datetime.date(prev_month_date.year, prev_month_date.month, 1)

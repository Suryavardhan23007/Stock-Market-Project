import datetime
import requests
from bs4 import BeautifulSoup

ref_date = datetime.date(1899, 12, 30)

test_dates = [
    datetime.date(2019, 3, 1),
    datetime.date(2019, 7, 5),
    datetime.date(2019, 9, 20),
    datetime.date(2020, 3, 23),
    datetime.date(2021, 2, 1),
    datetime.date(2022, 5, 4),
    datetime.date(2023, 1, 25),
    datetime.date(2024, 6, 4),
    datetime.date(2025, 1, 1),
    datetime.date(2026, 5, 1)
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for d in test_dates:
    serial = (d - ref_date).days
    url = f"https://economictimes.indiatimes.com/archivelist/year-{d.year},month-{d.month},starttime-{serial}.cms"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # Count links inside table or pageContent
        page_content = soup.find(id="pageContent")
        links = []
        if page_content:
            # Check the children tables or lists
            for a in page_content.find_all("a", href=True):
                if "/articleshow/" in a["href"]:
                    links.append(a.text.strip())
        print(f"Date: {d} (Serial: {serial}) -> HTTP {r.status_code}, length {len(r.content)} bytes, found {len(links)} articleshow links inside pageContent.")
        if links:
            print(f"  Samples: {links[:3]}")
    except Exception as e:
        print(f"Date: {d} -> Error: {e}")

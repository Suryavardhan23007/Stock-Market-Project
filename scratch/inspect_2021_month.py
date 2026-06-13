import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archive/year-2021,month-12.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

page_content = soup.find(id="pageContent")
if page_content:
    print("Found pageContent for Dec 2021 monthly page.")
    # Check if there is calendar div
    cal_div = page_content.find(id="calenderdiv")
    if cal_div:
        print(f"Found calenderdiv: '{cal_div.text.strip()}'")
        # Print sub-elements
        print(str(cal_div)[:1000])
    else:
        print("calenderdiv NOT found in pageContent.")
else:
    print("pageContent NOT found.")

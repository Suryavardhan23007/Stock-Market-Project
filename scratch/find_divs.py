import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archive/year-2024,month-1.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

page_content = soup.find(id="pageContent")
if page_content:
    print("Found section#pageContent")
    # Print all sub-divs and classes
    for d in page_content.find_all("div"):
        print(f"Div: class={d.get('class', [])} id={d.get('id', '')}")
        # Print text snippet
        print(f"  Snippet: {d.text.strip()[:100]}")
else:
    print("pageContent not found.")

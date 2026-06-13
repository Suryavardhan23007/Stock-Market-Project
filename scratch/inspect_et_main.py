import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2019,month-3,starttime-43525.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

# Find the main container
# Usually there is a table or div.content in the middle. Let's search for table or divs that contain links.
main_section = soup.find("section", class_="main_container")
if main_section:
    print("Found section.main_container")
    # Let's see the structure of children of main_section
    for child in main_section.children:
        if child.name:
            print(f"Child: {child.name}.{'.'.join(child.get('class', []))} id={child.get('id', '')}")
            
# Let's find links inside a <table> or specific <div> that lists the actual archive content.
# Usually, ET archive has a table inside a div with class "content" or similar.
# Let's search for tables on the page.
tables = soup.find_all("table")
print(f"\nFound {len(tables)} tables on the page.")
for idx, table in enumerate(tables):
    print(f"Table {idx}: class={table.get('class', [])} id={table.get('id', '')}")
    # Print some links inside it
    links = []
    for a in table.find_all("a", href=True):
        if "/articleshow/" in a["href"]:
            links.append((a.text.strip(), a["href"]))
    print(f"  - Contained {len(links)} articleshow links.")
    if links:
        print("  - Sample links:")
        for t, h in links[:3]:
            print(f"    * {t}: {h}")

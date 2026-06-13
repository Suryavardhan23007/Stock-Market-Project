import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/archivelist/year-2019,month-3,starttime-43525.cms"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

# Get text from body
text = soup.body.get_text(separator="\n")
lines = [l.strip() for l in text.split("\n") if l.strip()]

print(f"Total lines: {len(lines)}")
print("Sample lines:")
for i, line in enumerate(lines[:100]):
    print(f"{i}: {line}")

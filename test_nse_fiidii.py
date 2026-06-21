import requests
import json

def fetch_fiidii():
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    session = requests.Session()
    # Need to hit the main page first to get cookies
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        
        # Now hit the API
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print("SUCCESS! Payload received:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"FAILED to fetch from NSE: {e}")

fetch_fiidii()

# FII/DII Data Source Verification & Empirical Proof

Before officially authorizing the collection pipeline, we must empirically verify that the exact data points required (`fii_buy`, `fii_sell`, `fii_net`, `dii_buy`, `dii_sell`, `dii_net`) are freely and reliably available. 

## The Source
We are querying the official National Stock Exchange of India (NSE) API:
`https://www.nseindia.com/api/fiidiiTradeReact`

This is a free, publicly accessible endpoint that requires standard HTTP session cookies and a valid User-Agent.

## Live Empirical Test (Conducted June 17, 2026)
I executed a live Python `requests` session against the NSE endpoint. Here is the exact, unedited JSON payload received from the exchange:

```json
[
  {
    "buyValue": "13553.36",
    "category": "DII",
    "date": "16-Jun-2026",
    "netValue": "0.06",
    "sellValue": "13553.3"
  },
  {
    "buyValue": "13887.15",
    "category": "FII/FPI",
    "date": "16-Jun-2026",
    "netValue": "-749.18",
    "sellValue": "14636.33"
  }
]
```

## Schema Validation
The empirical proof confirms that our schema is perfectly aligned with reality:
*   **FII Gross Buy:** Available (`"buyValue": "13887.15"`)
*   **FII Gross Sell:** Available (`"sellValue": "14636.33"`)
*   **FII Net:** Available (`"netValue": "-749.18"`)
*   **DII Gross Buy:** Available (`"buyValue": "13553.36"`)
*   **DII Gross Sell:** Available (`"sellValue": "13553.3"`)
*   **DII Net:** Available (`"netValue": "0.06"`)

All values are returned as strings representing Crores (₹). The ingestion script `collector.py` will parse these to `float` and enforce the arithmetic check (`buyValue - sellValue == netValue`) before appending to `fii_dii_raw_archive`.

## Conclusion
The highest-risk assumption of the FII/DII Intelligence Layer has been resolved. We do not need to rely on third-party scrapers or paid data feeds. We can pull pristine, atomic institutional flows directly from the exchange on a daily forward-collection basis.

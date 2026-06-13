# Intelligence, News, and Event Memory

This module implements the event ingestion pipeline, embeds financial news headlines/articles, updates the Qdrant vector database, and generates explanatory forecasts.

## Components

- `rss_feed_aggregator.py`: Pulls financial news articles and central bank announcements from RSS feeds at regular intervals.
- `event_pipeline.py`: Parses news details, generates text embeddings using Sentence Transformers (e.g., FinBERT or local sentence-transformer models), and writes them to Qdrant.
- `event_retriever.py`: Retrieves previous similar financial events from Qdrant by querying current news headlines.
- `explainer.py`: Interfaces with the Gemini API to explain predicted signals, historical reactions, and macroeconomic factors.

## Supported Sources

- Tier 1: RBI Circulars, Economic Times, SEBI Press Releases, LiveMint, Moneycontrol, Reuters, US Federal Reserve.
- Tier 2: Ministry of Finance, Press Information Bureau (PIB), IMF, World Bank.
- Tier 3: RBI Policy Updates, Major Bank Press Releases (SBI, HDFC, ICICI, AXIS, Kotak).

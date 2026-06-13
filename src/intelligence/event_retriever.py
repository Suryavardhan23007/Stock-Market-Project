import datetime
import torch
from transformers import AutoTokenizer, AutoModel
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient

from src.config.config import config
from src.database.connection import SessionLocal
from src.database.models import MarketCandle

class EventRetriever:
    def __init__(self):
        print("[INFO] Initializing FinBERT model ('ProsusAI/finbert')...")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModel.from_pretrained("ProsusAI/finbert")
        print("[INFO] FinBERT model loaded successfully.")
        
        self.qclient = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        self.collection_name = "news_events"

    def get_embedding(self, text: str) -> list[float]:
        """Generates a 768-dimensional sentence embedding from FinBERT using mean pooling."""
        inputs = self.tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Mean pooling of token hidden states
        attention_mask = inputs['attention_mask']
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        embedding = sum_embeddings / sum_mask
        return embedding[0].tolist()

    def retrieve_similar_events(self, headline: str, top_k: int = 3) -> list[dict]:
        """Queries Qdrant to find the top_k most similar historical events."""
        try:
            # Embed the query headline using FinBERT
            query_vector = self.get_embedding(headline)
            
            # Search Qdrant
            results = self.qclient.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )
            
            similar_events = []
            for res in results:
                payload = res.payload
                score = res.score
                similar_events.append({
                    "id": payload.get("id"),
                    "headline": payload.get("headline"),
                    "url": payload.get("url"),
                    "source": payload.get("source"),
                    "timestamp": datetime.datetime.fromisoformat(payload.get("timestamp")),
                    "sentiment_label": payload.get("sentiment_label"),
                    "sentiment_score": payload.get("sentiment_score"),
                    "similarity_score": score
                })
            return similar_events
        except Exception as e:
            print(f"[ERROR] Qdrant similarity search failed: {e}")
            return []

    def study_market_reaction(self, symbol: str, event_time: datetime.datetime, window_minutes_before: int = 15, window_minutes_after: int = 60) -> dict:
        """Fetches market candles surrounding a historical event and calculates return metrics."""
        db: Session = SessionLocal()
        
        start_time = event_time - datetime.timedelta(minutes=window_minutes_before)
        end_time = event_time + datetime.timedelta(minutes=window_minutes_after)
        
        # Query candles
        candles = db.query(MarketCandle).filter(
            MarketCandle.symbol == symbol,
            MarketCandle.timestamp >= start_time,
            MarketCandle.timestamp <= end_time
        ).order_by(MarketCandle.timestamp.asc()).all()
        
        db.close()
        
        if not candles:
            return {
                "status": "No price data available",
                "pre_event_price": None,
                "post_event_price": None,
                "max_price": None,
                "min_price": None,
                "percent_return": 0.0
            }
            
        pre_event_candles = [c for c in candles if c.timestamp <= event_time]
        post_event_candles = [c for c in candles if c.timestamp > event_time]
        
        pre_price = pre_event_candles[-1].close if pre_event_candles else candles[0].open
        post_price = post_event_candles[-1].close if post_event_candles else candles[-1].close
        
        closes = [c.close for c in candles]
        max_p = max(closes)
        min_p = min(closes)
        
        pct_return = ((post_price - pre_price) / pre_price) * 100 if pre_price > 0 else 0.0
        
        return {
            "status": "SUCCESS",
            "pre_event_price": pre_price,
            "post_event_price": post_price,
            "max_price": max_p,
            "min_price": min_p,
            "percent_return": pct_return,
            "candle_count": len(candles)
        }

    def analyze_event_context(self, current_headline: str, symbol: str) -> list[dict]:
        """Combines similarity search and market reaction studies into a context report."""
        print(f"[INFO] Finding context for: '{current_headline}' on {symbol}...")
        similar_events = self.retrieve_similar_events(current_headline, top_k=3)
        
        reports = []
        for ev in similar_events:
            reaction = self.study_market_reaction(symbol, ev["timestamp"])
            reports.append({
                "historical_event": ev,
                "market_reaction": reaction
            })
        return reports

if __name__ == "__main__":
    retriever = EventRetriever()
    # Test query
    sample_headline = "RBI cuts repo rate by 50 bps to boost economy"
    results = retriever.analyze_event_context(sample_headline, "BANKNIFTY")
    print("\n--- Event Analysis Test Results ---")
    for r in results:
        print(f"\nHeadline: {r['historical_event']['headline']}")
        print(f"Similarity Score: {r['historical_event']['similarity_score']:.4f}")
        print(f"Reaction Return: {r['market_reaction']['percent_return']:.4f}%")

import torch
from transformers import AutoTokenizer, AutoModel
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from src.config.config import config
from src.database.connection import SessionLocal, init_db
from src.database.models import NewsArticle

class EventPipeline:
    def __init__(self):
        print("[INFO] Initializing FinBERT model ('ProsusAI/finbert')...")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModel.from_pretrained("ProsusAI/finbert")
        print("[INFO] FinBERT model loaded successfully.")
        
        print("[INFO] Connecting to Qdrant...")
        self.qclient = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        self.collection_name = "news_events"
        print("[INFO] Qdrant connection initialized.")

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

    def run_pipeline(self):
        """Fetches unprocessed articles, embeds them, and indexes them in Qdrant."""
        init_db()
        db: Session = SessionLocal()
        
        # Get all unprocessed news articles
        unprocessed = db.query(NewsArticle).filter(NewsArticle.processed == False).all()
        
        if not unprocessed:
            print("[INFO] No new news articles to process.")
            db.close()
            return
            
        print(f"[INFO] Found {len(unprocessed)} new articles to process.")
        
        points = []
        for article in unprocessed:
            try:
                # Generate embedding for the headline
                embedding = self.get_embedding(article.headline)
                
                # Check for simple sentiment keywords as a lightweight fallback
                # (Can be upgraded to a full FinBERT classifier later)
                sentiment_label, sentiment_score = self.classify_sentiment(article.headline)
                
                # Update DB record with sentiment and processed status
                article.sentiment_label = sentiment_label
                article.sentiment_score = sentiment_score
                article.processed = True
                
                # Prepare Qdrant point
                point = qmodels.PointStruct(
                    id=article.id,
                    vector=embedding,
                    payload={
                        "id": article.id,
                        "headline": article.headline,
                        "url": article.url,
                        "source": article.source,
                        "timestamp": article.timestamp.isoformat(),
                        "event_type": article.event_type or "general_news",
                        "sector": article.sector or "general",
                        "country": article.country or "India",
                        "sentiment_label": sentiment_label,
                        "sentiment_score": sentiment_score
                    }
                )
                points.append(point)
                
            except Exception as e:
                print(f"[ERROR] Failed to process article ID {article.id}: {e}")
        
        if points:
            try:
                # Insert points into Qdrant vector database
                self.qclient.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                print(f"[SUCCESS] Upserted {len(points)} embeddings into Qdrant collection '{self.collection_name}'.")
                
                # Save processed status to PostgreSQL
                db.commit()
                print("[SUCCESS] PostgreSQL articles updated and committed.")
            except Exception as q_err:
                db.rollback()
                print(f"[ERROR] Qdrant upsert or DB commit failed: {q_err}")
        
        db.close()

    def classify_sentiment(self, text: str) -> tuple[str, float]:
        """Simple keyword-based financial sentiment classifier."""
        text_lower = text.lower()
        positive_keywords = ["growth", "gain", "rise", "surge", "up", "bull", "rally", "positive", "cut rate", "beat", "higher", "record", "jump"]
        negative_keywords = ["fall", "drop", "plunge", "down", "bear", "negative", "hike rate", "loss", "crash", "slump", "lower", "decline", "slowdown"]
        
        pos_count = sum(1 for word in positive_keywords if word in text_lower)
        neg_count = sum(1 for word in negative_keywords if word in text_lower)
        
        if pos_count > neg_count:
            return "POSITIVE", 0.5 + 0.1 * min(5, pos_count - neg_count)
        elif neg_count > pos_count:
            return "NEGATIVE", -0.5 - 0.1 * min(5, neg_count - pos_count)
        return "NEUTRAL", 0.0

if __name__ == "__main__":
    pipeline = EventPipeline()
    pipeline.run_pipeline()

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sqlalchemy.exc import OperationalError

from src.config.config import config
from src.database.connection import init_db
from src.database.connection import engine

def initialize_postgres():
    """Verify PostgreSQL connectivity and create tables."""
    print("[INFO] Initializing PostgreSQL database tables...")
    try:
        # Check connection
        with engine.connect() as conn:
            print("[INFO] PostgreSQL connection successful.")
        
        # Create tables
        init_db()
        print("[SUCCESS] PostgreSQL tables initialized.")
        return True
    except OperationalError as oe:
        print(f"[ERROR] Could not connect to PostgreSQL: {oe}")
        print("[ERROR] Please make sure PostgreSQL is running (e.g., via Docker Compose).")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error during PostgreSQL init: {e}")
        return False

def initialize_qdrant():
    """Verify Qdrant connectivity and create vector collections."""
    print("[INFO] Initializing Qdrant collections...")
    try:
        client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        
        # Test connection
        collections_res = client.get_collections()
        print("[INFO] Qdrant connection successful.")
        
        collection_name = "news_events"
        exists = False
        for c in collections_res.collections:
            if c.name == collection_name:
                exists = True
                break
        
        if exists:
            # Recreate collection to ensure it matches FinBERT 768 dimensions
            print(f"[INFO] Re-creating Qdrant collection '{collection_name}' to ensure 768 dimensions...")
            client.delete_collection(collection_name=collection_name)
            
        print(f"[INFO] Creating Qdrant collection: '{collection_name}' with 768-dimensional vectors for FinBERT...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(
                size=768,
                distance=qmodels.Distance.COSINE
            )
        )
        print(f"[SUCCESS] Qdrant collection '{collection_name}' created.")
        return True
    except Exception as e:
        print(f"[ERROR] Could not connect to Qdrant: {e}")
        print("[ERROR] Please make sure Qdrant is running (e.g., via Docker Compose).")
        return False

def main():
    print("==================================================")
    print("Database Initialization Script")
    print("==================================================")
    
    # Validate configuration
    config.validate()
    
    postgres_ok = initialize_postgres()
    qdrant_ok = initialize_qdrant()
    
    if postgres_ok and qdrant_ok:
        print("\n[SUCCESS] All databases initialized successfully!")
    else:
        print("\n[ERROR] Database initialization failed. Check connection settings.")

if __name__ == "__main__":
    main()

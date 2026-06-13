from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.config import config

# Create Engine
engine = create_engine(config.postgres_uri, pool_pre_ping=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()

def get_db():
    """Context manager for DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables based on declarative models."""
    Base.metadata.create_all(bind=engine)

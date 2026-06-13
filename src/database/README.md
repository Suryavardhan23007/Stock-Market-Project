# Database Connection & Schema Definitions

This folder holds database connection functions and ORM classes using SQLAlchemy.

## Components

- `connection.py`: Functions to fetch SQLAlchemy engines and session pools.
- `models.py`: Definitions of tables (SQLAlchemy base models) for:
  * OHLCV Candles (1-minute resolution)
  * Raw and parsed News Articles
  * Paper-trading ledger entries

## Usage

```python
from src.database.connection import get_db_session
from src.database.models import Base

# Bind to DB and run migrations / create tables
# (This happens during pipeline initialization)
```

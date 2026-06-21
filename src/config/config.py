import os
from pathlib import Path
from dotenv import load_dotenv

# Find the project root (.env location)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # Database Settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "tradingpassword")
    DB_NAME = os.getenv("DB_NAME", "stock_market_db")

    @property
    def postgres_uri(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Qdrant Settings
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

    # 5paisa Credentials
    FIVEPAISA_APP_NAME = os.getenv("FIVEPAISA_APP_NAME")
    FIVEPAISA_APP_SOURCE = os.getenv("FIVEPAISA_APP_SOURCE")
    FIVEPAISA_USER_ID = os.getenv("FIVEPAISA_USER_ID")
    FIVEPAISA_EMAIL = os.getenv("FIVEPAISA_EMAIL")
    FIVEPAISA_DOB = os.getenv("FIVEPAISA_DOB")
    FIVEPAISA_CLIENT_CODE = os.getenv("FIVEPAISA_CLIENT_CODE")
    FIVEPAISA_PASSWORD = os.getenv("FIVEPAISA_PASSWORD")
    FIVEPAISA_USER_KEY = os.getenv("FIVEPAISA_USER_KEY")
    FIVEPAISA_ENCRYPTION_KEY = os.getenv("FIVEPAISA_ENCRYPTION_KEY")
    FIVEPAISA_TOTP_SECRET = os.getenv("FIVEPAISA_TOTP_SECRET")
    FIVEPAISA_MPIN = os.getenv("FIVEPAISA_MPIN")

    # Gemini AI API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    @classmethod
    def validate(cls):
        """Validates that all critical variables are defined."""
        missing = []
        # Check database
        if not cls.DB_HOST or not cls.DB_USER:
            missing.append("PostgreSQL Connection Info")

        # 5paisa - warn if missing
        fivepaisa_keys = [
            "FIVEPAISA_APP_NAME", "FIVEPAISA_APP_SOURCE",
            "FIVEPAISA_USER_ID", "FIVEPAISA_CLIENT_CODE",
            "FIVEPAISA_PASSWORD", "FIVEPAISA_USER_KEY",
            "FIVEPAISA_ENCRYPTION_KEY", "FIVEPAISA_EMAIL", "FIVEPAISA_DOB"
        ]
        for key in fivepaisa_keys:
            if not os.getenv(key):
                missing.append(key)

        if missing:
            print(f"[WARN] Missing configuration variables: {', '.join(missing)}")
            print("[WARN] Please ensure you configure your .env file correctly.")
        else:
            print("[INFO] Configuration validated successfully.")

# Pre-initialized config instance
config = Config()

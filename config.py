import os

from dotenv import load_dotenv

load_dotenv()

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-only-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
ANALYZER_URL = os.getenv(
    "ANALYZER_URL",
    "https://mogestesema-safe-text-model.hf.space/analyze",
)
DEMO_API_KEY = os.getenv("DEMO_API_KEY", "")

import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

_raw_token = os.getenv("BOT_TOKEN") 
_raw_url_qdrant = os.getenv("QDRANT_URL")

if not _raw_token:
    raise ValueError("Error: BOT_TOKEN not found!")
if not _raw_url_qdrant: 
    raise ValueError("Error: QDRANT_URL not found!")

BOT_TOKEN: str = _raw_token
QDRANT_URL: str = _raw_url_qdrant
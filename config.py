import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

_raw_token = os.getenv("BOT_TOKEN") 
if not _raw_token:
    raise ValueError("Error: BOT_TOKEN not found!")

BOT_TOKEN: str = _raw_token
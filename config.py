import sys
from pathlib import Path
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
ENV = BASE_DIR / ".env"

class Settings(BaseSettings):
    bot_token: str
    qdrant_url: str
    embedding_service_url: str = "http://127.0.0.1:8000"
    admin_ids: set[int] = set()
    collection_name: str

    model_config = SettingsConfigDict(
        env_file=ENV,
        env_file_encoding="utf-8"
    )

try:
    config = Settings() # type: ignore
except ValidationError as e:
    print("\n[ENV ERROR] Перевірте файл .env. Відсутні обов'язкові змінні оточення:")

    for error in e.errors(): 
        field_name = str(error["loc"][0])
        print(f"    - {field_name.upper()}")

    print("\n>>> Stop.")
    sys.exit(1)
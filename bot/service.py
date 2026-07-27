from pathlib import Path
from aiogram import Bot
from core.database import add_item, search_items
from core.api_client import EmbeddingApiClient

BASE_DIR = Path(__file__).resolve().parent.parent
REF_DIR = BASE_DIR / "data" / "reference"

api_client = EmbeddingApiClient()

async def download_photo(file_id: str, bot: Bot) -> Path:
    destination_path = REF_DIR / f"{file_id}.jpg"
    destination_path.parent.mkdir(parents=True, exist_ok=True)    
    await bot.download(file = file_id, destination=destination_path)
    return destination_path

async def process_add_photo(file_id: str, bot: Bot):
    photo_path = await download_photo(file_id, bot)
    file_bytes = await bot.download(file=file_id)
    vector = await api_client.get_image_embedding(image_bytes=file_bytes.read()) # type: ignore
    await add_item(tg_file_id=file_id, vector=vector, photo_path=photo_path)

async def process_search_photo(file_id: str, bot: Bot):
    file = await bot.download(file=file_id)
    vector = await api_client.get_image_embedding(image_bytes=file.read()) # type: ignore
    results = await search_items(vector=vector)

    if not results or not results.points:
        return {"message": "🤷‍♂️ Нічого не знайдено. Спробуйте сфоткати з іншого ракурсу"}

    best_match = results.points[0] 

    if best_match.score < 0.65: 
        return {"message": "Схоже, таких предметів у нас немає"}

    if not best_match.payload:
        return {"message": "Об'єкт існує, але дані про нього відсутні"}

    title = best_match.payload.get("title", "Без назви")
    photo_path = best_match.payload.get("photo_path")

    caption_text = (
        f"Знайдено збіг! {best_match.score * 100:.1f}%\n"
        f"Предмет: **{title}**"
    )

    valid_photo = photo_path if photo_path and Path(photo_path).exists() else None
    if photo_path and not valid_photo:
        caption_text += "\n\n⚠️ Попередження: Фото оригіналу не знайдено на сервері."

    return {
        "message": caption_text,
        "photo_path": valid_photo
    }
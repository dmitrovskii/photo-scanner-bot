from pathlib import Path

from aiogram import Bot

from core.database import add_item, search_items
from core.api_client import EmbeddingApiClient
from core.storage import save_photo_bytes, get_photo_path

api_client = EmbeddingApiClient()

async def process_add_photo(file_id: str, bot: Bot):
    file_bytes = await bot.download(file=file_id)
    image_bytes = file_bytes.read() #type: ignore

    item_id, photo_path = save_photo_bytes(image_bytes=image_bytes)
    vector = await api_client.get_image_embedding(image_bytes=image_bytes) 
    await add_item(item_id=item_id, vector=vector, photo_path=photo_path)

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
    caption_text = (
        f"Знайдено збіг! {best_match.score * 100:.1f}%\n"
        f"Предмет: **{title}**"
    )

    temp_path = best_match.payload.get("photo_path")
    valid_photo: Path | None = None

    if isinstance(temp_path, str) and temp_path.strip():
        resolved_path = get_photo_path(temp_path)
        if resolved_path.exists():
            valid_photo = resolved_path

    if not valid_photo: 
        caption_text += "\n\n⚠️ Попередження: Фото оригіналу не знайдено на сервері."
    
    return {
        "message": caption_text,
        "photo_path": valid_photo
    }
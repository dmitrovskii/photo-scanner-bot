import asyncio
# TODO: ПРАВИЛЬНО НАЛАШТУВАТИ ІМПОРТИ, НАРАЗІ НЕ ГАРНО
from pathlib import Path
from aiogram import Router, Bot, F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from database import add_item, search_items
from models import get_image_embedding

from io import BytesIO
from PIL import Image

select_router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent
REF = BASE_DIR / "data" / "reference"

async def download_photo(file_id: str, bot: Bot, dest_path: Path = REF):
    destination_path = dest_path / f"{file_id}.jpg" # TODO: ВИНЕСТИ ЙОГО ОКРЕМО
    destination_path.parent.mkdir(parents=True, exist_ok=True)    
    
    await bot.download(
        file = file_id,
        destination=destination_path
    )
    return destination_path

# ADD EMBEDDING
async def add_embedding(file_id: str, bot: Bot):
    photo_path = REF / f"{file_id}.jpg" # TODO: ВИНЕСТИ ЙОГО ОКРЕМО
    image = Image.open(photo_path)
    vector = await asyncio.to_thread(get_image_embedding, image)
    await add_item(
        tg_file_id=file_id,
        vector=vector, 
        photo_path=photo_path
    )

# SEARCH EMBEDDING
async def search_embedding(image: Image.Image, bot: Bot):
    vector = await asyncio.to_thread(get_image_embedding, image)
    result = await search_items(vector=vector)
    return result

# MAIN SELECT ROUTER
@select_router.message(F.photo)
async def selection_menu(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder() # TODO: ДОДАТИ ПЕРЕВІРКУ ЮЗЕР ID ДЛЯ АДМІНІСТРАТОРІВ
    builder.add(
        InlineKeyboardButton(text="⬇️ Зберегти", callback_data="button_add"),
        InlineKeyboardButton(text="🔍 Знайти", callback_data="button_search")
    )
    if not message.photo: return 
    largest_photo = message.photo[-1] 
    await state.update_data(photo_id=largest_photo.file_id)
    await message.answer(
        text="Спіймав! Що робимо далі?",
        reply_markup=builder.as_markup()
    )

# BUTTON ADD
@select_router.callback_query(F.data == "button_add")
async def button_add(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    user_data = await state.get_data() # TODO: ВИНЕСТИ ОТРИМАННЯ STATE ОКРЕМО 
    file_id = user_data.get("photo_id")# TODO: ВИНЕСТИ ОТРИМАННЯ STATE ОКРЕМ
    if file_id:
        await download_photo(file_id=file_id, bot=bot)
        await add_embedding(file_id=file_id, bot=bot)
        await callback.message.answer("Фото було збережено!")
        await state.clear()
    else: 
        await callback.message.answer("Щось зламалося! Будь ласка, надішліть фото ще раз.")

# BUTTON SEARCH
@select_router.callback_query(F.data == "button_search")
async def button_search(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    
    user_data = await state.get_data()  # TODO: ВИНЕСТИ ОТРИМАННЯ STATE ОКРЕМО 
    file_id = user_data.get("photo_id") # TODO: ВИНЕСТИ ОТРИМАННЯ STATE ОКРЕМО 
    if file_id:

        buffer = BytesIO()
        await bot.download(file=file_id, destination=buffer)
        buffer.seek(0)
        image = Image.open(buffer)

        results = await search_embedding(image=image, bot=bot) 
        if results and results.points:
            best_match = results.points[0]

            if best_match.score < 0.60:
                await callback.message.answer("Схоже, таких предметів у нас немає.")
                return 

            if best_match.payload is not None:
                title = best_match.payload.get('title', 'Без назви') # TODO: ЗНАЧЕННЯ DEFAULT НЕ ПРАЦЮЄ
                photo_path = best_match.payload.get('photo_path')

                caption_text = (
                    f"Знайдено збіг! {best_match.score * 100:.1f}%\n"
                    f"Предмет: **{title}**"
                )

                if photo_path and Path(photo_path).exists():
                    await callback.message.answer_photo(
                        photo=FSInputFile(photo_path),
                        caption=caption_text,
                        parse_mode="Markdown"
                    )
                else: 
                    await callback.message.answer(caption_text + "\n\n⚠️ Попередження: Фото оригіналу не знайдено на сервері.")
            else: 
                await callback.message.answer(f"🤖 Знайдено об'єкт з ID `{best_match.id}`, але він поржній!")
        else:
            await callback.message.answer("🤷‍♂️ Нічого не знайдено. Спробуйте сфоткати з іншого ракурсу.")
    else: 
        await callback.message.answer("Щось зламалося! Будь ласка, надішліть фото ще раз.")
    
    # TODO: ЗАНАДТО БАГАТО IF ELSE
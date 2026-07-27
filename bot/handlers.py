from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.utils import text_to_callback, photo_to_callback
from bot.buttons import get_selection_buttons
from bot.service import process_add_photo, process_search_photo

select_router = Router()

@select_router.message(F.photo)
async def selection_menu(message: Message, state: FSMContext):
    if not message.photo:
        return
     
    largest_photo = message.photo[-1] 
    await state.update_data(photo_id=largest_photo.file_id)

    await message.answer(
        text="Спіймав! Що робимо далі?",
        reply_markup=get_selection_buttons()
    )

# BUTTON ADD
@select_router.callback_query(F.data == "button_add")
async def button_add(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    user_data = await state.get_data()
    file_id = user_data.get("photo_id")

    if not file_id:
        await text_to_callback(callback=callback, text="Щось зламалося! Будь ласка, надішліть фото ще раз.")
        return

    await process_add_photo(file_id, bot)
    await text_to_callback(callback=callback, text="Фото було збережено!")
    await state.clear()

# BUTTON SEARCH
@select_router.callback_query(F.data == "button_search")
async def button_search(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    user_data = await state.get_data()
    file_id = user_data.get("photo_id")

    if not file_id:
        await text_to_callback(callback=callback, text="Щось зламалося! Будь ласка, надішліть фото ще раз.")
        return
    
    result = await process_search_photo(file_id, bot)

    if result.get("photo_path"):
        await photo_to_callback(
            callback=callback,
            photo=FSInputFile(result["photo_path"]),
            caption=result["message"],
            parse_mode="Markdown"
        )
    else: 
        await text_to_callback(
            callback=callback,
            text=result["message"],
            parse_mode="Markdown"
        )
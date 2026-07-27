from aiogram.types import CallbackQuery, Message, InputFile

async def text_to_callback(callback: CallbackQuery, text: str, **kwargs):
    if isinstance(callback.message, Message):
        return await callback.message.answer(text, **kwargs)
    if callback.bot:
        return await callback.bot.send_message(chat_id=callback.from_user.id, text=text, **kwargs)

async def photo_to_callback(callback: CallbackQuery, photo: InputFile | str, **kwargs):
    if isinstance(callback.message, Message):
        return await callback.message.answer_photo(photo=photo,**kwargs)
    if callback.bot:
        return await callback.bot.send_photo(chat_id=callback.from_user.id, photo=photo, **kwargs)
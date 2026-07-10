from aiogram.types import CallbackQuery, Message

async def reply_to_callback(callback: CallbackQuery, text: str, **kwargs):
    if isinstance(callback.message, Message):
        return await callback.message.answer(text, **kwargs)
    if callback.bot:
        return await callback.bot.send_message(chat_id=callback.from_user.id, text=text, **kwargs)
    #TODO: Додати логування!
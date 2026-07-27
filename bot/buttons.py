from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_selection_buttons():
    builder = InlineKeyboardBuilder() 
    builder.add(
        InlineKeyboardButton(text="⬇️ Зберегти", callback_data="button_add"),
        InlineKeyboardButton(text="🔍 Знайти", callback_data="button_search")
    )
    return builder.as_markup()
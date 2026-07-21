import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from . import handlers
from database import init_db, close_db
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(handlers.select_router)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привіт. Я зберігаю та шукаю фотографії. Будь ласка, надсилайте по одній фотографії за раз.")

async def main():
    await init_db()
    print(">>> Start...")
    try:
        await dp.start_polling(bot)
    finally:
        print(">>> Stop.")
        await close_db()
if __name__ == "__main__":
    asyncio.run(main())
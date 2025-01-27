from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
import os
import asyncio
from dotenv import load_dotenv
from my_request import get_info
from my_db import *


load_dotenv()
BOT_API_KEY = os.getenv("BOT_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message):
    await message.answer("Добрый день! Чтобы начать пользоваться ботом введите секретный ключ")


@dp.message()
async def menu(message):
    if await check_user(message.chat.id):
        data = await get_info(message.text)
        error = data.get("error")
        print(error)
        if error:  
            await message.answer(str(error))
            
        else:
            formatted_data = "\n".join([f"{key}: {value}" for key, value in data["properties"].items()])
            await message.answer(formatted_data)

    elif message.text == SECRET_KEY:
        await allow_user(message.chat.id)
        await message.answer("Теперь можете проверить IMEI.\nВведите его:")


async def main():
    bot = Bot(token=BOT_API_KEY)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())

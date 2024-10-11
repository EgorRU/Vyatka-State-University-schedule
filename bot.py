from aiogram import Dispatcher, Bot
import asyncio

from user import router_user
from config import TOKEN


async def start_bot():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router_user)
    await dp.start_polling(bot)


def start_parsing():
    asyncio.run(start_bot())


if __name__ == "__main__":
    start_parsing()
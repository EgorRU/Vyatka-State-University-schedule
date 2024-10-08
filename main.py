import asyncio
from aiogram import Dispatcher, Bot
from multiprocessing import Process

from config import TOKEN
from parsing import start_parsing
from models import async_main
from user import router_user


async def main():
    await async_main()
    process = Process(target=start_parsing)
    process.start()
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router_user)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
from multiprocessing import Process
from aiogram import Dispatcher
import asyncio

from bot import schedule_router
from parsing import main as start_parsing
from config import bot


async def main():
    p1 = Process(target=start_parsing)
    p1.start()
    
    dp = Dispatcher()
    dp.include_router(schedule_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
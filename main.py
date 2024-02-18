from aiogram import Dispatcher
import asyncio

from config import bot
from handlers import schedule_router


dp = Dispatcher()


async def main():
    dp.include_router(schedule_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

from config import TOKEN_BOT
from handlers import schedule_router


bot = Bot(token=TOKEN_BOT)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    dp.include_router(schedule_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
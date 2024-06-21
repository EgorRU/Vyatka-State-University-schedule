from multiprocessing import Process
import asyncio

from bot import start_bot
from parsing import main as start_parsing


async def main():
    p1 = Process(target=start_parsing)
    p1.start()
    await start_bot()


if __name__ == '__main__':
    asyncio.run(main())
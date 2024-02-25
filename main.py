from multiprocessing import Process
import asyncio

from bot import main as start_bot
from parsing import main as start_parsing


async def main():
    p1 = Process(target=start_bot)
    p2 = Process(target=start_parsing)
    
    p1.start()
    p2.start()


if __name__ == '__main__':
    asyncio.run(main())
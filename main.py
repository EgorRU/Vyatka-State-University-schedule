import asyncio
from multiprocessing import Process

from parsing import start_parsing
from models import async_main
from bot import start_bot


async def main():
    await async_main()
    process = Process(target=start_parsing)
    process.start()
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
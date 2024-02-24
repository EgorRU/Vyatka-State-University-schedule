import asyncio
from multiprocessing import Process
from bot import main as start_bot
from parsing_pdf import main as start_parsing_pdf
from parsing_xlsx import main as start_parsing_xlsx


async def main():
    p1 = Process(target=start_bot)
    p2 = Process(target=start_parsing_pdf)
    p3 = Process(target=start_parsing_xlsx)
    
    p1.start()
    p2.start()
    p3.start()


if __name__ == '__main__':
    asyncio.run(main())
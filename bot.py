from aiogram import Router, Dispatcher
from aiogram.types import Message, CallbackQuery
from config import bot
from db import get_keyboard
from db import get_files
import asyncio


schedule_router = Router()


# ответ на текстовое сообщение
@schedule_router.message()
async def find_name_group(message: Message):
    # если нажата старт
    if message.text == "/start":
        await bot.send_message(message.chat.id, "Напишите учебную групу в виде: ЮРб-1, ЮР-1, Юрб 1 или ЮРб-1901-01-00")
    # иначе ищем группы
    else:
        # получение клавиатуры
        keyboard = await get_keyboard(message.text)
        # если группы нашлись
        if keyboard == None:
            await bot.send_message(message.chat.id, "Не могу найти такую группу, попробуйте ещё раз ввести группу\n\nВозможно, расписания для вашей группы ещё нет")
        else:
            await bot.send_message(message.chat.id, "Выберите группу", reply_markup=keyboard)


# отправка расписания по нажатию на кнопку
@schedule_router.callback_query()
async def get_schedule_for_group(callback: CallbackQuery):
    await callback.answer()
    # поиск id файлов
    id_files = await get_files(callback.data)
    # если есть файлы, отправляем
    if id_files:
        for file in id_files:
            await bot.send_document(callback.message.chat.id, file)
            await asyncio.sleep(1)
    else:
        await bot.send_message(callback.message.chat.id, "Расписания для вашей группы ещё нет")
        

async def start_bot():
    dp = Dispatcher()
    dp.include_router(schedule_router)
    await dp.start_polling(bot)


def main():
    asyncio.run(start_bot())
    

if __name__ == '__main__':
    asyncio.run(start_bot())
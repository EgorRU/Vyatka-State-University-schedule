from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
import os

from config import bot
from parsing import get_keyboard
from parsing import get_files



schedule_router = Router()


@schedule_router.message()
async def find_name_group(message: Message):
    if message.text == "/start":
        msg = await bot.send_message(message.chat.id, 'Напишите учебную групу в виде: ЮРб-1, ЮР-1, Юрб 1 или ЮРб-1901-01-00')
    else:
        msg = await bot.send_message(message.chat.id, 'Немного подождите... ищем учебные группы в базе данных')
        keyboard = await get_keyboard(message.text)
        if keyboard == None:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text='Не могу найти такую группу, попробуйте ещё раз ввести группу')
        else:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="Выберите группу", reply_markup=keyboard)


#получение нажатия на кнопку и отправка расписания
@schedule_router.callback_query()
async def get_schedule_for_group(callback: CallbackQuery):
    msg = await bot.send_message(chat_id=callback.message.chat.id, text='Немного подождите... ищем расписание в базе данных')
    await callback.answer()
    list_files = await get_files(callback.data)
    await bot.delete_message(callback.message.chat.id, msg.message_id)
    if list_files:
        for file in list_files:
            input_file = FSInputFile(file)
            await bot.send_document(callback.message.chat.id, input_file)
            os.remove(file)
    else:
        await bot.send_message(callback.message.chat.id, 'Сервер не доступен')
    
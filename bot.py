# from typing import Callable, Awaitable, Dict, Any
# from aiogram import Router, Dispatcher, Bot, F
# from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, TelegramObject
# from aiogram import BaseMiddleware
# import asyncio

# from db import create_db
# from db import get_list_schedule
# from db import get_keyboard_and_text
# from db import update_users
# from config import TOKEN

# bot = Bot(TOKEN)
 

# # мидлварь - при апдейте боту обновляются данные пользователей
# class DbMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any]
#     ) -> Any:
#         await update_users(event)
#         return await handler(event, data)
    

# # навешиваем мидлварь на сообщения и на кнопки
# schedule_router = Router()
# schedule_router.message.middleware(DbMiddleware())
# schedule_router.callback_query.middleware(DbMiddleware())



# # первое сообщение
# @schedule_router.message()
# async def start(message: Message):
    


# # выбор нужной кнопки для получения расписания
# @schedule_router.callback_query(F.data.startswith("Выбор"))
# async def find_data(callback: CallbackQuery):
#     keyboard, text = await get_keyboard_and_text(callback.data[5:])
#     await callback.message.answer(text, reply_markup=keyboard)
#     await callback.answer()

   
# # Обновление клавиатуры
# @schedule_router.callback_query(F.data.startswith("Обновить"))
# async def update_keyboard(callback: CallbackQuery):
#     keyboard, text = await get_keyboard_and_text(callback.data[8:])
#     try:
#         if callback.message.text != text:
#             await callback.message.edit_text(text, reply_markup=keyboard)
#     except:
#         pass
#     await callback.answer()
    

# # получение расписания на Сегодня, Завтра, Послезавтра
# @schedule_router.callback_query(F.data.startswith("Сегод")|F.data.startswith("Завтр")|F.data.startswith("После"))
# async def find_today(callback: CallbackQuery):
#     keyboard, text = await get_keyboard_and_text(callback.data[5:], callback.data[:5])
#     if keyboard != None:
#         text += "\nРасписание может быть изменено. Узнавайте актуальное расписание новым запросом."
#     # пробуем отредактировать старую клавиатуру
#     try:
#         if callback.message.text != text:
#             await callback.message.edit_text(text, reply_markup=keyboard)
#     # если ошибка, то отправляем текст, а потом новую клавиатуру
#     except:
#         while len(text)>4090:
#             await callback.message.answer(text[:4090])
#             text = text[4090:]
#         await callback.message.answer(text, reply_markup=keyboard)
#     await callback.answer()


# # получение расписания на конкретную неделю
# @schedule_router.callback_query(F.data.startswith("Неделя"))
# async def find_week(callback: CallbackQuery):
#     keyboard, text = await get_keyboard_and_text(callback.data[16:], callback.data[:16])
#     if keyboard != None:
#         text += '\nРасписание может быть изменено. Узнавайте актуальное расписание новым запросом.'
#     # пробуем отредактировать старую клавиатуру
#     try:
#         if callback.message.text != text:
#             await callback.message.edit_text(text, reply_markup=keyboard)
#     # если ошибка, то отправляем текст, а потом новую клавиатуру
#     except:
#         while len(text)>4090:
#             await callback.message.answer(text[:4090])
#             text = text[4090:]
#         await callback.message.answer(text)
#         await callback.message.answer(f"Фильтры расписания для {callback.data[16:]}", reply_markup=keyboard)
#     await callback.answer()


# # получение расписания на весь доступный промежуток
# @schedule_router.callback_query(F.data.startswith("Всё"))
# async def find_all(callback: CallbackQuery):
#     keyboard, text = await get_keyboard_and_text(callback.data[23:], callback.data[:23])
#     if keyboard != None:
#         text += '\nРасписание может быть изменено. Узнавайте актуальное расписание новым запросом.'
#     # пробуем отредактировать старую клавиатуру
#     try:
#         if callback.message.text != text:
#             await callback.message.edit_text(text, reply_markup=keyboard)
#     # если ошибка, то отправляем текст, а потом новую клавиатуру
#     except:
#         while len(text)>4090:
#             await callback.message.answer(text[:4090])
#             text = text[4090:]
#         await callback.message.answer(text)
#         await callback.message.answer(f"Фильтры расписания для {callback.data[23:]}", reply_markup=keyboard)
#     await callback.answer()
    

    
from typing import Callable, Awaitable, Dict, Any
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, TelegramObject
from aiogram import BaseMiddleware

from dbrequests import update_user

class DbMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        await update_user(event)
        return await handler(event, data)
    

router_user = Router()
router_user.message.middleware(DbMiddleware())
router_user.callback_query.middleware(DbMiddleware())


@router_user.message()
async def test(message: Message):
    # если нажата старт`
    if message.text == "/start":
        msg = '➡️ Чтобы узнать расписание группы, введите группу, например, ПОДб-1, ПОД-1, ПОДб 1, ПОД 1, ПОДб-1901-01-00\n\n➡️ Чтобы узнать расписание преподавателя, введите только его фамилию, например, Иванов\n\n➡️ Чтобы узнать расписание аудитории, введите название аудитории, например, 1-100'
        await message.answer(msg)
    # # иначе ищем расписание
    # else:
    #     # получение листа с возможными кнопками для выбора
    #     list_schedule = await get_list_schedule(message.text)
        
    #     # если расписание НЕ нашлось(кнопок нет)
    #     if len(list_schedule) == 0:
    #         await message.answer("Группа/преподаватель/аудитория не найден(а)\n\nПроверьте корректность данных и повторите попытку\n\nВозможно, расписание по Вашему запросу отсутствует")
        
    #     # если по запросу найдена 1 группа / 1 препод / 1 кабинет, то сразу выводи расписание
    #     elif len(list_schedule) == 1:
    #         # формируем клавиатуру по одной возможной кнопке
    #         keyboard, text = await get_keyboard_and_text(list_schedule[0])
    #         # отправляем сообщение с кнопкой
    #         await message.answer(text, reply_markup=keyboard)
        
    #     # если кнопок много, то просим выбрать что-то одно
    #     else:
    #         # делаем кнопки в два рядя
    #         lenght = int(len(list_schedule)/2)
    #         list_keyboard_buttons = []
    #         # формируем строки
    #         for i in range(lenght):
    #             button1 = InlineKeyboardButton(text=f'{list_schedule[i*2]}', callback_data=f'Выбор{list_schedule[i*2]}')
    #             button2 = InlineKeyboardButton(text=f'{list_schedule[i*2+1]}', callback_data=f'Выбор{list_schedule[i*2+1]}')
    #             list_keyboard_buttons.append([button1, button2])
    #         # если было нечётное кол-во кнопок, то последнюю добавляем одну
    #         if len(list_schedule) % 2 == 1:
    #             button1 = InlineKeyboardButton(text=f'{list_schedule[-1]}', callback_data=f'Выбор{list_schedule[-1]}')
    #             list_keyboard_buttons.append([button1])
    #         keyboard = InlineKeyboardMarkup(inline_keyboard=list_keyboard_buttons)
    #         await message.answer("Выберите группу/преподавателя/аудиторию", reply_markup=keyboard)
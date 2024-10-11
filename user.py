from aiogram import Router, F, BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, TelegramObject

from typing import Callable, Awaitable, Dict, Any

import logging
import traceback

from dbrequests import update_user
from kb import get_list_schedule, get_keyboard_and_text


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
        msg = '➡️ Чтобы узнать расписание группы, введите группу, например, ПОДб-1, ПОД-1, ПОДб 1, ПОД 1, ПОДб-1901-01-00\n\n➡️ Чтобы узнать расписание преподавателя, введите фамилию или фамилию с инициалами, например, Иванов или Иванов А.А.\n\n➡️ Чтобы узнать расписание аудитории, введите название аудитории, например, 16-415'
        await message.answer(msg)
    # иначе ищем расписание
    else:
        # получение листа с возможными кнопками для выбора
        list_schedule = await get_list_schedule(message.text)
        
        # если расписание НЕ нашлось(кнопок нет)
        if len(list_schedule) == 0:
            await message.answer("Группа/преподаватель/аудитория не найден(а)\n\nПроверьте корректность данных и повторите попытку\n\nВозможно, расписание по Вашему запросу отсутствует")
        
        # если по запросу найдена 1 группа / 1 препод / 1 кабинет, то сразу выводи расписание
        elif len(list_schedule) == 1:
            # формируем клавиатуру по одной возможной кнопке
            keyboard, text = await get_keyboard_and_text(list_schedule[0])
            # отправляем сообщение с кнопкой
            await message.answer(text, reply_markup=keyboard)
        
        # если кнопок много, то просим выбрать что-то одно
        else:
            # делаем кнопки в два рядя
            lenght = int(len(list_schedule)/2)
            list_keyboard_buttons = []
            # формируем строки
            for i in range(lenght):
                button1 = InlineKeyboardButton(text=f'{list_schedule[i*2]}', callback_data=f'Выбор{list_schedule[i*2]}')
                button2 = InlineKeyboardButton(text=f'{list_schedule[i*2+1]}', callback_data=f'Выбор{list_schedule[i*2+1]}')
                list_keyboard_buttons.append([button1, button2])
            # если было нечётное кол-во кнопок, то последнюю добавляем одну
            if len(list_schedule) % 2 == 1:
                button = InlineKeyboardButton(text=f'{list_schedule[-1]}', callback_data=f'Выбор{list_schedule[-1]}')
                list_keyboard_buttons.append([button])
            keyboard = InlineKeyboardMarkup(inline_keyboard=list_keyboard_buttons)
            await message.answer("Выберите группу/преподавателя/аудиторию", reply_markup=keyboard)


# выбор нужной кнопки для получения расписания
@router_user.callback_query(F.data.startswith("Выбор"))
async def find_data(callback: CallbackQuery):
    keyboard, text = await get_keyboard_and_text(callback.data[5:])
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()

   
# Обновление клавиатуры
@router_user.callback_query(F.data.startswith("Обновить"))
async def update_keyboard(callback: CallbackQuery):
    keyboard, text = await get_keyboard_and_text(callback.data[8:])
    try:
        if callback.message.text != text:
            await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"{e}")
        logging.error(traceback.format_exc())
    await callback.answer()
    

# получение расписания на Сегодня, Завтра, Послезавтра
@router_user.callback_query(F.data.startswith("Сегод")|F.data.startswith("Завтр")|F.data.startswith("После"))
async def find_today(callback: CallbackQuery):
    keyboard, text = await get_keyboard_and_text(callback.data[5:], callback.data[:5])
    if keyboard != None:
        text += "\nРасписание может быть изменено. Узнавайте актуальное расписание новым запросом."
    # пробуем отредактировать старую клавиатуру
    try:
        if callback.message.text != text:
            await callback.message.edit_text(text, reply_markup=keyboard)
    # если ошибка, то отправляем текст, а потом новую клавиатуру
    except:
        while len(text)>4090:
            await callback.message.answer(text[:4090])
            text = text[4090:]
        await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


# получение расписания на конкретную неделю
@router_user.callback_query(F.data.startswith("Неделя"))
async def find_week(callback: CallbackQuery):
    keyboard, text = await get_keyboard_and_text(callback.data[16:], callback.data[:16])
    if keyboard != None:
        text += '\nРасписание может быть изменено. Узнавайте актуальное расписание новым запросом.'
    # пробуем отредактировать старую клавиатуру
    try:
        if callback.message.text != text:
            await callback.message.edit_text(text, reply_markup=keyboard)
    # если ошибка, то отправляем текст, а потом новую клавиатуру
    except:
        while len(text)>4090:
            await callback.message.answer(text[:4090])
            text = text[4090:]
        await callback.message.answer(text)
        await callback.message.answer(f"Фильтры расписания для {callback.data[16:]}", reply_markup=keyboard)
    await callback.answer()


# получение расписания на весь доступный промежуток
@router_user.callback_query(F.data.startswith("Всё"))
async def find_all(callback: CallbackQuery):
    keyboard, text = await get_keyboard_and_text(callback.data[23:], callback.data[:23])
    if keyboard != None:
        text += '\nРасписание может быть изменено. Узнавайте актуальное расписание новым запросом.'
    # пробуем отредактировать старую клавиатуру
    try:
        if callback.message.text != text:
            await callback.message.edit_text(text, reply_markup=keyboard)
    # если ошибка, то отправляем текст, а потом новую клавиатуру
    except:
        while len(text)>4090:
            await callback.message.answer(text[:4090])
            text = text[4090:]
        await callback.message.answer(text)
        await callback.message.answer(f"Фильтры расписания для {callback.data[23:]}", reply_markup=keyboard)
    await callback.answer()
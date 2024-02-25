from aiogram import Router, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import asyncio

from config import bot
from db import get_list_schedule
from db import get_date_for_valid_text


schedule_router = Router()


# получение клавиатуры для группы/преподавателя/кабинета
async def get_keyboard(valid_text):
    text = f"Фильтры расписания для {valid_text}"

    button0 = InlineKeyboardButton(text=f'{valid_text}', callback_data=f'Обновить {valid_text}')

    button1 = InlineKeyboardButton(text='Сегодня', callback_data=f'Сегодня {valid_text}')
    button2 = InlineKeyboardButton(text='Завтра', callback_data=f'Завтра {valid_text}')
    button3 = InlineKeyboardButton(text='Послезавтра', callback_data=f'Послезавтра {valid_text}')
    
    inline_keyboard = [[button0],[button1, button2, button3]]
    
    # получение всех дат
    date = await get_date_for_valid_text(valid_text)
    
    # формирование кнопок с неделями
    last_date = date[-1]
    current_date = datetime.date.today()
    
    # понедельник текущей недели
    first_day_week = current_date - datetime.timedelta(days=current_date.weekday())
    # воскресение текущей недели
    last_day_week = first_day_week + datetime.timedelta(days=6)
    
    # пока можно добавлять две недели - добавляем
    while first_day_week + datetime.timedelta(days=7) < last_date:
        button1 = InlineKeyboardButton(text=f'{first_day_week.day}-{last_day_week.day}.{last_day_week.month}| Неделя', callback_data=f'Неделя {first_day_week} {last_day_week} {valid_text}')
        first_day_week += datetime.timedelta(days=7)
        last_day_week += datetime.timedelta(days=7)

        button2 = InlineKeyboardButton(text=f'{first_day_week.day}-{last_day_week.day}.{last_day_week.month}| Неделя', callback_data=f'Неделя {first_day_week} {last_day_week} {valid_text}')
        first_day_week += datetime.timedelta(days=7)
        last_day_week += datetime.timedelta(days=7)
        
        inline_keyboard.append([button1, button2])
        
    # добавялем ласт неделю
    if first_day_week < last_date:
        button = InlineKeyboardButton(text=f'{first_day_week.day}-{last_day_week.day}.{last_day_week.month}| Неделя', callback_data=f'Неделя {first_day_week} {last_day_week} {valid_text}')
        inline_keyboard.append([button])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard, text


# обновление клавиатуры и раписания, получение расписания
async def update_keyboard(valid_data, period):
    return None, "test"


# первое сообщение
@schedule_router.message()
async def start(message: Message):
    # если нажата старт
    if message.text == "/start":
        msg = '➡️ Чтобы узнать расписание группы, введите группу, например, ЮРб-1, ЮР-1, Юрб 1, ЮРб-1901-01-00\n\n➡️ Чтобы узнать расписание преподавателя, введите только его фамилию, например, Иванов\n\n➡️ Чтобы узнать расписание аудитории, введите название аудитории, например, 16-415'
        await message.answer(msg)
    # иначе ищем расписание
    else:
        # получение листа с возможными кнопками для выбора
        list_schedule = await get_list_schedule(message.text)
        
        # если расписание НЕ нашлось(кнопок нет)
        if len(list_schedule) == 0:
            await message.answer("Группа/преподаватель/аудитория не найден(а)\n\nПроверьте корректность данных и повторите попытку\n\nВозможно, расписание по Вашему запросу отсутствует")
        
        # если по запросу найдена только одна группа или один препод, то сразу выводи расписание
        elif len(list_schedule) == 1:
            # формируем клавиатуру по одной возможной кнопке
            keyboard, text = await get_keyboard(list_schedule[0])
            # отправляем сообщение с кнопкой
            await message.answer(text, reply_markup=keyboard)
        
        # если кнопок много, то просим выбрать что-то одно
        else:
            # делаем кнопки в два рядя
            lenght = int(len(list_schedule)/2)
            list_keyboard_buttons = []
            # формируем строки
            for i in range(lenght):
                button1 = InlineKeyboardButton(text=f'{list_schedule[i*2]}', callback_data=f'Выбор {list_schedule[i*2]}')
                button2 = InlineKeyboardButton(text=f'{list_schedule[i*2+1]}', callback_data=f'Выбор {list_schedule[i*2+1]}')
                list_keyboard_buttons.append([button1, button2])
            # если было нечётное кол-во кнопок, то последнюю добавляем одну
            if len(list_schedule) % 2 == 1:
                button1 = InlineKeyboardButton(text=f'{list_schedule[-1]}', callback_data=f'Выбор {list_schedule[-1]}')
                list_keyboard_buttons.append([button1])
            keyboard = InlineKeyboardMarkup(inline_keyboard=list_keyboard_buttons)
            await message.answer("Выберите группу/преподавателя/аудиторию", reply_markup=keyboard)


# выбор нужной кнопки для получения расписания
@schedule_router.callback_query(F.data.startswith("Выбор"))
async def find_data(callback: CallbackQuery):
    keyboard, text = await get_keyboard(callback.data[6:])
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()

    
# получение расписания на Сегодня
@schedule_router.callback_query(F.data.startswith("Сегодня"))
async def find_today(callback: CallbackQuery):
    keyboard, text = await update_keyboard(F.data[8:], "Сегодня")
    await callback.message.edit_text(text, reply_markup=keyboard)





async def start_bot():
    dp = Dispatcher()
    dp.include_router(schedule_router)
    await dp.start_polling(bot)


def main():
    asyncio.run(start_bot())
    

if __name__ == '__main__':
    asyncio.run(start_bot())
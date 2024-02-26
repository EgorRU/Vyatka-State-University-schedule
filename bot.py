from aiogram import Router, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import BaseFilter
import datetime
import asyncio

from config import bot
from db import get_list_schedule
from db import get_date_for_valid_text
from db import get_schedule_by_date


schedule_router = Router()


class FilterWeek(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        return callback.data[:4].isdigit() and callback.data[4]=="-" and callback.data[5:6].isdigit()
    

# получение клавиатуры для группы/преподавателя/кабинета
async def get_keyboard(valid_text, period=None):
    button0 = InlineKeyboardButton(text=f'{valid_text}', callback_data=f'Обновить{valid_text}')
    
    button1 = InlineKeyboardButton(text='Сегодня', callback_data=f'Сегод{valid_text}')
    button2 = InlineKeyboardButton(text='Завтра', callback_data=f'Завтр{valid_text}')
    button3 = InlineKeyboardButton(text='Послезавтра', callback_data=f'После{valid_text}')
    
    inline_keyboard = [[button0],[button1, button2, button3]]
    
    # получение всех дат
    date = await get_date_for_valid_text(valid_text)
    
    # формирование кнопок с неделями
    last_date = date[-1]
    current_date = datetime.date.today()
    
    # понедельник текущей недели
    first_day_week = current_date - datetime.timedelta(days=current_date.weekday())
    if current_date.weekday()>=5:
        first_day_week += datetime.timedelta(days=7)
    # воскресение текущей недели
    last_day_week = first_day_week + datetime.timedelta(days=6)
    
    # пока можно добавлять две недели - добавляем
    while first_day_week + datetime.timedelta(days=7) < last_date:
        button1 = InlineKeyboardButton(text=f'{first_day_week.day}.{first_day_week.month}-{last_day_week.day}.{last_day_week.month}| Неделя', callback_data=f'{first_day_week}{last_day_week}{valid_text}')
        first_day_week += datetime.timedelta(days=7)
        last_day_week += datetime.timedelta(days=7)

        button2 = InlineKeyboardButton(text=f'{first_day_week.day}.{first_day_week.month}-{last_day_week.day}.{last_day_week.month}| Неделя', callback_data=f'{first_day_week}{last_day_week}{valid_text}')
        first_day_week += datetime.timedelta(days=7)
        last_day_week += datetime.timedelta(days=7)
        
        inline_keyboard.append([button1, button2])
        
    # добавялем ласт неделю
    if first_day_week < last_date:
        button = InlineKeyboardButton(text=f'{first_day_week.day}.{first_day_week.month}-{last_day_week.day}.{last_day_week.month}| Неделя', callback_data=f'{first_day_week}{last_day_week}{valid_text}')
        inline_keyboard.append([button])
    
    # формируем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    
    # если периода нет, то просто изначальная клавиарута
    if period == None:
        text = f"Фильтры расписания для {valid_text}"
    # иначе ищем раписание по выбранной дате и выводим в виде текста
    else:
        text = await get_schedule_by_date(valid_text, period)
    return keyboard, text


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
                button1 = InlineKeyboardButton(text=f'{list_schedule[i*2]}', callback_data=f'C{list_schedule[i*2]}')
                button2 = InlineKeyboardButton(text=f'{list_schedule[i*2+1]}', callback_data=f'C{list_schedule[i*2+1]}')
                list_keyboard_buttons.append([button1, button2])
            # если было нечётное кол-во кнопок, то последнюю добавляем одну
            if len(list_schedule) % 2 == 1:
                button1 = InlineKeyboardButton(text=f'{list_schedule[-1]}', callback_data=f'C{list_schedule[-1]}')
                list_keyboard_buttons.append([button1])
            keyboard = InlineKeyboardMarkup(inline_keyboard=list_keyboard_buttons)
            await message.answer("Выберите группу/преподавателя/аудиторию", reply_markup=keyboard)


# выбор нужной кнопки для получения расписания
@schedule_router.callback_query(F.data.startswith("C"))
async def find_data(callback: CallbackQuery):
    keyboard, text = await get_keyboard(callback.data[1:])
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()

   
# Обновление клавиатуры
@schedule_router.callback_query(F.data.startswith("Обновить"))
async def find_today(callback: CallbackQuery):
    keyboard, text = await get_keyboard(callback.data[8:])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except:
        pass
    await callback.answer("Обновлено")
    

# получение расписания на Сегодня, Завтра, Послезавтра
@schedule_router.callback_query(F.data.startswith("Сегод")|F.data.startswith("Завтр")|F.data.startswith("После"))
async def find_today(callback: CallbackQuery):
    keyboard, text = await get_keyboard(callback.data[5:], callback.data[:5])
    text += '\nРасписание может быть изменено. Узнавайте актуальное расписание новым запросом.'
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except:
        pass
    await callback.answer()


# получение расписания на неделю
@schedule_router.callback_query(FilterWeek())
async def find_today(callback: CallbackQuery):
    keyboard, text = await get_keyboard(callback.data[20:], callback.data[:20])
    text += '\nРасписание может быть изменено. Узнавайте актуальное расписание новым запросом.'
    try:
        await callback.message.answer(text)
    except:
        index = text.find("➡️ Вторник |")
        await callback.message.answer(text[:index])
        text = text[index:]
        
        index = text.find("➡️ Среда |")
        await callback.message.answer(text[:index])
        text = text[index:]

        index = text.find("➡️ Четверг |")
        await callback.message.answer(text[:index])
        text = text[index:]
        
        index = text.find("➡️ Пятница |")
        await callback.message.answer(text[:index])
        text = text[index:]
        
        index = text.find("➡️ Суббота |")
        await callback.message.answer(text[:index])
        text = text[index:]
        
        await callback.message.answer(text)
        
    await callback.message.answer(f"Фильтры расписания для {callback.data[20:]}", reply_markup=keyboard)
    await callback.answer()


async def start_bot():
    dp = Dispatcher()
    dp.include_router(schedule_router)
    await dp.start_polling(bot)


def main():
    asyncio.run(start_bot())
    

if __name__ == '__main__':
    asyncio.run(start_bot())
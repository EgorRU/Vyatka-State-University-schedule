from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from parsing_schedule import ScheduleGroups
from parsing_schedule import FilterGroup
from parsing_schedule import get_keyboard
from parsing_schedule import get_schedule


schedule_router = Router()

#команда старт
@schedule_router.message(F.text.startswith("/start"), StateFilter(None))
async def start(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена', callback_data='Отмена')]])
    await message.answer("Напишите учебную групу в виде: ЮРб-1, ЮР-1, Юрб 1 или ЮРб-1901-01-00", reply_markup=keyboard)
    await state.set_state(ScheduleGroups.name_group)


#команда отмена
@schedule_router.callback_query(ScheduleGroups.name_group, F.data == 'Отмена')
async def cancel_state(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass
    await callback.answer()
    

#получение имени группы и отправка клавиатуры с предполагаемой группой для выбора
@schedule_router.message(ScheduleGroups.name_group)
async def find_name_group(message: Message, state: FSMContext):
    if message.text == "/start":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена', callback_data='Отмена')]])
        await message.answer("Напишите учебную групу в виде: ЮРб-1, ЮР-1, Юрб 1 или ЮРб-1901-01-00", reply_markup=keyboard)
        await state.set_state(ScheduleGroups.name_group)
    else:
        await message.answer("Немного подождите... ищем учебные группы в базе данных")
        keyboard = await get_keyboard(message.text)
        if keyboard==None:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена', callback_data='Отмена')]])
            await message.answer("Не могу найти такую группу, попробуйте ещё раз ввести группу", reply_markup=keyboard)
        else:
            await message.answer("Выберите группу", reply_markup=keyboard)


#получение нажатия на кнопку и отправка расписания
@schedule_router.callback_query()
async def get_schedule_for_group(callback):
    await callback.message.answer("Немного подождите... ищем раписание для этой учебной группы")
    await callback.answer()
    name_group = callback.data
    url = await get_schedule(name_group)
    if url != None:
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer(url)
    else:
        await callback.message.answer("Сервер не доступен")
    await callback.answer()
    
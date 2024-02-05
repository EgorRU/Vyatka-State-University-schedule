from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import  BaseFilter
from bs4 import BeautifulSoup
import requests
import re


#ловим сообщение с названием группы
class ScheduleGroups(StatesGroup):
    name_group = State()
  

#фильтрация, что была нажата кнопка именна с названием группы
class FilterGroup(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        await callback.message.answer("Немного подождите... ищем раписание для этой учебной группы")
        list_groups = await get_name_group()
        return callback.data in list_groups


#получаем список всех групп
async def get_name_group():
    try:
        response = requests.get("https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie-zanyatiy-dlya-studentov.html")
        soup = BeautifulSoup(response.text, 'lxml')
        list_groups = soup.find_all('div', class_='grpPeriod')
        new_list_groups = [value.text.strip() for value in list_groups]
        list_groups = list(set(new_list_groups))
    except:
        return
    return list_groups


async def get_keyboard(input_group):
    #поиск всех групп на сайте
    list_groups = await get_name_group()
    #обработка введённой строки
    list_input_groups = []
    #добавляем необработанную группу в массив
    list_input_groups.append(input_group.lower())
    input_group = input_group.lower()
    #режем строку на куски, где разделителем является тире
    if input_group.find("-") > 0:
        input_split_dash = input_group.split("-")
        input_split_dash = [value.strip() for value in input_split_dash]
        if len(input_split_dash)>1:
            list_symbol = ['б', 'м', 'а', 'с']
            for i in list_symbol:
                list_input_groups.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
            list_input_groups.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
        else:
            list_input_groups.append(f"{input_split_dash[0]}")
    #если есть пробелы, то режем строку на куски по пробелам
    if any(char.isspace () for char in input_group):
        input_split_dash = input_group.split(" ")
        input_split_dash = [value.strip() for value in input_split_dash]
        list_symbol = ['б', 'м', 'а', 'с']
        for i in list_symbol:
            list_input_groups.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
        list_input_groups.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
    #убираем повторки
    list_input_groups = list(set(list_input_groups))
    #формирование клавиатуры
    list_keyboard_buttons = []
    for group in list_groups:
        for input_group in list_input_groups:
            if input_group in group.lower():
                list_keyboard_buttons.append([InlineKeyboardButton(text=f'{group}', callback_data=f'{group}')])
    if len(list_keyboard_buttons)>0:
        return InlineKeyboardMarkup(inline_keyboard=list_keyboard_buttons)
    return None


async def get_schedule(name_group):
    try:
        response = requests.get("https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie-zanyatiy-dlya-studentov.html")
        text = response.text
        cnt = 0
        for m in re.finditer(name_group, text):
            cnt += 1
            if cnt == 2:
                index = m.start()
                text = text[index:]
        #поиск ссылки
        index = text.find("href")
        text = text[index+6:]
        index = 0
        url = "https://www.vyatsu.ru"
        while text[index]!="\"":
            url += text[index]
            index += 1
    except:
        return None
    return url

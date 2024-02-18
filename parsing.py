from typing import Set
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bs4 import BeautifulSoup
from requests.models import Response
import requests
import datetime


user_agent: dict = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36'}
url1: str = "https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie-zanyatiy-dlya-studentov.html"
url2: str = "https://www.vyatsu.ru/internet-gazeta/raspisanie-sessiy-obuchayuschihsya-na-2016-2017-uc.html"


# получение данных с сайта
async def get_content(url: str) -> Response | None:
    try:
        response = requests.get(url, headers=user_agent)
        return response
    except:
        pass


# получение кортежа групп
async def get_name_groups(response: Response) -> Set[str]:
    soup = BeautifulSoup(response.text, 'lxml')
    set_groups = soup.find_all('div', class_='grpPeriod')
    set_groups = [value.text.strip() for value in set_groups]
    return set(set_groups)


# получение ссылок на расписание
async def get_url_schedule(response: Response, set_groups: Set[str]) -> dict[str, Set[str]]:
    schedule: dict[str, Set[str]] = {}
    for name_group in set_groups:
        text = response.text
        # ищем название группы
        index = text.find(name_group)
        
        # всё до названия группы удаляем
        text = text[index:]    
        
        index_begin = text.find("listPeriod")  #ищем начало ссылок на расписание
        text = text[index_begin:]     #удаляем текст, до начала ссылок
        index_end = text.find("</div>")    #ищем конец, где ссылки заканчиваются
        
        new_text = text[index_begin:index_end]  # блок с ссылками
        index = new_text.find("href")    # поиск первой ссылки
        new_text = new_text[index+6:]
        
        # пока есть ссылки в 1 семестре
        while index>0:
            index_temp = 0
            url = "https://www.vyatsu.ru"
            
            # формируем url
            while new_text[index_temp]!="\"":
                url += new_text[index_temp]
                index_temp += 1
                
            # добаляем только свежее расписание
            temp_url = url[:-4]
            year_end = int(temp_url[-4:])
            month_end = int(temp_url[-6:-4])
            day_end = int(temp_url[-8:-6])
            date = datetime.date(year_end, month_end, day_end)
            current_date = datetime.date.today()
            
            # если текущая дата больше, чем последний день с раписанием, то удаляем ссылку
            if current_date < date:
                # добавляем ссылку в словарь
                if name_group in schedule:
                    schedule[name_group].append(url)
                else:
                    schedule[name_group] = [url]
                    
            # переемещаем индекс вперёд
            new_text = new_text[index_temp:]
            index = new_text.find("href")
            new_text = new_text[index+6:]
                
        text = text[index_end:] 
        
        # ищем название группы
        index = text.find(name_group) 
        
        # всё до названия группы удаляем
        text = text[index:] 
        
        index = text.find("listPeriod")  #ищем начало ссылок на расписание
        text = text[index_begin:]     #удаляем текст, до начала ссылок
        index_end = text.find("</div>")    #ищем конец, где ссылки заканчиваются
        
        new_text = text[index_begin:index_end]  # блок с ссылками
        index = new_text.find("href")    # поиск первой ссылки
        new_text = new_text[index+6:]
        
        # пока есть ссылки в 2 семестре
        while index>0:
            index_temp = 0
            url = "https://www.vyatsu.ru"
            
            # формируем url
            while new_text[index_temp]!="\"":
                url += new_text[index_temp]
                index_temp += 1
            
            # добаляем только свежее расписание
            temp_url = url[:-4]
            year_end = int(temp_url[-4:])
            month_end = int(temp_url[-6:-4])
            day_end = int(temp_url[-8:-6])
            date = datetime.date(year_end, month_end, day_end)
            current_date = datetime.date.today()
            
            # если текущая дата больше, чем последний день с раписанием, то удаляем ссылку
            if current_date < date:
                # добавляем ссылку в словарь
                if name_group in schedule:
                    schedule[name_group].append(url)
                else:
                    schedule[name_group] = [url]
                    
            # переемещаем индекс вперёд
            new_text = new_text[index_temp:]
            index = new_text.find("href")
            new_text = new_text[index+6:]
    return schedule



# получение клавиатуры с названиями групп
async def get_keyboard(input_group):
    # получение данных с сайта
    response = await get_content(url1)
    
    # получение кортежа групп
    if response:
        set_groups = await get_name_groups(response)
        
        # обработка введённой строки
        list_input_groups = []
    
        #добавляем необработанную группу в массив
        input_group = input_group.lower()
        list_input_groups.append(input_group)
    
        #режем строку на куски, где разделителем является тире
        if input_group.find("-") > 0:
            input_split_dash = input_group.split("-")
            input_split_dash = [value.strip() for value in input_split_dash]
            if len(input_split_dash)>1:
                list_symbol = ['б', 'м', 'а', 'с']
                for i in list_symbol:
                    list_input_groups.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
                list_input_groups.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
            
        #если есть пробелы, то режем строку на куски по пробелам
        if any(char.isspace () for char in input_group):
            input_split_dash = input_group.split(" ")
            input_split_dash = [value.strip() for value in input_split_dash]
            if len(input_split_dash)>1:
                list_symbol = ['б', 'м', 'а', 'с']
                for i in list_symbol:
                    list_input_groups.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
                list_input_groups.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
        
        #убираем повторки
        list_input_groups = set(list_input_groups)
    
        #формирование клавиатуры
        list_keyboard_buttons = []
        for group in set_groups:
            for input_group in list_input_groups:
                if input_group in group.lower():
                    list_keyboard_buttons.append([InlineKeyboardButton(text=f'{group}', callback_data=f'{group}')])
        if len(list_keyboard_buttons)>0:
            return InlineKeyboardMarkup(inline_keyboard=list_keyboard_buttons)


# получение файлов
async def get_files(name_group):
    # получение данных с сайта
    response = await get_content(url1)
    result = []
    if response:
        list_groups = await get_name_groups(response)
        url_schedule = await get_url_schedule(response, list_groups)
        lists_url = url_schedule[name_group]
        for url in lists_url:
            response = requests.get(url, headers=user_agent)
            with open(url[-29:], 'wb') as file:
                file.write(response.content)
            result.append(url[-29:])
    return result
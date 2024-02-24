from bs4 import BeautifulSoup
from typing import List
from aiogram.types import FSInputFile
import requests
import sqlite3
import datetime
import os
import asyncio
from config import bot
from config import chat_id


user_agent: dict = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36'}
url1: str = "https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie-zanyatiy-dlya-studentov.html"
url2: str = "https://www.vyatsu.ru/internet-gazeta/raspisanie-sessiy-obuchayuschihsya-na-2016-2017-uc.html"


# актуализация базы данных
async def clear_db():
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS data(name_group text, url text, id_file text)")
    base.commit()
    cmd = "SELECT url, id_file FROM data"
    data = cur.execute(cmd).fetchall()
    
    count = 0
    # для каждой ссылки
    for value in data:
        url = value[0]
        id_file = value[1]
        
        # находим время окончания недели расписания
        temp_url = url[:-4]
        year_end = int(temp_url[-4:])
        month_end = int(temp_url[-6:-4])
        day_end = int(temp_url[-8:-6])
        date = datetime.date(year_end, month_end, day_end)
        current_date = datetime.date.today()
        
        #если старое, то удаляем
        if date < current_date:
            cmd = "delete from data where id_file=?"
            base.execute(cmd, (id_file,))
            base.commit()
            count += 1
    print(f"Удалено: {count} ссылок")
    base.close()


# получение данных с сайта
async def get_content(url: str):
    return requests.get(url, headers=user_agent)


# получение списка из групп
async def get_name_groups(response):
    soup = BeautifulSoup(response.text, 'lxml')
    list_groups = soup.find_all('div', class_='grpPeriod')
    list_groups = [value.text.strip() for value in list_groups]
    set_groups = set(list_groups)
    list_groups = list(set_groups)
    list_groups.sort()
    return list_groups


# получение ссылок на расписание
async def get_url_schedule(response, list_groups: List[str]) -> dict[str, List[str]]:
    schedule: dict[str, List[str]] = {}
    count = 0
    for name_group in list_groups:
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
            if current_date < date:
                # добавляем ссылку в словарь
                if name_group in schedule:
                    schedule[name_group].append(url)
                else:
                    schedule[name_group] = [url]
                count += 1
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
            if current_date < date:
                # добавляем ссылку в словарь
                if name_group in schedule:
                    schedule[name_group].append(url)
                else:
                    schedule[name_group] = [url]
                count += 1
            # перемещаем индекс вперёд
            new_text = new_text[index_temp:]
            index = new_text.find("href")
            new_text = new_text[index+6:]
    print(f"Ссылок получено с сайта: {count}")
    return schedule


async def update_db(schedule: dict[str, List[str]]):
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS data(name_group text, url text, id_file text)")
    base.commit()
    count_update = 0
    count_insert = 0
    # для каждой группы
    for group in schedule:
        # для каждой ссылки
        for url in schedule[group]:
            
            # скачивание файла
            response = requests.get(url, headers=user_agent)
            with open(url[-29:], 'wb') as file:
                file.write(response.content)
                
            # загрузка файл в тг
            input_file = FSInputFile(url[-29:])
            msg = await bot.send_document(chat_id, input_file)
            await asyncio.sleep(1)
            
            # получение id_file
            id_file = msg.document.file_id
            
            # удаление сообщения из ОС
            os.remove(url[-29:])
            
            # удаление файла из чата
            await bot.delete_message(chat_id, msg.message_id)
            await asyncio.sleep(1)
            
            # заполнение бд
            cmd = "select url from data where url=?"
            data = cur.execute(cmd, (url,)).fetchone()
            
            # если ссылка новая, то добавляем
            if data == None:
                cmd = "insert into data values(?, ?, ?)"
                cur.execute(cmd, (group, url, id_file))
                base.commit()
                count_insert += 1
            # иначе обновляем file_id
            else:
                cmd = "update data set id_file=? where url=?"
                cur.execute(cmd, (id_file, url))
                base.commit()
                count_update += 1
    print(f"Итого: {count_insert} ссылок добавлено в бд")
    print(f"{count_update} ссылок обновлено в бд")
    
    cmd = "select count(*) from data"
    data = cur.execute(cmd).fetchone()
    print(f"Всего данных в бд: {data[0]} строк")
    
    cmd = "select count(distinct name_group) from data"
    data = cur.execute(cmd).fetchone()
    print(f"Всего групп в бд: {data[0]}")
    base.close()
    

async def start_parsing_pdf():
    while True:
        
        print(f"Время начала обновления: {datetime.datetime.now()}")
        # удаление неактуальных данных
        await clear_db()
        
        try:
            # получение расписания семестров
            response = await get_content(url1)
            
            # получение кортежа групп
            list_groups: List[str] = await get_name_groups(response)
            
            # получение ссылок
            schedule: dict[str, List[str]] = await get_url_schedule(response, list_groups)
            
            # заполнение базы данных id файлов
            await update_db(schedule)

            # получение расписания сессии
            response = await get_content(url2)
            
            # получение кортежа групп
            list_groups: List[str] = await get_name_groups(response)
            
            # получение ссылок
            schedule: dict[str, List[str]] = await get_url_schedule(response, list_groups)
            
            # заполнение базы данных id файлов
            await update_db(schedule)
        except:
            pass
        
        print(f"Время конца обновления: {datetime.datetime.now()}")
        
        #обновляем бд каждый 4 часа
        await asyncio.sleep(12000)
        

def main():
    asyncio.run(start_parsing_pdf())
    

if __name__ == '__main__':
    asyncio.run(start_parsing_pdf())
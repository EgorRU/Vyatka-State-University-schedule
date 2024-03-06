from xls2xlsx import XLS2XLSX
from openpyxl import load_workbook
import logging
import requests
import datetime
import sqlite3
import os
import traceback
import asyncio


logging.basicConfig(level=logging.INFO, filename="log.log", format='%(asctime)s:  %(message)s')
user_agent: dict = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36'}
url1: str = "https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/teacher.html"


# актуализация базы данных
async def clear_db():
    base = sqlite3.connect("database.db")
    base.execute("CREATE TABLE IF NOT EXISTS schedule(date text, time_lesson text, name_teacher text, cabinet_number text, name_of_group text, name_of_discipline text)")
    base.commit()
    cur = base.cursor()
    
    # ищем записи в бд по конкретному времени и преподу
    cmd = "select date from schedule"
    data_by_db = cur.execute(cmd).fetchall()
    
    list_date = []
    for record in data_by_db:
        temp_date = record[0]
        date_datetime = datetime.date(int(temp_date[6:])+2000, int(temp_date[3:5]), int(temp_date[:2]))
        list_date.append(date_datetime)
    
    data = list(set(list_date))
    
    current_date = datetime.date.today()
    for date in data:
        if date < current_date:
            cmd = "delete from schedule where date=?"
            day = date.day if len(str(date.day))==2 else f"0{date.day}"
            month = date.month if len(str(date.month))==2 else f"0{date.month}"
            year = date.year-2000
            temp_date = f"{day}.{month}.{year}"
            cur.execute(cmd, (temp_date,))
            base.commit()
    base.close()
    

# получение данных с сайта
async def get_content(url: str):
    return requests.get(url, headers=user_agent)


# получение актуальных ссылок с сайта
async def get_urls(response):
    list_urls = []
    text = response.text
    
    # ищем первую ссылку
    index = text.find('href="/reports/')
    text = text[index+6:]
    
    # пока есть ссылки
    while index > 0:
        i = 0
        # пока не конец ссылки
        url = "https://www.vyatsu.ru"
        while text[i]!="\"":
            # формируем url
            url += text[i]
            i += 1
        if url[-3:] == "xls":
            temp_url = url[:-4]
            year_end = int(temp_url[-4:])
            month_end = int(temp_url[-6:-4])
            day_end = int(temp_url[-8:-6])
            date = datetime.date(year_end, month_end, day_end)
            current_date = datetime.date.today()
            if current_date < date and (date-current_date).days <= 35:
                list_urls.append(url)
                
        text = text[i:]
        # ищем новую ссылку
        index = text.find('href="/reports/')
        text = text[index+6:]
        
    logging.info(f"Получено url-ссылок: {len(list_urls)}\n")
    return list_urls


# добавление или изменение одной строки
async def update_db(date, time_lesson, name_teacher, cabinet_number, name_of_group, name_of_discipline):
    base = sqlite3.connect("database.db")
    base.execute("CREATE TABLE IF NOT EXISTS schedule(date text, time_lesson text, name_teacher text, cabinet_number text, name_of_group text, name_of_discipline text)")
    base.commit()
    cur = base.cursor()
    
    # ищем запись в бд по конкретному времени и преподу
    cmd = "select date from schedule where date=? and time_lesson=? and name_teacher=?"
    data = cur.execute(cmd, (date, time_lesson, name_teacher)).fetchone() 
    
    # название групп в строку
    str_name_of_group = " ".join(name_of_group).strip()
    
    # если запись есть, то меняем её поля
    if data != None:
        cmd = "update schedule set cabinet_number=?, name_of_group=?, name_of_discipline=? where date=? and time_lesson=? and name_teacher=?"
        cur.execute(cmd, (cabinet_number, str_name_of_group, name_of_discipline, date, time_lesson, name_teacher))
        base.commit()
    else:
        cmd = "insert into schedule values(?,?,?,?,?,?)"
        cur.execute(cmd, (date, time_lesson, name_teacher, cabinet_number, str_name_of_group, name_of_discipline))
        base.commit()
    base.close()


# скачивание и парсинг xlsx файлов
async def parsing_xlsx(list_urls):
    # для каждой ссылки
    count = 0
    for url in list_urls:
        # скачивание файла
        response = requests.get(url, headers=user_agent)
        with open(url[-27:], 'wb') as file:
            file.write(response.content)
            
        # конвертируем в xlsx
        x2x = XLS2XLSX(url[-27:])
        path = url[-27:] + "x"
        x2x.to_xlsx(path)
        
        #открываем файл
        wookbook = load_workbook(path)
        worksheet = wookbook.active

        #парсим файл
        for i in range(3, worksheet.max_column):
            # ФИО преподавателя
            name_teacher = worksheet.cell(row=2, column=i).value
            for j in range(3, worksheet.max_row):
                
                # данные ячеек
                value = worksheet.cell(row=j, column=i).value

                # время пары
                time_lesson = worksheet.cell(row=j, column=2).value.strip()

                # дата
                date = worksheet.cell(row=j, column=1).value

                # если дата пустая, то ищем дату, зачем оставляем только число xx-xx-xx
                index_for_day = j - 1
                while date == None:
                    date = worksheet.cell(row=index_for_day, column=1).value
                    index_for_day -= 1
                date = date.strip()[-8:]
                
                # парсим значения ячейки, если они есть
                cabinet_number = None
                name_of_group = []
                name_of_discipline = None
                
                # если ячейка была не пустая
                if value!= None:
                    # разделяем даные в ячейке
                    list_values = value.strip().split()
                    
                    if list_values[0][0].isdigit():
                        # номер кабинета
                        cabinet_number = list_values[0]
                        
                        # название дисциплины
                        name_of_discipline = " ".join(list_values[1:]).strip()
                        
                    else:
                        # номер кабинета
                        cabinet_number = None
                        
                        # название дисциплины
                        name_of_discipline = value
                        
                    # названия групп
                    for ii in range(len(list_values)):
                        val = list_values[ii].replace(",","").strip()
                        if val.count("-") == 3:
                            if val not in name_of_group:
                                name_of_group.append(val)
                    
                    # название дисциплины снова, делаем короче
                    if "Элективные дисциплины (модули) по физической культуре и спорту" in name_of_discipline:
                        name_of_discipline = "Элективные дисциплины (модули) по физической культуре и спорту"
                    if len(name_of_discipline) > 60:
                        index = 9999
                        for group in name_of_group:
                            temp_index = name_of_discipline.find(group)
                            if temp_index < index and temp_index>0:
                                index = temp_index
                        name_of_discipline = name_of_discipline[:index].strip()

                    # сортируем названия групп, чтобы было одинаково в бд
                    name_of_group.sort()
                    
                # проверяем время, чтоб данные были новые
                date_datetime = datetime.date(int(date[6:])+2000, int(date[3:5]), int(date[:2]))
                current_date = datetime.date.today()
                
                # если данные свежие, то записываем в бд
                if date_datetime >= current_date:
                    if not (name_teacher==None and cabinet_number==None and name_of_group==None and name_of_discipline==None):
                        count += 1
                        await update_db(date, time_lesson, name_teacher, cabinet_number, name_of_group, name_of_discipline)
        # спим
        await asyncio.sleep(1)
        
        # удаляем оба файла
        os.remove(url[-27:])
        os.remove(path)
        
    logging.info(f"Изменено строк: {count}\n")
    

async def start_parsing_xlsx():
    while True:
        
        logging.info(f"Время начала обновления: {datetime.datetime.now()}\n")
        
        # удаление неактуальных данных
        await clear_db()
        
        try:
            # получение данных с сайта
            response = await get_content(url1)
        
            # получение ссылок с сайта
            list_urls = await get_urls(response)
        
            # заполнение базы данных id файлов
            await parsing_xlsx(list_urls)
        except:
            logging.exception(f"{traceback.format_exc()}\n")
        
        logging.info(f"Время конца обновления: {datetime.datetime.now()}\n")
        
        # обновляем бд каждые 3 часа
        await asyncio.sleep(9000)


def main():
    asyncio.run(start_parsing_xlsx())
    

if __name__ == '__main__':
    asyncio.run(start_parsing_xlsx())
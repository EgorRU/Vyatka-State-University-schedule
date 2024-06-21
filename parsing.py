from xls2xlsx import XLS2XLSX
from openpyxl import load_workbook
from typing import NoReturn, List 
import logging
import requests
import datetime
import sqlite3
import os
import traceback
import asyncio


time_from_pair = {
    "1 пара": "8:20-9:50",
    "2 пара": "10:00-11:30",
    "3 пара": "11:45-13:15",
    "4 пара": "14:00-15:30",
    "5 пара": "15:45-17:15",
    "6 пара": "17:20-18:50",
    "7 пара": "18:55-20:15",
    }

logging.basicConfig(level=logging.INFO, filename="log.log", format='%(asctime)s:  %(message)s')
user_agent: dict = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36'}
url_site: str = "https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/zanyatost-auditoriy.html"



# создание базы даных, если её нет
async def create_db() -> None:
    base = sqlite3.connect("database.db")
    base.execute("CREATE TABLE IF NOT EXISTS schedule(date text, time_lesson text, cabinet_number text, name_of_group text, name_teacher text, name_of_discipline text)")
    base.commit()



# удаление старых записей
async def remove_old_data_from_db() -> None:
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    
    # получение даты из бд
    cmd = "select date from schedule"
    data_by_db = cur.execute(cmd).fetchall()
    
    # формирование списка с датами
    list_date: List[datetime.datetime] = []
    for record in data_by_db:
        temp_date: str = record[0]
        date_datetime = datetime.date(int(temp_date[6:])+2000, int(temp_date[3:5]), int(temp_date[:2]))
        list_date.append(date_datetime)
    
    # удаление дубликатов и сортировка
    list_date = list(set(list_date))
    list_date.sort()
    
    # сегодняшняя дата
    current_date = datetime.date.today()
    
    # понедельник текущейй недели
    current_date -= datetime.timedelta(days=current_date.weekday())
    
    # если прошло больше двух недель с понедельника текущей недели, то удаляем расписание
    for date in list_date:
        if date + datetime.timedelta(days=14) < current_date:
            cmd: str = "delete from schedule where date=?"
            day: str = f"{date.day}" if len(str(date.day))==2 else f"0{date.day}"
            month: str = f"{date.month}" if len(str(date.month))==2 else f"0{date.month}"
            year: str = f"{date.year-2000}"
            date_by_str: str = f"{day}.{month}.{year}"
            cur.execute(cmd, (date_by_str,))
            base.commit()
        else:
            break
    base.close()
    


# получение данных с сайта
async def get_content(url: str):
    return requests.get(url, headers=user_agent)



# получение актуальных ссылок с сайта
async def get_urls(response) -> List[str]:
    list_urls: List[str] = []
    text: str = response.text
    
    # ищем первую ссылку
    index = text.find('href="/reports/')
    text = text[index+6:]
    
    # пока есть ссылки
    while index > 0:
        i = 0
        url = "https://www.vyatsu.ru"
        
        # пока не конец ссылки, формируем url
        while text[i]!="\"":
            url += text[i]
            i += 1
            
        # если формат ссылки .xls (может быть .html)
        # проверяем даты, которые будут по ссылке
        if url[-3:] == "xls":
            temp_url = url[:-4]
            year_end = int(temp_url[-4:])
            month_end = int(temp_url[-6:-4])
            day_end = int(temp_url[-8:-6])
            
            # последняя дата в расписании
            last_date = datetime.date(year_end, month_end, day_end)
            
            # текущая дата
            current_date = datetime.date.today()
            
            # если последняя дата в будущем и не более двух месяцев 
            if (current_date < last_date) and (last_date - current_date).days < 60:
                list_urls.append(url)
        
        # ищем новую ссылку
        text = text[i:]
        index = text.find('href="/reports/')
        text = text[index+6:]
    return list_urls



#добавление или изменение одной строки(пары)
async def update_db(date, time_lesson, cabinet_number, name_of_group, name_teacher, name_of_discipline, *, empty = False, many = False):
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    
    # ищем записи в бд по конкретной дате, времени и кабинету
    cmd = "select date, time_lesson, cabinet_number from schedule where date=? and time_lesson=? and cabinet_number=?"
    data = cur.execute(cmd, (date, time_lesson, cabinet_number,)).fetchall() 
    
    # если пары нет сейчас, то возможно она есть в старом расписании - надо удалить
    if empty:
        # если записи есть, то удаляем их
        if data != None:
            cmd = "delete from schedule where date=? and time_lesson=? and cabinet_number=?"
            cur.execute(cmd, (date, time_lesson, cabinet_number,))
            base.commit()
            
    # если пара есть сейчас, то нужно заменить(если есть) или добавить(если нет)
    else:
        # если нет старых записей, то добавляем все группы на паре
        if data == None:
            for i in range(len(name_of_group)):
                cmd = "insert into schedule values(?,?,?,?,?,?)"
                cur.execute(cmd, (date, time_lesson, cabinet_number, name_of_group[i], name_teacher[i], name_of_discipline[i],))
                base.commit()
            
        # если есть записи
        else:
            # если добавляется много записей, то удаляем все старые и добавляем все новые
            if many:
                cmd = "delete from schedule where date=? and time_lesson=? and cabinet_number=?"
                cur.execute(cmd, (date, time_lesson, cabinet_number,))
                base.commit()
                
                for i in range(len(name_of_group)):
                    cmd = "insert into schedule values(?,?,?,?,?,?)"
                    cur.execute(cmd, (date, time_lesson, cabinet_number, name_of_group[i], name_teacher[i], name_of_discipline[i],))
                    base.commit()
            # если добавляется одна запись
            else:
                # если запись всего одна в бд, то просто заменяем
                if len(data)==1:
                    cmd = "update schedule set name_of_group=?, name_teacher=?, name_of_discipline=? where date=? and time_lesson=? and cabinet_number=?"
                    cur.execute(cmd, (name_of_group[0], name_teacher[0], name_of_discipline[0], date, time_lesson, cabinet_number,))
                    base.commit()
                # если записей много в бд, но добавляется одна
                else:
                    # удаляем все
                    cmd = "delete from schedule where date=? and time_lesson=? and cabinet_number=?"
                    cur.execute(cmd, (date, time_lesson, cabinet_number,))
                    base.commit()
                    
                    # добавляем одну запись
                    cmd = "insert into schedule values(?,?,?,?,?,?)"
                    cur.execute(cmd, (date, time_lesson, cabinet_number, name_of_group[0], name_teacher[0], name_of_discipline[0],))
                    base.commit()
                    
    # закрываем соединение с бд
    base.close()



# скачивание файла с расширением .xls
async def download(url: str) -> None:
    response = requests.get(url, headers=user_agent)
    with open(url[-25:], 'wb') as file:
        file.write(response.content)



# конвертирование файлв из .xls в .xlsx
async def convert_xls_to_xlsx(path: str) -> None:
    x2x = XLS2XLSX(path)
    x2x.to_xlsx(path + 'x')



# парсинг файла и заполнение бд данными
async def try_parsing_url(url: str) -> None:
    # скичивание файла
    await download(url)
            
    # конвертирование файла из .xls в .xlsx
    path = url[-25:]
    await convert_xls_to_xlsx(path)
    
    # удаляем старый файл
    os.remove(path)
    
    #открываем файл уже с расширением .xlsx
    path += 'x'
    wookbook = load_workbook(path)
    worksheet = wookbook.active

    # парсим файл
    for i in range(3, worksheet.max_column):
        # номер кабинета
        cabinet_number: str = worksheet.cell(row=2, column=i).value
        
        # по каждому столбцу
        for j in range(3, worksheet.max_row):
                
            # номер пары
            time_lesson: str = worksheet.cell(row=j, column=2).value.strip()
            # время пары
            time_lesson: str = time_from_pair[time_lesson]
            
            # дата
            date = worksheet.cell(row=j, column=1).value
            # если дата пустая, то ищем дату, зачем оставляем только число xx-xx-xx
            index_for_day = j - 1
            while date == None:
                date = worksheet.cell(row=index_for_day, column=1).value
                index_for_day -= 1
            date = date.strip()[-8:]
            

            # данные основной ячейки
            value: str = worksheet.cell(row=j, column=i).value
            
            # если что-то есть, но не нужное - удаляем
            if value != None:
                if "Резервирование" in value:
                    value = None
            
            # парсим, если что-то есть
            if value != None:
                # если несколько групп в одном кабинете
                if "\n" in value:
                    list_value: list[str] = value.split("\n")
                else:
                    list_value: list[str] = [value]
                    
                # убираем концевые пробелы
                list_value: list[str] = [value.strip() for value in list_value]
                
                # убираем вначале приписку из двух-трёх символом, если она есть
                for ii in range(len(list_value)):
                    if len(list_value[ii].split()[0]) <= 3:
                        list_value[ii] = " ".join(list_value[ii].split()[1:])

                # списки(если на паре несколько групп)
                name_of_group = []
                name_teacher = []
                name_of_discipline = []     
                
                # разделяем данные для каждой записи в ячейке(в одном кабинете может быть несколько групп)
                for value in list_value:
                    # делим строку
                    text_split = value.split()
                    
                    # если две точки есть в ласт слове, то инициалы = препод
                    if text_split[-1].count(".") == 2:
                        name_teacher.append(" ".join(text_split[-2:]))
                        text_split = text_split[:-2]
                    # иначе препода нет
                    else:
                        name_teacher.append(None)
                    
                    # если в конце названия группы запятая, то дальше идёт номер подгруппы
                    if text_split[0][-1] == ",":
                        name_of_group.append(" ".join(text_split[:3]))
                        text_split = text_split[3:]
                    else:
                        name_of_group.append(text_split[0])
                        text_split = text_split[1:]
                        
                    # название дисциплины
                    name_of_discipline.append(" ".join(text_split))    
                
                # обновляем данные
                # если на паре одна группа
                if len(list_value)==1:
                    await update_db(date, time_lesson, cabinet_number, name_of_group, name_teacher, name_of_discipline)
                    
                # если на паре несколько групп
                else:
                    await update_db(date, time_lesson, cabinet_number, name_of_group, name_teacher, name_of_discipline, many = True)
                    
            # если пары нет на это дату, время и кабинет
            else:
                await update_db(date, time_lesson, cabinet_number, None, None, None, empty = True)

    # удаляем файд
    os.remove(path)
        


# цикл обработки файлов
async def start_parsing_xlsx() -> NoReturn:
    #создание базы данных, если её нет
    await create_db()
    
    # цикл обработки
    while True:
        # удаление старых записей
        await remove_old_data_from_db()
        
        # обновление записей
        try:
            # получение данных с сайта
            response = await get_content(url_site)
            
            # получение ссылок с сайта
            urls: List[str] = await get_urls(response)
            
            # заполнение базы данных расписанием по ссылкам
            for url in urls:
                await try_parsing_url(url)
        except:
            logging.exception(f"{traceback.format_exc()}\n")
        
        # обновляем бд каждые 3 часа
        await asyncio.sleep(9000)



# если файл импортируется
def main() -> None:
    asyncio.run(start_parsing_xlsx())


    
# если файл запускается как основной
if __name__ == '__main__':
    asyncio.run(start_parsing_xlsx())
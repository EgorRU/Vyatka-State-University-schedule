import sqlite3
import datetime


number_day_to_day_week = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
    }


# получение списка групп, преподов и кабинетов
async def get_list_groups():
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS schedule(date text, time_lesson text, name_teacher text, cabinet_number text, name_of_group text, name_of_discipline text)")
    base.commit()
    cmd = 'select distinct name_of_group from schedule'
    list_groups = cur.execute(cmd).fetchall()
    list_groups = [value[0] for value in list_groups if value[0]!=None]
    
    new_list_groups = []
    for string in list_groups:
        groups = string.split()
        for group in groups:
            if group not in new_list_groups:
                new_list_groups.append(group)
    new_list_groups.sort()
    return new_list_groups
        

async def get_list_teachers():
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS schedule(date text, time_lesson text, name_teacher text, cabinet_number text, name_of_group text, name_of_discipline text)")
    base.commit()
    cmd = 'select distinct name_teacher from schedule'
    list_teachers = cur.execute(cmd).fetchall()
    list_teachers = [value[0] for value in list_teachers if value[0]!=None]
    list_teachers.sort()
    return list_teachers


async def get_list_cabinet():
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS schedule(date text, time_lesson text, name_teacher text, cabinet_number text, name_of_group text, name_of_discipline text)")
    base.commit()
    cmd = 'select distinct cabinet_number from schedule'
    list_cabinet = cur.execute(cmd).fetchall()
    list_cabinet = [value[0] for value in list_cabinet if value[0]!=None]
    list_cabinet.sort()
    return list_cabinet


# получение возможного листа кнопок для выбора
async def get_list_schedule(text):
    # получение списка групп, преподов и кабинетов
    list_groups_in_db = await get_list_groups()
    list_teachers_in_db = await get_list_teachers()
    list_cabinet_in_db = await get_list_cabinet()
    
    # добавляем необработанную строку сразу же в список, который дальше проверяем
    text = text.lower()
    list_to_check = [text]
    
    # режем строку на куски, где разделителем является тире
    if text.find("-") > 0:
        input_split_dash = text.split("-")
        input_split_dash = [value.strip() for value in input_split_dash if value!="" and value!=" "]
        if len(input_split_dash)>1:
            if input_split_dash[0].isdigit() and input_split_dash[1].isdigit():
                if "-".join(input_split_dash[:2]).strip() in list_cabinet_in_db:
                    return ["-".join(input_split_dash[:2]).strip()]
                else:
                    return []
            list_symbol = ['б', 'м', 'а', 'с']
            for i in list_symbol:
                list_to_check.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
            list_to_check.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
            
    # если есть пробелы, то режем строку на куски по пробелам
    if any(char.isspace () for char in text):
        input_split_dash = text.split(" ")
        input_split_dash = [value.strip() for value in input_split_dash if value!=""]
        if len(input_split_dash)>1:
            list_symbol = ['б', 'м', 'а', 'с']
            for i in list_symbol:
                list_to_check.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
            list_to_check.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
    # проверяем наш список на валидность, что валидно - будут кнопки
    list_valid_data_for_buttons = []
    for valid_value_in_db in list_groups_in_db:
        for value_for_check in list_to_check:
            if value_for_check in valid_value_in_db.lower() and valid_value_in_db not in list_valid_data_for_buttons:
                list_valid_data_for_buttons.append(valid_value_in_db)
    
    for valid_value_in_db in list_teachers_in_db:
        for value_for_check in list_to_check:
            if value_for_check in valid_value_in_db.lower() and valid_value_in_db not in list_valid_data_for_buttons:
                list_valid_data_for_buttons.append(valid_value_in_db)

    for valid_value_in_db in list_cabinet_in_db:
        for value_for_check in list_to_check:
            if value_for_check in valid_value_in_db.lower() and valid_value_in_db not in list_valid_data_for_buttons:
                list_valid_data_for_buttons.append(valid_value_in_db)
    return list_valid_data_for_buttons


# получение всех дат для запроса в отсортированном порядке
async def get_date_for_valid_text(valid_text):
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS schedule(date text, time_lesson text, name_teacher text, cabinet_number text, name_of_group text, name_of_discipline text)")
    base.commit()
    
    cmd = f'''select distinct date from schedule where name_teacher=? or cabinet_number=? or name_of_group like "%{valid_text}%"'''
    list_date = cur.execute(cmd,(valid_text, valid_text)).fetchall()
    list_date = [value[0] for value in list_date if value[0]!=None]
    
    new_list_date = [datetime.date(int(value[6:])+2000, int(value[3:5]), int(value[:2])) for value in list_date]
    new_list_date.sort()
    return new_list_date


# получение всех данных в отсортированном виде для запроса
async def get_data_by_valid_text(valid_text):
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS schedule(date text, time_lesson text, name_teacher text, cabinet_number text, name_of_group text, name_of_discipline text)")
    base.commit()
    
    cmd = f'''select * from schedule where name_teacher=? or cabinet_number=? or name_of_group like "%{valid_text}%" and name_of_discipline is not null'''
    list_date = cur.execute(cmd,(valid_text, valid_text)).fetchall()
    list_date = [list(value)for value in list_date if value[5]!=None]
    for i in range(len(list_date)):
        value = list_date[i][0]
        list_date[i][0] = datetime.date(int(value[6:])+2000, int(value[3:5]), int(value[:2]))
    list_date.sort()
    return list_date


# получение расписания по выбранной дате
async def get_schedule_by_date(valid_text, period):
    full_data = await get_data_by_valid_text(valid_text)
    list_date = []
    if period=="Сегод": 
        list_date.append(datetime.date.today())
    elif period=="Завтр":
        list_date.append(datetime.date.today() + datetime.timedelta(days=1))
    elif period=="После":
        list_date.append(datetime.date.today() + datetime.timedelta(days=2))
    else:
        begin_week = period[:10]
        end_week = period[10:]
        date_begin_week = datetime.date(int(begin_week[:4]), int(begin_week[5:7]), int(begin_week[8:]))
        date_end_week = datetime.date(int(end_week[:4]), int(end_week[5:7]), int(end_week[8:]))
        
        list_date.append(date_begin_week)
        while date_begin_week < date_end_week:
            date_begin_week += datetime.timedelta(days=1)
            list_date.append(date_begin_week)
        
    is_global_true = False
    text = f"➡️ {valid_text}\n\n"
    for day in list_date:
        if day.weekday()<6:
            is_true = False
            for day_data in full_data:
                if day == day_data[0] and not is_true:
                    is_true = True
                    is_global_true = True
                    text += f"➡️ {number_day_to_day_week[day.weekday()]} | {day}:\n"
                    text += f"——/ {day_data[1]} /——\n"
                    text += f"{day_data[5]}\n"
                    text += f"{day_data[2]}\n" if day_data[2] != None else ""
                    text += f"{day_data[3]}\n"  if day_data[3] != None else ""
                    text += f"{day_data[4]}\n\n" if len(day_data[4])<30 else f"{valid_text}\n\n"
                elif day == day_data[0]:
                    is_global_true = True
                    text += f"——/ {day_data[1]} /——\n"
                    text += f"{day_data[5]}\n"
                    text += f"{day_data[2]}\n" if day_data[2] != None else ""
                    text += f"{day_data[3]}\n" if day_data[3] != None else ""
                    text += f"{day_data[4]}\n\n" if len(day_data[4])<30 else f"{valid_text}\n\n"
            if not is_true:
                text += f"➡️ {number_day_to_day_week[day.weekday()]} | {day}:\n\nПар нет\n\n"
        
    if not is_global_true:
        next_day = list_date[-1] + datetime.timedelta(days=1)
        is_true = False
        while not is_true and next_day < full_data[-1][0] + datetime.timedelta(days=14):
            for day_data in full_data:
                if next_day==day_data[0] and not is_true:
                    text += "Следующие пары\n\n"
                    is_true = True
                    text += f"➡️ {number_day_to_day_week[next_day.weekday()]} | {next_day}:\n"
                    text += f"——/ {day_data[1]} /——\n"
                    text += f"{day_data[5]}\n"
                    text += f"{day_data[2]}\n" if day_data[2] != None else ""
                    text += f"{day_data[3]}\n" if day_data[3] != None else ""
                    text += f"{day_data[4]}\n\n" if len(day_data[4])<30 else f"{valid_text}\n\n"
                elif next_day == day_data[0]:
                    text += f"——/ {day_data[1]} /——\n"
                    text += f"{day_data[5]}\n"
                    text += f"{day_data[2]}\n" if day_data[2] != None else ""
                    text += f"{day_data[3]}\n" if day_data[3] != None else ""
                    text += f"{day_data[4]}\n\n" if len(day_data[4])<30 else f"{valid_text}\n\n"
            next_day += datetime.timedelta(days=1)
    return text

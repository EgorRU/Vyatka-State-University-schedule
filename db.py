import sqlite3
import datetime


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
        input_split_dash = [value.strip() for value in input_split_dash]
        if len(input_split_dash)>1:
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

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3


# получение списка групп
async def get_name_groups():
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS data(name_group text, url text, id_file text)")
    base.commit()
    cmd = "SELECT distinct name_group FROM data"
    list_groups = cur.execute(cmd).fetchall()
    base.close()
    if list_groups:
        return [value[0] for value in list_groups]


# получение кнопок с группами
async def get_keyboard(input_group):
    # получение списка групп
    list_groups = await get_name_groups()
    list_groups.sort()
        
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
        
    #формирование клавиатуры
    list_name_valid_groups = []
    for group in list_groups:
        for input_group in list_input_groups:
            if input_group in group.lower() and group not in list_name_valid_groups:
                list_name_valid_groups.append(group)
                
    if len(list_name_valid_groups)>0:
        list_keyboard_buttons = []
        for group in list_name_valid_groups:
            list_keyboard_buttons.append([InlineKeyboardButton(text=f'{group}', callback_data=f'{group}')])
        return InlineKeyboardMarkup(inline_keyboard=list_keyboard_buttons)
    

# получение ссылок на расписание
async def get_files(name_group):
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS data(name_group text, url text, id_file text)")
    base.commit()
    cmd = "SELECT id_file FROM data where name_group=?"
    list_id_file = cur.execute(cmd, (name_group,)).fetchall()
    base.close()
    if list_id_file:
        return [value[0] for value in list_id_file]
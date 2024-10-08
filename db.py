# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from typing import List, Union
# import sqlite3
# import datetime

# number_day_to_day_week = {
#     0: "Понедельник",
#     1: "Вторник",
#     2: "Среда",
#     3: "Четверг",
#     4: "Пятница",
#     5: "Суббота",
#     6: "Воскресенье"
#     }


# # получение списка групп
# async def get_list_groups() -> List[str]:
#     base = sqlite3.connect("database.db")
#     cur = base.cursor()
#     cmd = 'select distinct name_of_group from schedule'
#     list_groups = cur.execute(cmd).fetchall()
#     base.close()
#     if list_groups == None:
#         []
#     list_groups = [value[0] for value in list_groups if value[0]!=None]
#     list_groups.sort()
#     return list_groups
        

# # получение списка преподов
# async def get_list_teachers() -> List[str]:
#     base = sqlite3.connect("database.db")
#     cur = base.cursor()
#     cmd = 'select distinct name_teacher from schedule'
#     list_teachers = cur.execute(cmd).fetchall()
#     base.close()
#     if list_teachers == None:
#         []
#     list_teachers = [value[0] for value in list_teachers if value[0]!=None]
#     list_teachers.sort()
#     return list_teachers


# # получение списка кабинетов
# async def get_list_cabinet() -> List[str]:
#     base = sqlite3.connect("database.db")
#     cur = base.cursor()
#     cmd = 'select distinct cabinet_number from schedule'
#     list_cabinet = cur.execute(cmd).fetchall()
#     base.close()
#     if list_cabinet == None:
#         []
#     list_cabinet = [value[0] for value in list_cabinet if value[0]!=None]
#     list_cabinet.sort()
#     return list_cabinet


# # получение возможного листа кнопок для выбора
# async def get_list_schedule(text) -> List[str]:
#     if text == "." or text == "_" or text == "__":
#         return []
#     # список с валидными данными
#     list_valid_data_for_buttons = []
#     text = text.strip().lower()
    
#     # получение списка возможных групп, преподов и кабинетов
#     list_groups_from_db: List[str] = await get_list_groups()
#     list_teachers_from_db: List[str] = await get_list_teachers()
#     list_cabinet_from_db: List[str] = await get_list_cabinet()
    
#     # проверка на преподов
#     for teacher in list_teachers_from_db:
#         if text in teacher.split()[0].strip().lower():
#             list_valid_data_for_buttons.append(teacher)
    
#     # если список не пуст, то возвращаем его
#     if len(list_valid_data_for_buttons) > 0:
#         list_valid_data_for_buttons.sort()
#         return list_valid_data_for_buttons
    
#     # проверка на кабинеты
#     for cabinet in list_cabinet_from_db:
#         if text == cabinet.strip().lower():
#             list_valid_data_for_buttons.append(cabinet)
    
#     # если список не пуст, то возвращаем его
#     if len(list_valid_data_for_buttons) > 0:
#         list_valid_data_for_buttons.sort()
#         return list_valid_data_for_buttons
    
#     # иначе это название группы, парсим название группы
#     # добавляем необработанную строку сразу же в список, который дальше проверяем
#     list_to_check = [text]
    
#     # режем строку на куски, где разделителем является тире
#     if text.find("-") > 0:
#         input_split_dash = text.split("-")
#         input_split_dash = [value.strip() for value in input_split_dash if value!="" and value!=" "]
#         if len(input_split_dash)>1:
#             list_symbol = ['б', 'м', 'а', 'с']
#             for i in list_symbol:
#                 list_to_check.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
#             list_to_check.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
            
#     # если есть пробелы, то режем строку на куски по пробелам
#     if any(char.isspace() for char in text):
#         input_split_dash = text.split(" ")
#         input_split_dash = [value.strip() for value in input_split_dash if value!=""]
#         if len(input_split_dash)>1:
#             list_symbol = ['б', 'м', 'а', 'с']
#             for i in list_symbol:
#                 list_to_check.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
#             list_to_check.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
    
#     # если нет не пробелов, не тире, просто одна строка (допустим: "подб3")
#     if len(text.split())==1:
#         number_course: str = text[-1]
#         name_group: str = text[:-1]
#         list_symbol = ['б', 'м', 'а', 'с']
#         for i in list_symbol:
#             list_to_check.append(f"{name_group}{i}-{number_course}")
#         list_to_check.append(f"{name_group}-{number_course}")
        
#     # поиск валидных групп
#     for valid_value_from_db in list_groups_from_db:
#         for value_for_check in list_to_check:
#             if value_for_check in valid_value_from_db.lower() and valid_value_from_db not in list_valid_data_for_buttons:
#                 # если группа с номером подгруппы
#                 if len(valid_value_from_db.split())>1:
#                     list_valid_data_for_buttons.append(valid_value_from_db.split()[0][:-1])
#                 else:
#                     list_valid_data_for_buttons.append(valid_value_from_db)
#     list_valid_data_for_buttons = list(set(list_valid_data_for_buttons))
#     list_valid_data_for_buttons.sort()
#     return list_valid_data_for_buttons



# # получение всех дат с расписанием для запроса в отсортированном порядке
# async def get_all_date_for_valid_text(valid_text) -> List[datetime.date]:
#     base = sqlite3.connect("database.db")
#     cur = base.cursor()
#     cmd = f'select distinct date from schedule where name_teacher=? or cabinet_number=? or name_of_group like "%{valid_text}%"'
#     list_date = cur.execute(cmd,(valid_text, valid_text,)).fetchall()
#     base.close()
#     list_date = [value[0] for value in list_date if value[0] != None]
#     new_list_date = [datetime.date(int(value[6:])+2000, int(value[3:5]), int(value[:2])) for value in list_date]
#     new_list_date.sort()
#     return new_list_date



# # получение ВСЕХ ПОЛЕЙ по заданному дню
# async def get_all_data_from_date(valid_text, date):
#     base = sqlite3.connect("database.db")
#     cur = base.cursor()
#     day: str = f"{date.day}" if len(str(date.day))==2 else f"0{date.day}"
#     month: str = f"{date.month}" if len(str(date.month))==2 else f"0{date.month}"
#     year: str = f"{date.year-2000}"
#     date: str = f"{day}.{month}.{year}"
#     cmd = f'select * from schedule where date=? and (name_teacher=? or cabinet_number=? or name_of_group like "%{valid_text}%")'
#     list_data = cur.execute(cmd,(date, valid_text, valid_text,)).fetchall()
#     base.close()
#     return list_data



# # получение расписания по выбранной дате
# async def get_schedule_by_date(valid_text, period):   
#     def my_sort(value):
#         time = value[1]
#         begin_time = time.split("-")[0]
#         hour = int(begin_time.split(":")[0])
#         minute = int(begin_time.split(":")[0])
#         time = datetime.time(hour, minute)
#         return time
    
#     # даты которые надо отобразить
#     list_date = []
#     if period=="Сегод": 
#         list_date.append(datetime.date.today() + datetime.timedelta(hours=3))
#     elif period=="Завтр":
#         list_date.append(datetime.date.today() + datetime.timedelta(days=1, hours=3))
#     elif period=="После":
#         list_date.append(datetime.date.today() + datetime.timedelta(days=2, hours=3))
        
#     # если другой период
#     elif "Неделя" in period:
#         begin_week: str = period[6:16]
#         begin_week = datetime.date(int(begin_week[:4]), int(begin_week[5:7]), int(begin_week[8:10]))
#         list_date = [begin_week + datetime.timedelta(days=i) for i in range(7)]
#     elif "Всё" in period:
#         begin: str = period[3:13]
#         end: str = period[13:23]
#         begin_week = datetime.date(int(begin[:4]), int(begin[5:7]), int(begin[8:10]))
#         end_week = datetime.date(int(end[:4]), int(end[5:7]), int(end[8:10]))
        
#         while begin_week <= end_week:
#             list_date.append(begin_week)
#             begin_week += datetime.timedelta(days=1)

#     # формируем сообщение 
#     text = f"➡️ {valid_text}\n"
#     is_find = False

#     # рассматриваем каждую дату
#     for date in list_date:
#         # расписание на сутки
#         all_data_from_date = await get_all_data_from_date(valid_text, date)
#         all_data_from_date = sorted(all_data_from_date, key = my_sort)
        
#         # если есть расписание на этот день, то отображаем
#         if len(all_data_from_date)>0:
#             # для каждой пары за один день
#             last_time = None
#             for i in range(len(all_data_from_date)):
#                 # инфа про одну пару
#                 date_pair = all_data_from_date[i][0]
#                 date_pair = datetime.date(int(date_pair[6:])+2000, int(date_pair[3:5]), int(date_pair[:2]))
#                 time_lesson = all_data_from_date[i][1]
#                 cabinet_number = all_data_from_date[i][2]
#                 name_of_group = all_data_from_date[i][3]
#                 name_teacher = all_data_from_date[i][4]
#                 name_of_discipline = all_data_from_date[i][5]
                
#                 # формируем соообщение
#                 if i == 0: # если за день первая пара
#                     text += f"\n➡️ {number_day_to_day_week[date_pair.weekday()]} | {date_pair.strftime('%d-%m-%Y')}:"
#                 if time_lesson != last_time:
#                     text += f"\n——/ {time_lesson} /——\n"
#                     last_time = time_lesson
#                 else:
#                     text += '\n'
#                 text += f"{name_of_group}\n" if name_of_group != None else ""
#                 text += f"{name_of_discipline}\n" if name_of_discipline != None else ""
#                 text += f"{name_teacher}\n" if name_teacher != None else ""
#                 text += f"{cabinet_number}\n" if cabinet_number != None else ""
#             # флаг, что что-то нашли
#             is_find = True
            
#     # если ничего не нашли, то ищем след. день
#     if is_find == False:
#         start = list_date[0]
#         text += f"\n➡️ {number_day_to_day_week[start.weekday()]} | {start.strftime('%d-%m-%Y')}"
#         if len(list_date)>1:
#             end = list_date[-1]
#             text += f"- {number_day_to_day_week[end.weekday()]} | {end.strftime('%d-%m-%Y')}:\n\n"
#         else:
#             text += ":\n\n"
        
#         # следущая дата
#         last_date = list_date[-1] + datetime.timedelta(days=1)
#         all_data_from_date = []
        
#         # пока не нашли следующий день с расписанием
#         count = 0
#         while len(all_data_from_date)==0 and count<100:
#             # расписание на сутки
#             all_data_from_date = await get_all_data_from_date(valid_text, last_date)
#             all_data_from_date = sorted(all_data_from_date, key = my_sort)
#             last_date += datetime.timedelta(days=1)
#             count += 1
            
#         # если что-то нашли
#         if len(all_data_from_date)>0:
#             text += "Пар нет\n\nСледующие пары:"
#         else:
#             text += "Больше нет пар!\n"
            
#         # для каждой пары за один день
#         last_time = None
#         for i in range(len(all_data_from_date)):
#             # инфа про одну пару
#             date_pair = all_data_from_date[i][0]
#             date_pair = datetime.date(int(date_pair[6:])+2000, int(date_pair[3:5]), int(date_pair[:2]))
#             time_lesson = all_data_from_date[i][1]
#             cabinet_number = all_data_from_date[i][2]
#             name_of_group = all_data_from_date[i][3]
#             name_teacher = all_data_from_date[i][4]
#             name_of_discipline = all_data_from_date[i][5]
                
#             # формируем соообщение
#             if i == 0: # если за день первая пара
#                 text += f"\n➡️ {number_day_to_day_week[date_pair.weekday()]} | {date_pair.strftime('%d-%m-%Y')}:"
#             if time_lesson != last_time:
#                 text += f"\n——/ {time_lesson} /——\n"
#                 last_time = time_lesson
#             else:
#                 text += '\n'
#             text += f"{name_of_group}\n" if name_of_group != None else ""
#             text += f"{name_of_discipline}\n" if name_of_discipline != None else ""
#             text += f"{name_teacher}\n" if name_teacher != None else ""
#             text += f"{cabinet_number}\n" if cabinet_number != None else ""
#     return text



# # получение клавиатуры для группы/преподавателя/кабинета (для периода - опционально)
# async def get_keyboard_and_text(valid_text, period=None) -> Union[InlineKeyboardMarkup, str]:
#     # получение всех дат
#     all_date = await get_all_date_for_valid_text(valid_text)
    
#     # сегодняшняя дата
#     current_date = datetime.date.today() + datetime.timedelta(hours=3)
    
#     # если нет свежего расписания
#     for date in all_date:
#         if date > current_date:
#             break 
#     else: 
#         return None, "Нет расписания!"
    
#     # есть расписание, делаем стандартные кнопки
#     button0 = InlineKeyboardButton(text=f'{valid_text}', callback_data=f'Обновить{valid_text}')
#     button1 = InlineKeyboardButton(text='Сегодня', callback_data=f'Сегод{valid_text}')
#     button2 = InlineKeyboardButton(text='Завтра', callback_data=f'Завтр{valid_text}')
#     button3 = InlineKeyboardButton(text='Послезавтра', callback_data=f'После{valid_text}')
#     inline_keyboard = [[button0],[button1, button2, button3]]
    
#     # формирование кнопок с неделями
#     last_date = all_date[-1] # последняя дата с расписанием
    
#     # понедельник текущей недели
#     first_day_week = current_date - datetime.timedelta(days=current_date.weekday())
    
#     # если сегодня воскресение, то не рассматриваем текущую неделю
#     if current_date.weekday()>=6:
#         first_day_week += datetime.timedelta(days=7)
        
#     # воскресение текущей недели
#     last_day_week = first_day_week + datetime.timedelta(days=6)
    
#     # рассматриваем все недели до самой последней даты в бд
#     while first_day_week < last_date:
#         # рассматривая неделя
#         date_current_week = [first_day_week + datetime.timedelta(days=i) for i in range(7)]
        
#         button1 = None
#         # проверяем - есть ли на рассматриваемой неделе пары
#         for date in date_current_week:
#             # если есть пары, то добавялем кнопку
#             if date in all_date:
#                 # пока на неделе есть расписание, то добавялем
#                 button1 = InlineKeyboardButton(text=f'{first_day_week.day}.{first_day_week.month}-{last_day_week.day}.{last_day_week.month} | Неделя', callback_data=f'Неделя{first_day_week}{valid_text}')
#                 break
        
#         first_day_week += datetime.timedelta(days=7)
#         last_day_week += datetime.timedelta(days=7)
        
#         # для кнопок в два ряда, добавляем следующую неделю, если она есть
#         if first_day_week < last_date:
#             # рассматривая неделя
#             date_current_week = [first_day_week + datetime.timedelta(days=i) for i in range(7)]
#             # проверяем -  есть ли на рассматриваемой неделе пары
#             for date in date_current_week:
#                 # если есть пары, то добавялем кнопку
#                 if date in all_date:
#                     # пока на неделе есть расписание, то добавялем
#                     button2 = InlineKeyboardButton(text=f'{first_day_week.day}.{first_day_week.month}-{last_day_week.day}.{last_day_week.month} | Неделя', callback_data=f'Неделя{first_day_week}{valid_text}')
#                     if button1:
#                         inline_keyboard.append([button1, button2])
#                     else:
#                         inline_keyboard.append([button2])
#                     break
#         elif button1:
#             inline_keyboard.append([button1])
#         first_day_week += datetime.timedelta(days=7)
#         last_day_week += datetime.timedelta(days=7)
        
#     # добавляем кнопку со всем расписанием
#     # понедельник текущей недели недели
#     # если сегодня воскресение, то не рассматриваем текущую неделю
#     if current_date.weekday()>=6:
#         current_date += datetime.timedelta(days=7)    
#     first_day_week = current_date - datetime.timedelta(days=current_date.weekday())
#     # воскресение последней недели
#     last_day_week = last_date - datetime.timedelta(days=last_date.weekday()) + datetime.timedelta(days=6)    
    
#     # кнопка со всем расписанием
#     if first_day_week < last_day_week:
#         button = InlineKeyboardButton(text=f'{first_day_week.day}.{first_day_week.month}-{last_day_week.day}.{last_day_week.month} | Расписание', callback_data=f'Всё{first_day_week}{last_day_week}{valid_text}')
#         inline_keyboard.append([button])
        
#     # формируем кнопки
#     keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    
#     # если периода нет, то просто изначальная клавиатура
#     if period == None:
#         text = f"Фильтры расписания для {valid_text}"
#     # иначе ищем раписание по выбранной дате и выводим в виде текста
#     else:
#         text = await get_schedule_by_date(valid_text, period)
#     return keyboard, text



# # обновление данных о пользователях
# async def update_users(message) -> None:
#     current_time = str(datetime.datetime.now())[:19]
#     base = sqlite3.connect("database.db")
#     cur = base.cursor()
    
#     user_id_from_db = cur.execute(f"SELECT id FROM users WHERE id={message.from_user.id}").fetchone()
#     if user_id_from_db == None:
#         cmd = "INSERT INTO users values(?,?,?,?,?,?)"
#         cur.execute(cmd,
#             (
#                 message.from_user.id,
#                 message.from_user.full_name,
#                 message.from_user.username,
#                 current_time,
#                 current_time,
#                 1,
#             )
#         )
#     else:
#         cmd = "UPDATE users SET fullname==?, username==?, last_time==?, count = count + 1 WHERE id=?"
#         cur.execute(
#             cmd,
#             (
#                 message.from_user.full_name,
#                 message.from_user.username,
#                 current_time,
#                 message.from_user.id,
#             ),
#         )
#     base.commit()
#     base.close()
    


# async def create_db() -> None:
#     base = sqlite3.connect("database.db")
#     base.execute( "CREATE TABLE IF NOT EXISTS users(id PRIMARY KEY, fullname TEXT, username TEXT, time_register TEXT, last_time TEXT, count INTEGER)")
#     base.commit()
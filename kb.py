from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dbrequests import get_list_groups, get_list_teachers, get_list_cabinet, get_all_date_for_valid_text, get_all_data_from_date
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


# получение возможного листа кнопок для выбора
async def get_list_schedule(text):
    if text == "." or text == "_" or text == "__":
        return []
    if "," in text:
        text = text.split(",")[0].strip()
    # список с валидными данными
    list_valid_data_for_buttons = []
    text = text.strip().lower()
    
    # получение списка возможных групп, преподов и кабинетов
    list_teachers_from_db = await get_list_teachers()
    list_cabinet_from_db = await get_list_cabinet()
    list_groups_from_db = await get_list_groups()
    
    # проверка на преподов
    for teacher in list_teachers_from_db:
        if text in teacher.split()[0].strip().lower() or text in teacher.strip().lower():
            list_valid_data_for_buttons.append(teacher)
    
    # если список не пуст, то возвращаем его
    if len(list_valid_data_for_buttons) > 0:
        list_valid_data_for_buttons.sort()
        return list_valid_data_for_buttons
    
    # проверка на кабинеты
    for cabinet in list_cabinet_from_db:
        if text == cabinet.strip().lower():
            list_valid_data_for_buttons.append(cabinet)
    
    # если список не пуст, то возвращаем его
    if len(list_valid_data_for_buttons) > 0:
        list_valid_data_for_buttons.sort()
        return list_valid_data_for_buttons
    
    # проверка на название групп
    for name_group in list_groups_from_db:
        if text == name_group.strip().lower():
            list_valid_data_for_buttons.append(name_group)
            return list_valid_data_for_buttons
        
    # добавляем необработанную строку сразу же в список, который дальше проверяем
    list_to_check = [text]

    # режем строку на куски, где разделителем является тире
    if text.find("-") > 0:
        input_split_dash = text.split("-")
        input_split_dash = [value.strip() for value in input_split_dash if value!="" and value!=" "]
        if len(input_split_dash)>1:
            list_symbol = ['б', 'м', 'а', 'с']
            for i in list_symbol:
                list_to_check.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
            list_to_check.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
            
    # если есть пробелы, то режем строку на куски по пробелам
    if any(char.isspace() for char in text):
        input_split_dash = text.split(" ")
        input_split_dash = [value.strip() for value in input_split_dash if value!=""]
        if len(input_split_dash)>1:
            list_symbol = ['б', 'м', 'а', 'с']
            for i in list_symbol:
                list_to_check.append(f"{input_split_dash[0]}{i}-{input_split_dash[1]}")
            list_to_check.append(f"{input_split_dash[0]}-{input_split_dash[1]}")
    
    # если нет не пробелов, не тире, просто одна строка (допустим: "подб3")
    if len(text.split())==1:
        number_course: str = text[-1]
        name_group: str = text[:-1]
        list_symbol = ['б', 'м', 'а', 'с']
        for i in list_symbol:
            list_to_check.append(f"{name_group}{i}-{number_course}")
        list_to_check.append(f"{name_group}-{number_course}")
        
    # поиск валидных групп
    for valid_value_from_db in list_groups_from_db:
        for value_for_check in list_to_check:
            if value_for_check in valid_value_from_db.lower() and valid_value_from_db not in list_valid_data_for_buttons:
                # если группа с номером подгруппы
                if len(valid_value_from_db.split())>1:
                    list_valid_data_for_buttons.append(valid_value_from_db.split()[0][:-1])
                else:
                    list_valid_data_for_buttons.append(valid_value_from_db)
    list_valid_data_for_buttons = list(set(list_valid_data_for_buttons))
    list_valid_data_for_buttons.sort()
    return list_valid_data_for_buttons


def sort(schedule_list):
    return sorted(schedule_list, key=lambda x: datetime.datetime.strptime(x.time_lesson.split("-")[0],'%H:%M').time())


# получение расписания по выбранной дате
async def get_schedule_by_date(valid_text, period):   
    # даты которые надо отобразить
    list_date = []
    if period=="Сегод": 
        list_date.append(datetime.datetime.today() + datetime.timedelta(hours=3))
    elif period=="Завтр":
        list_date.append(datetime.datetime.today() + datetime.timedelta(days=1, hours=3))
    elif period=="После":
        list_date.append(datetime.datetime.today() + datetime.timedelta(days=2, hours=3))
        
    # если другой период
    elif "Неделя" in period:
        begin_week: str = period[6:16]
        begin_week = datetime.datetime(int(begin_week[:4]), int(begin_week[5:7]), int(begin_week[8:10]))
        list_date = [begin_week + datetime.timedelta(days=i) for i in range(7)]
    elif "Всё" in period:
        begin: str = period[3:13]
        end: str = period[13:23]
        begin_week = datetime.datetime(int(begin[:4]), int(begin[5:7]), int(begin[8:10]))
        end_week = datetime.datetime(int(end[:4]), int(end[5:7]), int(end[8:10]))
        
        while begin_week <= end_week:
            list_date.append(begin_week)
            begin_week += datetime.timedelta(days=1)

    # формируем сообщение 
    text = f"➡️ {valid_text}\n"
    is_find = False
    
    # рассматриваем каждую дату
    for date in list_date:
        # расписание на сутки
        all_data_from_date = await get_all_data_from_date(valid_text, date)
        all_data_from_date = sort(all_data_from_date)
        
        # если есть расписание на этот день, то отображаем
        if len(all_data_from_date)>0:
            # для каждой пары за один день
            last_time = None
            for i in range(len(all_data_from_date)):
                # инфа про одну пару
                date_pair = all_data_from_date[i].date
                date_pair = datetime.datetime(int(date_pair[6:])+2000, int(date_pair[3:5]), int(date_pair[:2]))
                time_lesson = all_data_from_date[i].time_lesson
                cabinet_number = all_data_from_date[i].cabinet_number
                name_of_group = all_data_from_date[i].name_group
                name_teacher = all_data_from_date[i].name_teacher
                name_of_discipline = all_data_from_date[i].name_discipline
                
                # формируем соообщение
                if i == 0: # если за день первая пара
                    text += f"\n➡️ {number_day_to_day_week[date_pair.weekday()]} | {date_pair.strftime('%d-%m-%Y')}:"
                if time_lesson != last_time:
                    text += f"\n——/ {time_lesson} /——\n"
                    last_time = time_lesson
                else:
                    text += '\n'
                text += f"{name_of_group}\n" if name_of_group != None else ""
                text += f"{name_of_discipline}\n" if name_of_discipline != None else ""
                text += f"{name_teacher}\n" if name_teacher != None else ""
                text += f"{cabinet_number}\n" if cabinet_number != None else ""
            # флаг, что что-то нашли
            is_find = True
            
    # если ничего не нашли, то ищем след. день
    if is_find == False:
        start = list_date[0]
        text += f"\n➡️ {number_day_to_day_week[start.weekday()]} | {start.strftime('%d-%m-%Y')}"
        if len(list_date)>1:
            end = list_date[-1]
            text += f"- {number_day_to_day_week[end.weekday()]} | {end.strftime('%d-%m-%Y')}:\n\n"
        else:
            text += ":\n\n"
        
        # следущая дата
        last_date = list_date[-1] + datetime.timedelta(days=1)
        all_data_from_date = []
        
        # пока не нашли следующий день с расписанием
        count = 0
        while len(all_data_from_date)==0 and count<100:
            # расписание на сутки
            all_data_from_date = await get_all_data_from_date(valid_text, last_date)
            all_data_from_date = sort(all_data_from_date)
            last_date += datetime.timedelta(days=1)
            count += 1
            
        # если что-то нашли
        if len(all_data_from_date)>0:
            text += "Пар нет\n\nСледующие пары:"
        else:
            text += "Больше нет пар!\n"
            
        # для каждой пары за один день
        last_time = None
        for i in range(len(all_data_from_date)):
            # инфа про одну пару
            date_pair = all_data_from_date[i].date
            date_pair = datetime.datetime(int(date_pair[6:])+2000, int(date_pair[3:5]), int(date_pair[:2]))
            time_lesson = all_data_from_date[i].time_lesson
            cabinet_number = all_data_from_date[i].cabinet_number
            name_of_group = all_data_from_date[i].name_group
            name_teacher = all_data_from_date[i].name_teacher
            name_of_discipline = all_data_from_date[i].name_discipline
                
            # формируем соообщение
            if i == 0: # если за день первая пара
                text += f"\n➡️ {number_day_to_day_week[date_pair.weekday()]} | {date_pair.strftime('%d-%m-%Y')}:"
            if time_lesson != last_time:
                text += f"\n——/ {time_lesson} /——\n"
                last_time = time_lesson
            else:
                text += '\n'
            text += f"{name_of_group}\n" if name_of_group != None else ""
            text += f"{name_of_discipline}\n" if name_of_discipline != None else ""
            text += f"{name_teacher}\n" if name_teacher != None else ""
            text += f"{cabinet_number}\n" if cabinet_number != None else ""
    return text


# получение клавиатуры для группы/преподавателя/кабинета (для периода - опционально)
async def get_keyboard_and_text(valid_text, period=None):
    # получение всех дат
    all_date = await get_all_date_for_valid_text(valid_text)
    
    # сегодняшняя дата
    current_date = datetime.datetime.today() + datetime.timedelta(hours=3)
    
    # если нет свежего расписания
    for date in all_date:
        if date >= current_date:
            break 
    else: 
        return None, "Группа/преподаватель/аудитория не найден(а)\n\nПроверьте корректность данных и повторите попытку\n\nВозможно, расписание по Вашему запросу отсутствует"
    
    # есть расписание, делаем стандартные кнопки
    button0 = InlineKeyboardButton(text=f'{valid_text}', callback_data=f'Обновить{valid_text}')
    button1 = InlineKeyboardButton(text='Сегодня', callback_data=f'Сегод{valid_text}')
    button2 = InlineKeyboardButton(text='Завтра', callback_data=f'Завтр{valid_text}')
    button3 = InlineKeyboardButton(text='Послезавтра', callback_data=f'После{valid_text}')
    inline_keyboard = [[button0],[button1, button2, button3]]
    
    # формирование кнопок с неделями
    last_date = all_date[-1] # последняя дата с расписанием
    
    # понедельник текущей недели
    first_day_week = current_date - datetime.timedelta(days=current_date.date().weekday())
    
    # если сегодня суббота или воскресение, то не рассматриваем текущую неделю
    if current_date.date().weekday()>=5:
        first_day_week += datetime.timedelta(days=7)
        
    # воскресение текущей недели
    last_day_week = first_day_week + datetime.timedelta(days=6)

    # рассматриваем все недели до самой последней даты в бд
    list_button_week = []
    while first_day_week < last_date:
        date_current_week = [first_day_week + datetime.timedelta(days=i) for i in range(7)]
        # проверяем - есть ли на рассматриваемой неделе пары
        for date in date_current_week:
            # если есть пары, то добавялем кнопку
            if date.date() in [i.date() for i in all_date]:
                # пока на неделе есть расписание, то добавялем
                text = f'{first_day_week.day}.{first_day_week.month}-{last_day_week.day}.{last_day_week.month} | Неделя'
                callback_data = f'Неделя{first_day_week.date()}{valid_text}'
                if len(list_button_week)<2:
                    list_button_week.append(InlineKeyboardButton(text=text, callback_data=callback_data))
                if len(list_button_week)==2:
                    inline_keyboard.append(list_button_week)
                    list_button_week = []
                break
        first_day_week += datetime.timedelta(days=7)
        last_day_week += datetime.timedelta(days=7)
        
    if len(list_button_week)==1:
        inline_keyboard.append(list_button_week)

    if current_date.date().weekday()>=5:
        current_date += datetime.timedelta(days=7)   

    first_day_week = current_date - datetime.timedelta(days=current_date.date().weekday())
    last_day_week = last_date - datetime.timedelta(days=last_date.date().weekday()) + datetime.timedelta(days=6)    
    
    if first_day_week < last_day_week:
        text = f'{first_day_week.day}.{first_day_week.month}-{last_day_week.day}.{last_day_week.month} | Расписание'
        callback_data = f'Всё{first_day_week.date()}{last_day_week.date()}{valid_text}'
        button = InlineKeyboardButton(text=text, callback_data=callback_data)
        inline_keyboard.append([button])
        
    # формируем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    
    # если периода нет, то просто изначальная клавиатура
    if period == None:
        text = f"Фильтры расписания для {valid_text}"
    # иначе ищем раписание по выбранной дате и выводим в виде текста
    else:
        text = await get_schedule_by_date(valid_text, period)
    return keyboard, text
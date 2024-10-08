from models import async_session
from models import User, Shedule, Mailing
from sqlalchemy import select, update, delete
import datetime

def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper

@connection
async def update_user(session, message):
    tg_id =  message.from_user.id
    fullname = message.from_user.full_name
    username = message.from_user.username
    time_last = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user = await session.scalar(select(User).where(User.tg_id==tg_id))
    if not user:
        session.add(User(tg_id=tg_id, fullname=fullname, username=username, time_register=time_last,time_last=time_last, count=1))
    else:
        await session.execute(update(User).where(User.tg_id == tg_id).values(fullname=fullname,username=username,time_last=time_last,count=User.count + 1))
    await session.commit()

@connection
async def delete_outdated_schedules(session):
    two_weeks_ago = datetime.datetime.now() - datetime.timedelta(weeks=2)

    result = await session.execute(select(Shedule))

    old_schedules = result.scalars().all()

    for schedule in old_schedules:
        schedule_date = datetime.datetime.strptime(schedule.date, '%Y-%m-%d %H:%M:%S')
        if schedule_date <= two_weeks_ago:
            await session.delete(schedule)
    
    await session.commit()

@connection
async def update_schedule(session, date, time_lesson, cabinet_number, name_of_group, name_teacher, name_of_discipline, *, empty=False, many=False):
    # ищем записи в бд по конкретной дате, времени и кабинету
    query = select(Shedule).where(
        Shedule.date == date,
        Shedule.time_lesson == time_lesson,
        Shedule.cabinet_number == cabinet_number
    )
    data = (await session.execute(query)).scalars().all()

    # если пары нет сейчас, то возможно она есть в старом расписании - надо удалить
    if empty:
        # если записи есть, то удаляем их
        if data:
            delete_query = delete(Shedule).where(
                Shedule.date == date,
                Shedule.time_lesson == time_lesson,
                Shedule.cabinet_number == cabinet_number
            )
            await session.execute(delete_query)
            await session.commit()

    # если пара есть сейчас, то нужно заменить(если есть) или добавить(если нет)
    else:
        # если нет старых записей, то добавляем все группы на паре
        if not data:
            for i in range(len(name_of_group)):
                new_record = Shedule(
                    date=date,
                    time_lesson=time_lesson,
                    cabinet_number=cabinet_number,
                    name_group=name_of_group[i],
                    name_teacher=name_teacher[i],
                    name_discipline=name_of_discipline[i]
                )
                session.add(new_record)
            await session.commit()

        # если есть записи
        else:
            # если добавляется много записей, то удаляем все старые и добавляем все новые
            if many:
                delete_query = delete(Shedule).where(
                    Shedule.date == date,
                    Shedule.time_lesson == time_lesson,
                    Shedule.cabinet_number == cabinet_number
                )
                await session.execute(delete_query)
                await session.commit()

                for i in range(len(name_of_group)):
                    new_record = Shedule(
                        date=date,
                        time_lesson=time_lesson,
                        cabinet_number=cabinet_number,
                        name_group=name_of_group[i],
                        name_teacher=name_teacher[i],
                        name_discipline=name_of_discipline[i]
                    )
                    session.add(new_record)
                await session.commit()

            # если добавляется одна запись
            else:
                # если запись всего одна в бд, то просто заменяем
                if len(data) == 1:
                    update_query = (
                        update(Shedule)
                        .where(
                            Shedule.date == date,
                            Shedule.time_lesson == time_lesson,
                            Shedule.cabinet_number == cabinet_number
                        )
                        .values(
                            name_group=name_of_group[0],
                            name_teacher=name_teacher[0],
                            name_discipline=name_of_discipline[0]
                        )
                    )
                    await session.execute(update_query)
                    await session.commit()

                # если записей много в бд, но добавляется одна
                else:
                    # удаляем все
                    delete_query = delete(Shedule).where(
                        Shedule.date == date,
                        Shedule.time_lesson == time_lesson,
                        Shedule.cabinet_number == cabinet_number
                    )
                    await session.execute(delete_query)
                    await session.commit()

                    # добавляем одну запись
                    new_record = Shedule(
                        date=date,
                        time_lesson=time_lesson,
                        cabinet_number=cabinet_number,
                        name_group=name_of_group[0],
                        name_teacher=name_teacher[0],
                        name_discipline=name_of_discipline[0]
                    )
                    session.add(new_record)
                    await session.commit()

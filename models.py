from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///database.db')

async_session = async_sessionmaker(engine, class_=AsyncSession)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer)
    fullname: Mapped[str] = mapped_column(String(50), nullable=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    time_register: Mapped[str] = mapped_column(String(50), nullable=True)
    time_last: Mapped[str] = mapped_column(String(50), nullable=True)
    count: Mapped[int] = mapped_column(nullable=True)

class Shedule(Base):
    __tablename__ = 'shedules'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String(50), nullable=True)
    time_lesson: Mapped[str] = mapped_column(String(50), nullable=True)
    cabinet_number: Mapped[str] = mapped_column(String(50), nullable=True)
    name_group: Mapped[str] = mapped_column(String(50), nullable=True)
    name_teacher: Mapped[str] = mapped_column(String(50), nullable=True)
    name_discipline: Mapped[str] = mapped_column(String(50), nullable=True)

class Mailing(Base):
    __tablename__ = 'mailing'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name_group: Mapped[str] = mapped_column(String(50))
    time: Mapped[str] = mapped_column(String(50))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
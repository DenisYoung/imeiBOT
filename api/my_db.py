from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Column, Integer, Table, TIMESTAMP, MetaData, BOOLEAN 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()
metadata = MetaData()


class Imei_checks(Base):
    __tablename__ = 'imei_checks'
    __table__ = Table(
        'imei_checks', metadata,
        Column('id', Integer, primary_key=True),
        Column('imei', String, unique=True, nullable=False),
        Column('check_status', BOOLEAN, default=None),
        Column('check_details', JSONB, default=None),
        Column('checked_at', TIMESTAMP, default=None),
    )

engine = create_async_engine(
    'postgresql+asyncpg://postgres:2131@db:5432/postgres', echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def add_check(imei: str, check_status: bool, check_details: JSONB):
    try:
        async with async_session() as session:
            async with session.begin():
                check = Imei_checks(imei=imei, check_status=check_status, check_details=check_details)
                session.add(check)
            await session.commit()
    except Exception as e:
        print(f"Ошибка при добавлении записи в базу данных: {e}")
        raise


async def find_check(imei: str):
    async with async_session() as session:
        query = select(Imei_checks).where(Imei_checks.imei == imei)
        result = await session.execute(query)
        row = result.fetchone()
        if row is None:
            return None
        return row[0].check_details

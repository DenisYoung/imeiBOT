from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import BigInteger, Column, Integer, Table, TIMESTAMP, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

Base = declarative_base()
metadata = MetaData()


class AllowedUser(Base):
    __tablename__ = 'allowed_users'
    __table__ = Table(
        'allowed_users', metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', BigInteger, unique=True, nullable=False),
        Column('added_at', TIMESTAMP, default=None),
    )


engine = create_async_engine(
    'postgresql+asyncpg://postgres:2131@db:5432/postgres')
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def allow_user(user_id: int):
    async with async_session() as session:
        async with session.begin():
            user = AllowedUser(user_id=user_id)
            session.add(user)
        await session.commit()

async def check_user(user_id: int) -> bool:
    async with async_session() as session:
        query = select(AllowedUser).where(AllowedUser.user_id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

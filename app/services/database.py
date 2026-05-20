from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session


async def save(db: AsyncSession, obj) -> None:
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
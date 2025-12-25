from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_database_session():
    async with async_session_maker() as session:
        yield session


async def initialize_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

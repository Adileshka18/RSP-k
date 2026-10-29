from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from backend.core.config import get_database_url, get_sql_echo


engine = create_async_engine(
    get_database_url(),
    echo=get_sql_echo(),
    pool_pre_ping=True,
    poolclass=NullPool,
    future=True,
)


async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

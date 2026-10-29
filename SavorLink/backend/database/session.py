import asyncio
import logging
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.core.config import get_db_config, get_sql_echo


logger = logging.getLogger(__name__)

CONNECT_ATTEMPTS = 10
CONNECT_FIRST_DELAY_SECONDS = 1
CONNECT_MAX_DELAY_SECONDS = 10
CONNECT_TIMEOUT_SECONDS = 5
HEALTH_CHECK_TIMEOUT_SECONDS = 2

db_config = get_db_config()

# Пул ограничен DB_MAX_CONNS: больше этого числа соединений к PostgreSQL не откроется
# (max_overflow=0), а лишние запросы подождут свободное соединение до pool_timeout секунд.
engine = create_async_engine(
    db_config.url(),
    echo=get_sql_echo(),
    pool_size=db_config.max_conns,
    max_overflow=0,
    pool_timeout=30,
    pool_pre_ping=True,
    connect_args={"timeout": CONNECT_TIMEOUT_SECONDS},
)


async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def ping_database() -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def wait_for_database() -> None:
    """Ждёт готовности PostgreSQL при старте: повторяет попытки с растущей паузой."""
    delay = CONNECT_FIRST_DELAY_SECONDS
    for attempt in range(1, CONNECT_ATTEMPTS + 1):
        try:
            await ping_database()
            return
        except Exception as exc:
            if attempt == CONNECT_ATTEMPTS:
                raise
            logger.warning(
                "База данных %s:%s недоступна (попытка %s из %s): %s. Повтор через %s с",
                db_config.host,
                db_config.port,
                attempt,
                CONNECT_ATTEMPTS,
                exc,
                delay,
            )
            await asyncio.sleep(delay)
            delay = min(delay * 2, CONNECT_MAX_DELAY_SECONDS)


async def is_database_available() -> bool:
    try:
        async with asyncio.timeout(HEALTH_CHECK_TIMEOUT_SECONDS):
            await ping_database()
        return True
    except Exception as exc:
        logger.warning("Проверка здоровья: база данных недоступна: %s", exc)
        return False

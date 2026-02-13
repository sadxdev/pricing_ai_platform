from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from app.core.config import settings
from typing import AsyncGenerator


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
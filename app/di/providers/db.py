from typing import AsyncIterable

from dishka import Provider, Scope, provide
from dishka.integrations.fastapi import FromDishka
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine,)

from app.core.config import settings

class DBProvider(Provider):

    @provide(scope=Scope.APP)
    def provide_engine(self) -> AsyncEngine:
        return create_async_engine(settings.database_url, echo=settings.ECHO)

    @provide(scope=Scope.APP)
    def provide_session_maker(
        self, engine: FromDishka[AsyncEngine]
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self, session_maker: FromDishka[async_sessionmaker[AsyncSession]]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

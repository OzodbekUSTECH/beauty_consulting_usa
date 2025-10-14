from dishka import Provider, Scope, provide
from dishka.integrations.fastapi import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.users import UsersRepository
from app.repositories.uow import UnitOfWork


class RepositoriesProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def provide_uow_repository(self, session: FromDishka[AsyncSession]) -> UnitOfWork:
        return UnitOfWork(session)

    @provide(scope=Scope.REQUEST)
    def provide_users_repository(self, session: FromDishka[AsyncSession]) -> UsersRepository:
        return UsersRepository(session)

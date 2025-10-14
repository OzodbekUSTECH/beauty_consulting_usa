from dishka import Provider, Scope, provide
from dishka.integrations.fastapi import FromDishka

from app.interactors.users.get import GetAllUsersInteractor, GetUserByTgIdInteractor
from app.interactors.users.update import UpdateUserInteractor
from app.repositories.uow import UnitOfWork
from app.repositories.users import UsersRepository


class UsersInteractorProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def provide_get_all(
            self,
            users_repo: FromDishka[UsersRepository],
    ) -> GetAllUsersInteractor:
        return GetAllUsersInteractor(
            users_repo=users_repo,
        )

    @provide(scope=Scope.REQUEST)
    def provide_get_by_tg_id(
            self,
            users_repo: FromDishka[UsersRepository],
    ) -> GetUserByTgIdInteractor:
        return GetUserByTgIdInteractor(
            users_repo=users_repo,
        )

    @provide(scope=Scope.REQUEST)
    def provide_update(
            self,
            uow: FromDishka[UnitOfWork],
            users_repo: FromDishka[UsersRepository],
    ) -> UpdateUserInteractor:
        return UpdateUserInteractor(
            uow=uow,
            users_repo=users_repo,
        )
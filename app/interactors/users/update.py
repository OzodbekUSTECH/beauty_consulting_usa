from app.dto.users import UserResponse, UpdateUserRequest
from app.entities import User
from app.exceptions.app_error import AppError
from app.exceptions.messages import ErrorMessages
from app.repositories.uow import UnitOfWork
from app.repositories.users import UsersRepository


class UpdateUserInteractor:

    def __init__(
            self,
            uow: UnitOfWork,
            users_repo: UsersRepository,
    ) -> None:
        self.uow = uow
        self.users_repo = users_repo


    async def execute(self, request: UpdateUserRequest) -> UserResponse:
        user = await self.users_repo.get_one(
            where=[User.tg_id == request.tg_id]
        )
        if not user:
            raise AppError(404, ErrorMessages.NOT_FOUND)
        user.is_active = request.is_active
        await self.uow.commit()
        return UserResponse.model_validate(user)
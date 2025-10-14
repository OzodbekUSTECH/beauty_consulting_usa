from app.dto.users import UserResponse, GetUsersParams
from app.entities import User
from app.exceptions.app_error import AppError
from app.exceptions.messages import ErrorMessages
from app.repositories.users import UsersRepository


class GetAllUsersInteractor:

    def __init__(
            self,
            users_repo: UsersRepository,
    ) -> None:
        self.users_repo = users_repo


    async def execute(self, request: GetUsersParams) -> list[UserResponse]:
        where = []
        if request.filter_by and request.filter:
            if request.filter_by == 'tg_id':
                where.append(User.tg_id == request.filter)
            elif request.filter_by == 'name':
                where.append(User.name.ilike(f"%{request.filter}%"))
            elif request.filter_by == 'username':
                where.append(User.username.ilike(f"%{request.filter}%"))
            elif request.filter_by == 'phone_number':
                where.append(User.phone_number.ilike(f"%{request.filter}%"))

        users = await self.users_repo.get_all(where=where)

        return [UserResponse.model_validate(user) for user in users]

class GetUserByTgIdInteractor:

    def __init__(
            self,
            users_repo: UsersRepository,
    ) -> None:
        self.users_repo = users_repo


    async def execute(self, tg_id: str) -> UserResponse:
        user = await self.users_repo.get_one(where=[User.tg_id == tg_id])
        if not user:
            raise AppError(404, ErrorMessages.NOT_FOUND)
        return UserResponse.model_validate(user)
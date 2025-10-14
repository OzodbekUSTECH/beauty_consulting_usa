from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Form
from dishka import FromDishka
from fastapi.params import Depends

from app.dto.users import UserResponse, UpdateUserRequest, GetUsersParams
from app.interactors.users.get import GetAllUsersInteractor, GetUserByTgIdInteractor
from app.interactors.users.update import UpdateUserInteractor

router = APIRouter(prefix="/users", tags=["Users"], route_class=DishkaRoute)

@router.get("/")
async def get_users(
    request: Annotated[GetUsersParams, Depends()],
    get_users_interactor: FromDishka[GetAllUsersInteractor],
) -> list[UserResponse]:
    return await get_users_interactor.execute(request)


@router.get("/{tg_id}")
async def get_user_by_tg_id(
    tg_id: str,
    get_user_by_tg_id_interactor: FromDishka[GetUserByTgIdInteractor],
) -> UserResponse:
    return await get_user_by_tg_id_interactor.execute(tg_id)




@router.patch("/{tg_id}")
async def update_user(
        tg_id: str,
        is_active: Annotated[bool, Form()],
        update_user_interactor: FromDishka[UpdateUserInteractor]
) -> UserResponse:
    request = UpdateUserRequest(tg_id=tg_id, is_active=is_active)

    user = await update_user_interactor.execute(request)
    return user
from typing import Optional
from pydantic import BaseModel

from app.dto.common import BaseModelResponse


class UpdateUserRequest(BaseModel):
    tg_id: str
    is_active: bool

class UserResponse(BaseModelResponse):
    tg_id: str
    name: Optional[str]
    username: Optional[str]
    phone_number: Optional[str]
    is_active: bool


class GetUsersParams(BaseModel):
    filter_by: Optional[str] = None
    filter: Optional[str] = None
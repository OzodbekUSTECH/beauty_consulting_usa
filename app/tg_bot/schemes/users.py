from pydantic import BaseModel
from uuid import UUID


class UserResponse(BaseModel):
    id: UUID
    tg_id: str
    phone_number: str | None
    name: str | None
    username: str | None
    is_active: bool

from uuid import UUID

from openai import BaseModel


class BaseModelResponse(BaseModel):
    id: UUID

    class Config:
        from_attributes = True
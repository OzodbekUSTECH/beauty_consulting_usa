from sqlalchemy.ext.asyncio import AsyncSession

from app.entities import User
from app.repositories.base import BaseRepository


class UsersRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)




from dishka import make_async_container

from app.di.providers.db import DBProvider
from app.di.providers.interactors.ai import AIAssistantProvider
from app.di.providers.interactors.users import UsersInteractorProvider
from app.di.providers.repositories import RepositoriesProvider
from app.di.providers.utils import UtilsProvider

container = make_async_container(
    DBProvider(),
    RepositoriesProvider(),
    UtilsProvider(),
    AIAssistantProvider(),
    UsersInteractorProvider()
)


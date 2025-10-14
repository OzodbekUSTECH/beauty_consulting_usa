from aiogram import Bot
from dishka import Provider, Scope, provide
from openai import AsyncOpenAI
from dishka.integrations.fastapi import FromDishka

from app.interactors.ai.create import CreatePromptInteractor
from app.repositories.uow import UnitOfWork
from app.repositories.users import UsersRepository


class AIAssistantProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def provide_get_response(
            self,
            openai_client: FromDishka[AsyncOpenAI],
            uow: FromDishka[UnitOfWork],
            aiogram_bot: FromDishka[Bot],
            users_repo: FromDishka[UsersRepository],
    ) -> CreatePromptInteractor:
        return CreatePromptInteractor(
            openai_client=openai_client,
            uow=uow,
            users_repo=users_repo,
            aiogram_bot=aiogram_bot,
        )
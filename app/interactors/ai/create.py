import asyncio
import json
import logging
from aiogram import Bot
from openai import AsyncOpenAI
from openai.types.beta import CodeInterpreterTool
from openai.types.beta.threads import ImageFileContentBlock
from openai.types.beta.threads.message import Attachment, AttachmentToolAssistantToolsFileSearchTypeOnly, AttachmentTool
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput
from app.core.config import settings
from app.dto.ai import CreatePromptRequest, AssistantResponse
from app.entities import User
from app.repositories.uow import UnitOfWork
from app.repositories.users import UsersRepository
from aiogram.enums import ParseMode

logger = logging.getLogger("app.interactors.ai.create")

class CreatePromptInteractor:
    def __init__(
            self,
            uow: UnitOfWork,
            openai_client: AsyncOpenAI,
            users_repo: UsersRepository,
            aiogram_bot: Bot,
    ) -> None:
        self.openai_client = openai_client
        self.uow = uow
        self.users_repo = users_repo
        self.aiogram_bot = aiogram_bot

    async def execute(self, request: CreatePromptRequest) -> AssistantResponse:
        logger.info("Executing prompt creation for user: %s", request.tg_id)
        user = await self._get_or_create_user(request)

        if not user.is_active:
            logger.warning("User is inactive: %s", request.tg_id)
            return AssistantResponse()

        message = await self.openai_client.beta.threads.messages.create(
            thread_id=user.thread_id,
            role="user",
            content=request.prompt,
            timeout=settings.OPENAI_TIMEOUT,
        )
        logger.info("Message sent to OpenAI: %s", request.prompt)

        run = await self.openai_client.beta.threads.runs.create(
            thread_id=user.thread_id,
            assistant_id=settings.ASSISTANT_ID,
        )

        response_message = await self._process_run(user, run, message.id)
        await self.uow.commit()
        logger.info("Prompt execution completed for user: %s", request.tg_id)
        return AssistantResponse(response=response_message)

    async def _get_or_create_user(self, request: CreatePromptRequest) -> User:
        logger.info("Retrieving or creating user: %s", request.tg_id)
        user = await self.users_repo.get_one(
            where=[
                User.tg_id == request.tg_id,
            ]
        )
        if not user:
            logger.info("User not found, creating new user: %s", request.tg_id)
            thread = await self.openai_client.beta.threads.create()
            user = User(
                **request.model_dump(exclude={"prompt"}),
                thread_id=thread.id,
            )
            await self.users_repo.create(user)
        return user

    async def _process_run(self, user: User, run, after_message_id: str) -> str | None:
        try:
            logger.info("Processing run for user: %s", user.tg_id)

            while run.status not in ["completed", "failed", "expired", "cancelled"]:
                run = await self.openai_client.beta.threads.runs.retrieve(
                    thread_id=user.thread_id, run_id=run.id
                )
                if run.status == "requires_action":
                    logger.info("Run requires action: %s", run.id)
                    ignore = await self._handle_required_actions(
                        run.required_action.submit_tool_outputs.model_dump(), run.id, user
                    )

                    if ignore:
                        logger.info("Ignoring run response for user: %s due to unrelated message", user.tg_id)
                        return None
                await asyncio.sleep(0.5)

            if run.status == "completed":
                messages = await self.openai_client.beta.threads.messages.list(
                    thread_id=user.thread_id, order="asc", after=after_message_id
                )
                logger.info("Run completed successfully, returning response.")
                return messages.data[0].content[0].text.value
            elif run.status == "failed":
                logger.error("Run failed for user: %s", user.tg_id)
                return None
            elif run.status in ["expired", "cancelled"]:
                logger.warning("Run expired or cancelled for user: %s", user.tg_id)
                return None

            return None
        except Exception as e:
            logger.exception("Exception occurred while processing run for user: %s. Error: %s", user.tg_id, e)
            return None

    async def _handle_required_actions(self, required_actions, run_id, user: User) -> bool:
        tool_outputs = []
        should_ignore = False  # <-- флаг, чтобы сообщить, что оффтоп

        try:
            logger.info("Handling required actions for run: %s", run_id)
            for action in required_actions["tool_calls"]:
                func_name = action["function"]["name"]
                arguments = json.loads(action["function"]["arguments"])

                if func_name == "collect_client_info":
                    logger.info("Telegram-ready message received for action: %s", action["id"])
                    msg_notification = arguments["message"]
                    user.is_active = False

                    tool_outputs.append(
                        ToolOutput(tool_call_id=action["id"], output=msg_notification)
                    )
                    await self._send_notification(msg_notification)

                elif func_name == "handle_unrelated_message":
                    logger.info("Received unrelated message, will ignore response for user: %s", user.tg_id)
                    should_ignore = True  # <-- выставляем флаг
                    tool_outputs.append(
                        ToolOutput(
                            tool_call_id=action["id"],
                            output="Игнорируем оффтоп-сообщение от пользователя."
                        )
                    )

        except Exception as e:
            logger.exception("Exception occurred while handling required actions for run: %s. Error: %s", run_id, e)
            raise e
        finally:
            await self.openai_client.beta.threads.runs.submit_tool_outputs(
                thread_id=user.thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            logger.info("Submitted tool outputs for run: %s", run_id)

        return should_ignore

    async def _send_notification(self, message: str, disable_parse_mode: bool = False):
        """Отправляет уведомление в Telegram, отключая разметку, если требуется."""
        parse_mode = None if disable_parse_mode else ParseMode.HTML
        for chat_id in settings.CHAT_IDS:
            try:
                await self.aiogram_bot.send_message(chat_id, message, parse_mode=parse_mode)
                logger.info("Notification sent to chat ID: %s", chat_id)
            except Exception as e:
                logger.exception("Failed to send notification to chat ID: %s. Error: %s", chat_id, e)
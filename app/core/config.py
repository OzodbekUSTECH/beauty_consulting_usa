import logging

from pydantic import Field
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    API_ID: int
    API_HASH: str
    PHONE_NUMBER: str
    SESSION_NAME: str

    ASSISTANT_ID: str

    OPENAI_API_KEY: str

    # Указываем путь к базе данных sqlite относительно корня проекта
    SQLITE_DB_PATH: str = os.path.join("data", "db.sqlite3")

    STRING_SESSION: Optional[str] = None

    ECHO: bool = False

    CHAT_IDS: list[str] = []

    ASSISTANT_ID: str

    OPENAI_API_KEY: str

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_DB: int = 0

    OPENAI_TIMEOUT: int = 60

    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["*"]
    TTL: int = 5
    MESSAGE_EXPIRATION_HOURS: int = 6

    DOCS_USERNAME: str
    DOCS_PASSWORD: str

    # --- tg bot ---
    BOT_TOKEN: str
    ALLOWED_USER_IDS: list[str] = Field(default_factory=list)

    @property
    def database_url(self):
        # абсолютный путь для корректного подключения (для docker и локально)
        db_full_path = os.path.abspath(self.SQLITE_DB_PATH)
        return f"sqlite+aiosqlite:///{db_full_path}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


def configure_logging(level = logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

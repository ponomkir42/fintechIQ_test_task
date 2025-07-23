from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    development = "development"
    production = "production"


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8"
    )

    SERVICE_NAME: str = "blacklist_service"
    LOGS_PATH: str = "/runtime/logs"

    POSTGRES_ECHO: bool = False
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    POSTGRES_URL: str = "postgresql+asyncpg://user:password@postgresql:5432/db-name"
    POSTGRES_TESTS_URL: str = "postgresql+asyncpg://user:password@postgresql:5432/db-name_tests"

    RABBIT_USER: str
    RABBIT_PASSWORD: str
    RABBIT_HOST: str

    RABBIT_URL: str = "amqp://user:password@rabbit/"

    RABBIT_QUEUE: str = "blacklist_queue"


config = Config()

config.POSTGRES_URL = f"postgresql+asyncpg://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
config.POSTGRES_TESTS_URL = f"postgresql+asyncpg://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}_tests"
config.RABBIT_URL = f"amqp://{config.RABBIT_USER}:{config.RABBIT_PASSWORD}@{config.RABBIT_HOST}//"

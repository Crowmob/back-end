from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class PostgresConfig(BaseConfig):
    PORT: int = Field(..., alias="POSTGRES_PORT")
    USER: str = Field(..., alias="POSTGRES_USER")
    PASSWORD: str = Field(..., alias="POSTGRES_PASSWORD")
    DB: str = Field(..., alias="POSTGRES_DB")
    URL: str = Field(..., alias="POSTGRES_URL")


class RedisConfig(BaseConfig):
    PORT: str = Field(..., alias="REDIS_PORT")
    HOST: str = Field(..., alias="REDIS_HOST")


class Settings(BaseConfig):
    HOST: str
    PORT: int
    RELOAD: bool

    db: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()


settings = Settings()
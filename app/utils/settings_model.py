from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class PostgresConfig(BaseConfig):
    PORT: int = Field(..., alias="POSTGRES_PORT")
    USER: str = Field(..., alias="POSTGRES_USER")
    PASSWORD: str = Field(..., alias="POSTGRES_PASSWORD")
    DB: str = Field(..., alias="POSTGRES_DB")
    TEST_DB: str = Field(..., alias="TEST_POSTGRES_DB")
    URL: str = Field(..., alias="POSTGRES_URL")
    TEST_URL: str = Field(..., alias="TEST_POSTGRES_URL")

    def get_url(self, env: str) -> str:
        return self.TEST_URL if env == "test" else self.URL


class RedisConfig(BaseConfig):
    PORT: str = Field(..., alias="REDIS_PORT")
    HOST: str = Field(..., alias="REDIS_HOST")


class AuthConfig(BaseConfig):
    AUTH0_ALGORITHM: str
    AUTH0_DOMAIN: str
    API_AUDIENCE: str
    CLIENT_ID: str
    CLIENT_SECRET: str


class Settings(BaseConfig):
    ENV: str
    HOST: str
    PORT: int
    RELOAD: bool
    REACT_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    EXP_TIME: int

    db: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()
    auth: AuthConfig = AuthConfig()


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    HOST: str
    PORT: int
    RELOAD: bool
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_URL: str
    REDIS_PORT: int
    REDIS_HOST: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    HOST: str
    PORT: int
    RELOAD: bool

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
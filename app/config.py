from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://icps:icps_secret@127.0.0.1:5434/icps_master"
    port: int = 8000


settings = Settings()

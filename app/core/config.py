from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AlToque AI"

    DATABASE_URL: str = (
        "postgresql+psycopg://altoque:altoque@localhost:5432/altoque"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
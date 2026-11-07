from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The placeholder from .env.example is public: a copied template must not start the app.
TEMPLATE_SECRET_PREFIX = "change-me"


class Settings(BaseSettings):
    database_url: str
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    db_echo: bool = False
    log_level: str = "INFO"
    # JSON list, e.g. CORS_ORIGINS=["http://localhost:5173"]; empty means CORS is off.
    cors_origins: list[str] = []

    @field_validator("secret_key")
    @classmethod
    def secret_key_is_not_template(cls, value: str) -> str:
        if value.lower().startswith(TEMPLATE_SECRET_PREFIX):
            raise ValueError("Замените SECRET_KEY из .env.example на свой случайный ключ")

        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()

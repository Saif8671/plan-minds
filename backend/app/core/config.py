from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AI Schedule Organizer"
    app_version: str = "1.0.0"
    environment: str = "production"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    run_scheduler: bool = True

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/schedule_organizer"
    )
    # Database connection pool settings
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800  # Recycle connections every 30 min

    secret_key: str = "change-me-to-a-long-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    firebase_project_id: str = ""
    firebase_service_account_path: str = ""
    firebase_service_account_json: str = ""

    vapid_private_key: str = ""
    vapid_email: str = "mailto:admin@example.com"

    smtp_hostname: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = False
    smtp_from_email: str = "noreply@example.com"

    groq_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GROQ_API_KEY", "OPENAI_API_KEY"),
    )
    groq_model: str = Field(
        default="llama-3.1-8b-instant",
        validation_alias=AliasChoices("GROQ_MODEL", "OPENAI_MODEL"),
    )

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]
    log_level: str = "INFO"

    # Optional integrations
    redis_url: str = ""  # For Celery/caching (future use)
    sentry_dsn: str = ""  # For error monitoring (Sentry)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            import json

            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_flag(cls, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}:
                return True
            if normalized in {
                "0",
                "false",
                "no",
                "off",
                "release",
                "production",
                "prod",
            }:
                return False
        return bool(value)

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @field_validator("secret_key", mode="after")
    @classmethod
    def validate_secret_key(cls, value: str, info) -> str:
        env = info.data.get("environment", "production")
        if env != "development" and value in {
            "change-me-to-a-long-random-secret-key",
            "dev-secret-key-placeholder",
        }:
            raise ValueError(
                "SECRET_KEY must be changed from the default in production!"
            )
        return value

    @field_validator("database_url", mode="after")
    @classmethod
    def validate_database_url(cls, value: str, info) -> str:
        env = info.data.get("environment", "production")
        if env != "development" and not value:
            raise ValueError("DATABASE_URL must be provided in production!")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

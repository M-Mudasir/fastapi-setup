from decimal import Decimal
import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_PREFIX: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 2 days = 2 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2
    FRONTEND_URL: str = "localhost:3000"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_URL
        ]
    
    SERVER_URL: str = "http://localhost:8000"
    USER_REGISTRATION: bool = False

    PROJECT_NAME: str
    ENABLE_ADMIN_PANEL: bool = False

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    # Okta SSO
    OKTA_BASE_URL: str = ""
    OKTA_AUTH_CLIENT_ID: str = ""
    OKTA_AUTH_CLIENT_SECRET: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI_SYNC(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    ACS_SENDER_EMAIL: str | None = None
    ACS_CONNECTION_STRING: str | None = None

    # TODO: update type to EmailStr when sqlmodel supports it

    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.EMAIL_LOGIC_APP_URL and self.EMAIL_LOGIC_APP_KEY)

    ADMIN_SUPERUSER: str
    ADMIN_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("ADMIN_SUPERUSER_PASSWORD", self.ADMIN_SUPERUSER_PASSWORD)

        return self
    
    REDIS_URL: str = "redis://localhost:6379/0"

    # TODO: uncomment this when we have a background task to run
    # SERVICE_BUS_SAS_KEY: str = ""
    # SERVICE_BUS_SAS_POLICY: str = ""
    # SERVICE_BUS_NAMESPACE: str = ""
    

    EMAIL_LOGIC_APP_URL: str = ""
    EMAIL_LOGIC_APP_KEY: str = ""

    SUPPORT_EMAIL: str = ""

    # SSO
    OKTA_BASE_URL: str = "" 
    OKTA_AUTH_CLIENT_ID: str = ""
    OKTA_AUTH_CLIENT_SECRET: str = ""
 
    GOOGLE_AUTH_CLIENT_ID: str = ""
    GOOGLE_AUTH_CLIENT_SECRET: str = ""

    LINKEDIN_AUTH_CLIENT_ID: str = ""
    LINKEDIN_AUTH_CLIENT_SECRET: str = ""

    MICROSOFT_AUTH_CLIENT_ID: str = ""
    MICROSOFT_AUTH_CLIENT_SECRET: str = ""
    MICROSOFT_AUTH_TENANT_ID: str = ""

settings = Settings()  # type: ignore

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy.engine import URL


load_dotenv()


REQUIRED_DB_VARS = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
DEFAULT_DB_PORT = 5432
DEFAULT_DB_MAX_CONNS = 10


class ConfigError(Exception):
    """Конфигурация приложения задана неверно — запускаться дальше нельзя."""


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    name: str
    max_conns: int

    def url(self, driver: str = "asyncpg") -> str:
        # URL.create сам экранирует спецсимволы в пароле (@, :, / и т.п.)
        return URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        ).render_as_string(hide_password=False)


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def get_required_env(name: str) -> str:
    value = get_env(name)
    if not value:
        raise ConfigError(f"{name} не задана в переменных окружения")
    return value


def _get_positive_int_env(name: str, default: int) -> int:
    raw = get_env(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ConfigError(f"{name} должна быть целым числом, сейчас: {raw!r}") from None
    if value <= 0:
        raise ConfigError(f"{name} должна быть больше 0, сейчас: {value}")
    return value


@lru_cache
def get_db_config() -> DatabaseConfig:
    missing = [name for name in REQUIRED_DB_VARS if not get_env(name)]
    if missing:
        raise ConfigError(
            "не заданы обязательные переменные окружения: "
            + ", ".join(missing)
            + ". Скопируйте .env.example в .env и заполните значения."
        )

    return DatabaseConfig(
        host=get_env("DB_HOST"),
        port=_get_positive_int_env("DB_PORT", DEFAULT_DB_PORT),
        user=get_env("DB_USER"),
        password=get_env("DB_PASSWORD"),
        name=get_env("DB_NAME"),
        max_conns=_get_positive_int_env("DB_MAX_CONNS", DEFAULT_DB_MAX_CONNS),
    )


def get_database_url() -> str:
    return get_db_config().url("asyncpg")


def get_sync_database_url() -> str:
    return get_db_config().url("psycopg2")


def get_backend_host() -> str:
    return get_env("BACKEND_HOST", "0.0.0.0") or "0.0.0.0"


def get_backend_port() -> int:
    return int(get_env("BACKEND_PORT", "8002") or "8002")


def get_backend_reload() -> bool:
    return (get_env("BACKEND_RELOAD", "true") or "true").lower() == "true"


def get_backend_log_level() -> str:
    return get_env("BACKEND_LOG_LEVEL", "info") or "info"


def get_sql_echo() -> bool:
    return (get_env("SQL_ECHO", "false") or "false").lower() == "true"


def get_auth_token_secret() -> str:
    return get_env("AUTH_TOKEN_SECRET", "dev-auth-token-secret") or "dev-auth-token-secret"


def get_auth_token_ttl_seconds() -> int:
    return int(get_env("AUTH_TOKEN_TTL_SECONDS", "604800") or "604800")

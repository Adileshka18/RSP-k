import os

from dotenv import load_dotenv
from sqlalchemy.engine import make_url


load_dotenv()


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def get_required_env(name: str) -> str:
    value = get_env(name)
    if not value:
        raise ValueError(f"{name} не задана в переменных окружения")
    return value


def get_database_url() -> str:
    return get_required_env("DATABASE_URL")


def get_sync_database_url() -> str:
    url = make_url(get_database_url())
    if url.drivername.endswith("+asyncpg"):
        url = url.set(drivername=url.drivername.replace("+asyncpg", "+psycopg2"))
    elif "+" not in url.drivername:
        url = url.set(drivername=f"{url.drivername}+psycopg2")
    return url.render_as_string(hide_password=False)


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

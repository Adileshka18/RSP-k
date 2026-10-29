import sys

from backend.core.config import (
    ConfigError,
    get_backend_host,
    get_backend_log_level,
    get_backend_port,
    get_backend_reload,
    get_db_config,
)


def main() -> None:
    # Проверяем конфигурацию до старта сервера, чтобы упасть сразу и с понятным текстом,
    # а не с трассировкой из глубины uvicorn.
    try:
        get_db_config()
    except ConfigError as exc:
        sys.exit(f"Ошибка конфигурации: {exc}")

    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host=get_backend_host(),
        port=get_backend_port(),
        reload=get_backend_reload(),
        log_level=get_backend_log_level(),
    )


if __name__ == "__main__":
    main()

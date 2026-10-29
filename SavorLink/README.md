# SavorLink

SavorLink - это B2B-маркетплейс для поставщиков и покупателей. Проект использует разнесенную структуру:

- `backend/app.py` - точка входа FastAPI
- `backend/core/*` - конфигурация, зависимости и помощники безопасности
- `backend/modules/*` - функциональные API-модули
- `frontend/src/services/*` - общие клиенты сервисов
- `frontend/src/stores/*` - публичный путь импорта стора для Vue-компонентов

## Быстрый старт

Запустить весь стек через Docker:

```bash
docker compose up --build
```

После запуска:

- Фронтенд: http://localhost:5173
- Документация backend: http://localhost:8002/docs
- PostgreSQL: localhost:5440

## Рабочий сценарий

Минимальный ручной сценарий, который сейчас работает через API:

1. Зарегистрироваться или войти как покупатель и поставщик.
2. Создать предприятие для каждого пользователя.
3. Создать категорию и затем товар для поставщика.
4. Добавить товар в корзину покупателя.
5. Создать заказ и очистить корзину.

## Структура API

- `GET /` - стартовый ответ
- `GET /openapi.json` - схема OpenAPI
- `POST /auth/register` и `POST /auth/login`
- `GET /products`, `POST /products`
- `GET /cart/me`, `POST /cart/me/items`, `POST /cart/me/clear`
- `GET /orders/my-as-buyer`, `GET /orders/my-as-supplier`, `POST /orders`
- `GET /enterprises`, `POST /enterprises`

## Структура проекта

```text
backend/
  app.py
  main.py         # необязательная точка входа uvicorn
  core/
  modules/
  database/
frontend/
  src/services/
  src/stores/
  src/data/
```

## Смоук-тесты

В репозитории есть небольшой набор smoke-тестов API, который проверяет:

- `GET /`
- `GET /openapi.json`
- `GET /products/categories`

Запуск:

```bash
pytest backend/tests/test_api_smoke.py
```

## Примечания

- Текущий Docker-стек использует PostgreSQL на порту `5440`.
- Контейнер backend выполняет миграции перед стартом приложения.
- API теперь в основном живет в `backend/modules/*`; старые переходные обвязки удалены из основного пути запуска.

## Admin Account Bootstrap

Use the helper script to create or update an admin user directly in DB:

```bash
python backend/scripts/create_admin.py --email admin@example.com --password "StrongPass123!"
```

What it does:
- creates the user if it does not exist;
- updates password and sets role to `ADMIN` if the user exists;
- increments `token_version` for existing users to invalidate old tokens.

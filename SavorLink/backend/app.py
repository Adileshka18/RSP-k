from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from backend.database.session import engine, is_database_available, wait_for_database
from backend.modules.auth.router import router as auth_router
from backend.modules.cart.router import router as cart_router
from backend.modules.chats.router import router as chats_router
from backend.modules.enterprises.router import router as enterprises_router
from backend.modules.favorites.router import router as favorites_router
from backend.modules.orders.router import router as orders_router
from backend.modules.products.router import router as products_router
from backend.modules.users.router import router as users_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск API SavorLink...")

    try:
        await wait_for_database()
    except Exception as exc:
        logger.exception("Не удалось подключиться к базе данных")
        raise RuntimeError("Не удалось подключиться к базе данных при запуске приложения") from exc

    logger.info("Подключение к базе данных успешно")
    yield

    logger.info("Завершение работы API SavorLink...")
    await engine.dispose()
    logger.info("Соединение с базой данных закрыто")


app = FastAPI(
    title="SavorLink API",
    description="Маркетплейс для связи поставщиков и покупателей (MVP SavorLink)",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Ошибка валидации", "errors": exc.errors()},
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    # Сработало ограничение БД (UNIQUE, CHECK, FOREIGN KEY) — это ошибка данных, а не сервера
    logger.warning("Нарушено ограничение целостности: %s", exc.orig)
    return JSONResponse(
        status_code=409,
        content={"detail": "Операция нарушает ограничения целостности данных"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Непредвиденная ошибка при обработке запроса")
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )


app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(chats_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(enterprises_router)
app.include_router(favorites_router)


@app.get("/")
async def read_root():
    return {"message": "Добро пожаловать в API SavorLink"}


@app.get("/health")
async def health_check():
    database_ok = await is_database_available()
    return JSONResponse(
        status_code=200 if database_ok else 503,
        content={
            "status": "ok" if database_ok else "unavailable",
            "database": "ok" if database_ok else "unavailable",
            "service": "SavorLink API",
            "version": "0.1.0",
            "uptime": int(time.time() - START_TIME),
        },
    )
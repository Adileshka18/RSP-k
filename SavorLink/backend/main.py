import os

from backend.app import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", "8002")),
        reload=os.getenv("BACKEND_RELOAD", "true").lower() == "true",
        log_level=os.getenv("BACKEND_LOG_LEVEL", "info"),
    )

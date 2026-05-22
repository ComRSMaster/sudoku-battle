"""Настройка и запуск HTTP-сервера FastAPI"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api import games, history, leaderboards, users
from backend.database import Base, engine
from core.exceptions import (
    AuthTMAError,
    GameAccessDeniedError,
    GameNotFoundError,
    SudokuError,
    UserNotFoundError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    print("app shutdown")


app = FastAPI(
    title="Sudoku Battle API",
    description="FastAPI backend for Sudoku Battle game sessions",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(AuthTMAError)
async def auth_tma_handler(
    request: Request,
    error: AuthTMAError,
) -> JSONResponse:
    """Преобразовать ошибку авторизации в Telegram Mini Apps в HTTP-ответ"""

    return JSONResponse(status_code=403, content={"detail": str(error)})


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(
    request: Request,
    error: UserNotFoundError,
) -> JSONResponse:
    """Преобразовать ошибку отсутствующего пользователя в HTTP-ответ"""

    return JSONResponse(status_code=404, content={"detail": str(error)})


@app.exception_handler(GameNotFoundError)
async def game_not_found_handler(
    request: Request,
    error: GameNotFoundError,
) -> JSONResponse:
    """Преобразовать ошибку отсутствующей игры в HTTP-ответ"""

    return JSONResponse(status_code=404, content={"detail": str(error)})


@app.exception_handler(GameAccessDeniedError)
async def game_access_denied_handler(
    request: Request,
    error: GameAccessDeniedError,
) -> JSONResponse:
    """Преобразовать ошибку доступа к игре в HTTP-ответ"""

    return JSONResponse(status_code=403, content={"detail": str(error)})


@app.exception_handler(SudokuError)
async def sudoku_error_handler(
    request: Request,
    error: SudokuError,
) -> JSONResponse:
    """Преобразовать все ошибки поля судоку в HTTP-ответ"""

    return JSONResponse(status_code=400, content={"detail": str(error)})


app.include_router(games.router, prefix="/ws")
app.include_router(history.router, prefix="/api")
app.include_router(leaderboards.router, prefix="/api")
app.include_router(users.router, prefix="/api")

BUILD_DIR = os.path.join(os.path.dirname(__file__), "../frontend/build")

if os.path.exists(BUILD_DIR):
    app.mount(
        "/_app", StaticFiles(directory=os.path.join(BUILD_DIR, "_app")), name="assets"
    )

    @app.get("/{catchall:path}")
    async def serve_index(catchall: str):
        if catchall in ["docs", "redoc", "openapi.json"]:
            raise HTTPException(status_code=404)

        return FileResponse(os.path.join(BUILD_DIR, "index.html"))
else:
    raise FileNotFoundError(BUILD_DIR)

async def run_server() -> None:
    """Запустить сервер игры FastAPI"""
    import uvicorn

    config = uvicorn.Config("backend.server:app")
    server = uvicorn.Server(config)
    await server.serve()

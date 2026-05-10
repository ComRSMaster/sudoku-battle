"""Настройка и запуск HTTP-сервера FastAPI"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api import games, leaderboards, users
from backend.database import Base, engine
from core.exceptions import (
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


app.include_router(games.router, prefix="/api")
app.include_router(leaderboards.router, prefix="/api")
app.include_router(users.router, prefix="/api")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


async def run_server() -> None:
    """Запустить сервер игры FastAPI"""
    import uvicorn

    config = uvicorn.Config("backend.server:app")
    server = uvicorn.Server(config)
    await server.serve()

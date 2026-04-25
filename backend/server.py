"""Настройка и запуск HTTP-сервера FastAPI"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api import games

app = FastAPI(
    title="Sudoku Battle API",
    description="FastAPI backend for Sudoku Battle game sessions",
    version="0.1.0",
)

app.include_router(games.router, prefix="/api")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


async def run_server() -> None:
    """Запустить сервер игры FastAPI"""
    import uvicorn

    config = uvicorn.Config("backend.server:app")
    server = uvicorn.Server(config)
    await server.serve()

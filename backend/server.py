import asyncio
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from core.generator import Sudoku

BOARD_SIZE = 3
DEFAULT_HOLES = 45


class MoveRequest(BaseModel):
    user_id: int = Field(ge=0)
    row: int = Field(ge=0, le=BOARD_SIZE * BOARD_SIZE - 1)
    col: int = Field(ge=0, le=BOARD_SIZE * BOARD_SIZE - 1)
    value: int = Field(ge=1, le=BOARD_SIZE * BOARD_SIZE)


# TODO: заменить user_id на аутентификацию через Telegram Mini Apps
# TODO: пользователь может ввести неправильные клетки так, чтобы судоку было невозможно разгадать, надо разрешить пользователю отменять свои ходы


class CreateGameRequest(BaseModel):
    holes_count: int = Field(default=DEFAULT_HOLES, ge=1, le=BOARD_SIZE**4 - 1)
    user_id: int = Field(ge=0)


class SudokuSchema(BaseModel):
    n: int
    holes_count: int
    table: list[list[int]]
    model_config = ConfigDict(from_attributes=True)


class GameStateResponse(BaseModel):
    sudoku: SudokuSchema
    user_ids: list[int]
    model_config = ConfigDict(from_attributes=True)


class CreateGameResponse(GameStateResponse):
    game_id: int


@dataclass
class GameState:
    sudoku: Sudoku
    user_ids: list[int]


app = FastAPI(
    title="Sudoku Battle API",
    description="FastAPI backend for Sudoku Battle game sessions.",
    version="0.1.0",
)

_users: dict[int, list[int]] = {}
_games: dict[int, GameState] = {}
_free_game_id: int = 0
_games_lock = asyncio.Lock()


async def _get_game(game_id: int, user_id: int) -> GameState:
    async with _games_lock:
        game = _games.get(game_id)

    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    if user_id not in game.user_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    return game


@app.post("/games", response_model=CreateGameResponse)
async def create_game(payload: CreateGameRequest) -> CreateGameResponse:
    game = GameState(
        sudoku=Sudoku(holes_count=payload.holes_count),
        user_ids=[payload.user_id],
    )

    async with _games_lock:
        global _free_game_id
        game_id = _free_game_id
        _games[game_id] = game
        _free_game_id += 1

    return CreateGameResponse(
        sudoku=SudokuSchema.model_validate(game.sudoku),
        user_ids=game.user_ids,
        game_id=game_id,
    )


@app.get("/games/{game_id}", response_model=GameStateResponse)
async def get_game(game_id: int, user_id: int) -> GameStateResponse:
    game = await _get_game(game_id, user_id)
    return GameStateResponse(
        sudoku=SudokuSchema.model_validate(game.sudoku), user_ids=game.user_ids
    )


@app.post("/games/{game_id}/move", response_model=GameStateResponse)
async def apply_move(game_id: int, move: MoveRequest) -> GameStateResponse:
    game = await _get_game(game_id, move.user_id)

    if not game.sudoku.solve_hole(move.row, move.col, move.value):
        raise HTTPException(status_code=400, detail="Invalid move")

    return GameStateResponse(
        sudoku=SudokuSchema.model_validate(game.sudoku), user_ids=game.user_ids
    )


@app.delete("/games/{game_id}", status_code=204)
async def delete_game(game_id: int, user_id: int) -> None:
    await _get_game(game_id, user_id)
    _games.pop(game_id)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "name": "Sudoku Battle API",
        "docs": "/docs",
    }

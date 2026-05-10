from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import games as crud_games
from backend.crud import users as crud_users
from backend.database import AsyncSessionLocal, get_db
from backend.schemas.games import (
    CreateGameRequest,
    GameStateResponse,
    SudokuSchema,
)
from backend.sockets.manager import manager
from core.generator import Sudoku

router = APIRouter(prefix="/games", tags=["Games"])


async def _get_game_state(game_id: int, db: AsyncSession) -> GameStateResponse:
    """Вспомогательная функция для формирования состояния игры"""
    game = await crud_games.get_game(db, game_id)
    if not game:
        raise ValueError(f"Game {game_id} not found")

    return GameStateResponse(
        game_id=game.id,
        sudoku=SudokuSchema(n=game.n, holes_count=game.holes_count, table=game.table),
        user_ids=[u.user_id for u in game.users],
    )


@router.post("/", response_model=GameStateResponse)
async def create_game(
    payload: CreateGameRequest, db: AsyncSession = Depends(get_db)
) -> GameStateResponse:
    """Создать новую игру"""
    await crud_users.get_user_or_create(db, payload.user_id)
    game = await crud_games.create_game(db, payload.user_id, payload.holes_count)
    return await _get_game_state(game.id, db)


@router.websocket("/{game_id}/ws/{user_id}")
async def game_websocket(game_id: int, user_id: int, websocket: WebSocket):
    """WebSocket для real-time взаимодействия"""
    await manager.connect(game_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Expecting {"row": int, "col": int, "value": int}

            async with AsyncSessionLocal() as db:
                game = await crud_games.get_game(db, game_id)
                if not game or user_id not in [u.user_id for u in game.users]:
                    await websocket.send_json(
                        {"error": "Unauthorized or game not found"}
                    )
                    continue

                sudoku = Sudoku(n=game.n, holes_count=game.holes_count)
                sudoku.table = game.table

                try:
                    sudoku.solve_hole(data["row"], data["col"], data["value"])
                    await crud_games.update_game_table(
                        db, game_id, sudoku.table, sudoku.holes_count
                    )

                    if sudoku.holes_count == 0:
                        await crud_users.increment_user_solved_count(db, user_id)

                    state = await _get_game_state(game_id, db)
                    await manager.broadcast(game_id, state.model_dump())

                except Exception as e:
                    await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        manager.disconnect(game_id, websocket)

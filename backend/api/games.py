from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import get_user_data_from_tma
from backend.crud import games as crud_games
from backend.crud import users as crud_users
from backend.database import AsyncSessionLocal
from backend.schemas.games import (
    GameStateResponse,
    SudokuSchema,
)
from backend.sockets.manager import manager
from core.exceptions import SudokuRulesViolationError, UserNotFoundError
from core.generator import Sudoku

from datetime import datetime, timezone

router = APIRouter(prefix="/games", tags=["Websocket games"])

start_date = datetime.fromtimestamp(0, tz=timezone.utc).date()


async def _get_game_state(game_id: int, db: AsyncSession) -> GameStateResponse:
    """Вспомогательная функция для формирования состояния игры"""
    game = await crud_games.get_game(db, game_id)
    if not game:
        raise ValueError(f"Game {game_id} not found")

    return GameStateResponse(
        game_id=game.id,
        sudoku=SudokuSchema(
            n=game.n,
            holes_count=game.holes_count,
            table=game.table,
            holes_mask=game.holes_mask,
        ),
        user_ids=[u.user_id for u in game.users],
    )


@router.websocket("/play")
async def game_websocket(
    websocket: WebSocket,
    game_id: int | None = Query(None),
    from_game_id: int | None = Query(None),
    is_daily: bool | None = Query(None),
    tma: str | None = Query(None),
) -> None:
    """WebSocket для real-time взаимодействия"""

    user_data = get_user_data_from_tma(tma)
    user_id = user_data.id

    async with AsyncSessionLocal() as db:
        user = await crud_users.get_user_or_create(db, user_data)

        if game_id:
            game = await crud_games.get_game(db, game_id)
        else:
            random_seed = None
            if is_daily:
                today_utc = datetime.now(timezone.utc).date()
                random_seed = (today_utc - start_date).days

            game = None
            if from_game_id:
                from_game = await crud_games.get_game(db, from_game_id)
                if from_game:
                    for i in range(from_game.n * from_game.n):
                        for j in range(from_game.n * from_game.n):
                            if from_game.holes_mask[i][j]:
                                from_game.table[i][j] = 0
                    game = await crud_games.create_game_from(
                        db, user_id, from_game.table, from_game.holes_mask
                    )
            if game is None:
                game = await crud_games.create_game(db, user_id, 5, random_seed)
            game_id = game.id

        await manager.connect(game_id, websocket)

        state = await _get_game_state(game_id, db)
        await websocket.send_json(state.model_dump())

    try:
        while True:
            data = await websocket.receive_json()

            async with AsyncSessionLocal() as db:
                game = await crud_games.get_game(db, game_id)
                if not game:
                    continue

                sudoku = Sudoku(
                    n=game.n,
                    holes_count=game.holes_count,
                    table=game.table,
                    holes_mask=game.holes_mask,
                )

                try:
                    sudoku.solve_hole(data["row"], data["col"], data["value"])
                    await crud_games.update_game_table(
                        db, game_id, sudoku.table, sudoku.holes_count, sudoku.holes_mask
                    )

                    if sudoku.holes_count == 0:
                        solved_time = data.get("time", 0)
                        user = await crud_users.get_user_or_create(db, user_data)
                        if user is None:
                            raise UserNotFoundError(user_id)

                        battle_won = False
                        if solved_time > 0:
                            if game.fastest_solve != -1 and game.fastest_solve > solved_time:
                                battle_won = True
                            await crud_games.update_game_solved_time(
                                db,
                                game_id,
                                solved_time,
                            )

                            if user.fastest_solve_time is None or solved_time < user.fastest_solve_time:
                                user.fastest_solve_time = solved_time
                                await db.commit()

                        await crud_users.increment_user_solved_count(db, user_id)
                        await crud_users.increment_user_battles_won(db, user_id)
                        await crud_users.update_user_achievements(
                            db, user_id, solved_time
                        )

                    state = await _get_game_state(game_id, db)
                    await manager.broadcast(game_id, state.model_dump())

                except SudokuRulesViolationError:
                    await websocket.send_json({"error": "Invalid move", "penalty": 10})
                except Exception as e:
                    await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        manager.disconnect(game_id, websocket)

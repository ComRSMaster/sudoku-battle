from pydantic import BaseModel, ConfigDict, Field

from core.constants import DEFAULT_HOLES_COUNT, DEFAULT_REG_SIZE


class SudokuSchema(BaseModel):
    """Схема судоку, отдаваемая через API"""

    n: int
    holes_count: int
    table: list[list[int]]
    holes_mask: list[list[bool]]
    model_config = ConfigDict(from_attributes=True)


class GameStateResponse(BaseModel):
    """Схема ответа с состоянием игры"""

    game_id: int
    sudoku: SudokuSchema
    user_ids: list[int]
    model_config = ConfigDict(from_attributes=True)


class CreateGameRequest(BaseModel):
    """Тело запроса для создания новой игры"""

    holes_count: int = Field(
        default=DEFAULT_HOLES_COUNT,
        ge=1,
        le=DEFAULT_REG_SIZE**4 - 1,
    )
    user_id: int = Field(ge=0)


class MoveRequest(BaseModel):
    """Тело запроса для хода в судоку"""

    user_id: int = Field(ge=0)
    row: int = Field(ge=0, le=DEFAULT_REG_SIZE * DEFAULT_REG_SIZE - 1)
    col: int = Field(ge=0, le=DEFAULT_REG_SIZE * DEFAULT_REG_SIZE - 1)
    value: int = Field(ge=1, le=DEFAULT_REG_SIZE * DEFAULT_REG_SIZE)

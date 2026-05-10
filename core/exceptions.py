"""Пользовательские исключения для логики игры"""


class SudokuBattleError(Exception):
    """Базовое исключение приложения игры"""


class UserNotFoundError(SudokuBattleError):
    """Пользователь не найден"""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")


class SudokuError(SudokuBattleError):
    """Базовое исключение для операций с игровым полем судоку"""


class InvalidHolesCountError(SudokuError):
    """Ошибка некорректного количества пустых клеток"""

    def __init__(self, count: int, max_count: int) -> None:
        self.count = count
        self.max_count = max_count
        super().__init__(f"Invalid holes count: expected 1..{max_count}, got {count}")


class InvalidMoveError(SudokuError):
    """Ошибка хода, нарушающего правила судоку"""


class CellOutOfBoundsError(InvalidMoveError):
    """Ошибка обращения к ячейке за пределами поля"""

    def __init__(self, row: int, col: int, board_size: int) -> None:
        self.row = row
        self.col = col
        self.board_size = board_size
        super().__init__(
            f"Cell ({row}, {col}) is out of bounds for board size {board_size}x{board_size}"
        )


class InvalidCellValueError(InvalidMoveError):
    """Ошибка недопустимого значения в ячейке"""

    def __init__(self, value: int, max_value: int) -> None:
        self.value = value
        self.max_value = max_value
        super().__init__(f"Invalid cell value: expected 1..{max_value}, got {value}")


class CellAlreadyFilledError(InvalidMoveError):
    """Ошибка попытки изменить уже заполненную ячейку"""

    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        super().__init__(f"Cell ({row}, {col}) is already filled")


class SudokuRulesViolationError(InvalidMoveError):
    """Ошибка хода, который нарушает правила судоку
    (появляются одинаковые значения на одной строке, одном столбце или одном регионе)"""

    def __init__(self, row: int, col: int, value: int) -> None:
        self.row = row
        self.col = col
        self.value = value
        super().__init__(f"Move ({row}, {col}) -> {value} violates sudoku rules")


class GameError(SudokuBattleError):
    """Базовое исключение для игровых сессий"""


class GameNotFoundError(GameError):
    """Ошибка запроса к несуществующей игре"""

    def __init__(self, game_id: int) -> None:
        self.game_id = game_id
        super().__init__(f"Game {game_id} not found")


class GameAccessDeniedError(GameError):
    """Ошибка доступа пользователя к чужой приватной игре"""

    def __init__(self, game_id: int, user_id: int) -> None:
        self.game_id = game_id
        self.user_id = user_id
        super().__init__(f"User {user_id} has no access to game {game_id}")

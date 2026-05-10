"""Генерация и проверка таблиц судоку"""

import random
from typing import Generator

from core.constants import (
    DEFAULT_HOLES_COUNT,
    DEFAULT_REG_SIZE,
    DEFAULT_SHUFFLE_COUNT,
)
from core.exceptions import (
    CellAlreadyFilledError,
    CellOutOfBoundsError,
    InvalidCellValueError,
    InvalidHolesCountError,
    SudokuRulesViolationError,
)


class Sudoku:
    """Класс таблицы судоку.
    `self.n` - размер района (по умолчанию 3)
    0 - пустая клетка (hole).
    Клетки с 1 до `self.n * self.n` - заполненные"""

    def __init__(
        self,
        n: int = DEFAULT_REG_SIZE,
        table: list[list[int]] | None = None,
        holes_mask: list[list[bool]] | None = None,
        holes_count: int = DEFAULT_HOLES_COUNT,
        shuffle_count: int = DEFAULT_SHUFFLE_COUNT,
    ) -> None:
        """Создание таблицы судоку"""

        self.n: int = n
        self.holes_count: int = holes_count

        if table is None or holes_mask is None:
            self.table: list[list[int]] = [
                [((i * n + i // n + j) % (n * n) + 1) for j in range(n * n)]
                for i in range(n * n)
            ]
            self.holes_mask: list[list[bool]] = [
                [False] * (n * n) for _ in range(n * n)
            ]
            self.shuffle(shuffle_count)
            self.create_holes(holes_count)
        else:
            self.table = table
            self.holes_mask = holes_mask

    def __str__(self) -> str:
        """Вывод таблицы в виде строки"""

        width = len(str(self.n * self.n))

        lines = []
        for i, row in enumerate(self.table):
            if i > 0 and i % self.n == 0:
                divider = "".join("+" if c == "|" else "-" for c in lines[0])
                lines.append(divider)

            blocks = [
                " ".join(f"{cell:{width}}" for cell in row[i : i + self.n])
                for i in range(0, self.n * self.n, self.n)
            ]
            lines.append(" | ".join(blocks))

        return "\n".join(lines)

    def transpose(self) -> None:
        """Транспонирование всей таблицы"""

        self.table = [list(row) for row in zip(*self.table)]

    def swap_rows_single(self) -> None:
        """Обмен двух строк"""

        row = random.randint(0, self.n - 1)
        l1 = random.randint(0, self.n - 1)
        while True:
            l2 = random.randint(0, self.n - 1)
            if l1 != l2:
                break

        self.table[row * self.n + l1], self.table[row * self.n + l2] = (
            self.table[row * self.n + l2],
            self.table[row * self.n + l1],
        )

    def swap_columns_single(self) -> None:
        """Обмен двух столбцов"""

        self.transpose()
        self.swap_rows_single()
        self.transpose()

    def swap_rows_area(self) -> None:
        """Обмен двух районов по горизонтали"""

        area1 = random.randint(0, self.n - 1)
        while True:
            area2 = random.randint(0, self.n - 1)
            if area1 != area2:
                break

        for i in range(0, self.n):
            l1 = area1 * self.n + i
            l2 = area2 * self.n + i
            self.table[l1], self.table[l2] = self.table[l2], self.table[l1]

    def swap_columns_area(self) -> None:
        """Обмен двух районов по вертикали"""

        self.transpose()
        self.swap_rows_area()
        self.transpose()

    def shuffle(self, count: int = DEFAULT_SHUFFLE_COUNT) -> None:
        """Перемешивание таблицы `count` раз"""

        shuffle_func = [
            self.transpose,
            self.swap_rows_single,
            self.swap_columns_single,
            self.swap_rows_area,
            self.swap_columns_area,
        ]
        for _ in range(0, count):
            random.choice(shuffle_func)()

    def create_holes(self, count: int = DEFAULT_HOLES_COUNT) -> None:
        """Вычеркивание `count` случайных ячеек"""

        max_holes_count = self.n**4 - 1
        if not 1 <= count <= max_holes_count:
            raise InvalidHolesCountError(count=count, max_count=max_holes_count)

        cells = random.sample(range(self.n**4), count)
        for cell in cells:
            i = cell // (self.n * self.n)
            j = cell % (self.n * self.n)
            self.table[i][j] = 0
            self.holes_mask[i][j] = True

    def _validate_coordinates(self, row: int, col: int) -> None:
        """Проверить, что координаты ячейки находятся в пределах поля"""

        board_size = self.n * self.n
        if not (0 <= row < board_size and 0 <= col < board_size):
            raise CellOutOfBoundsError(row=row, col=col, board_size=board_size)

    def available_values(self, row: int, col: int) -> Generator[int, None, None]:
        """Возвращает список доступных значений для ячейки (`row`, `col`)"""

        self._validate_coordinates(row, col)
        unused = [True] * (self.n * self.n + 1)

        for i in range(0, self.n * self.n):
            unused[self.table[row][i]] = False
            unused[self.table[i][col]] = False

        arow = row // self.n * self.n
        acol = col // self.n * self.n
        for i in range(0, self.n):
            for j in range(0, self.n):
                unused[self.table[arow + i][acol + j]] = False

        return (i for i in range(1, self.n * self.n + 1) if unused[i])

    def solve_hole(self, row: int, col: int, value: int) -> None:
        """Ход пользователя в ячейке (`row`, `col`)"""

        self._validate_coordinates(row, col)

        if not (1 <= value <= self.n * self.n):
            raise InvalidCellValueError(value=value, max_value=self.n * self.n)

        if not self.holes_mask[row][col]:
            raise CellAlreadyFilledError(row=row, col=col)

        if value not in self.available_values(row, col):
            raise SudokuRulesViolationError(row=row, col=col, value=value)

        self.table[row][col] = value
        self.holes_count -= 1

    def _validate_rows(self) -> bool:
        """Проверить, что каждая строка содержит все значения без пропусков"""

        for row in range(0, self.n * self.n):
            unused = [True] * (self.n * self.n)
            for col in range(0, self.n * self.n):
                if self.table[row][col] == 0:
                    continue
                unused[self.table[row][col] - 1] = False
            if any(unused):
                return False
        return True

    def _validate_columns(self) -> bool:
        """Проверить, что каждый столбец содержит все значения без пропусков"""

        for col in range(0, self.n * self.n):
            unused = [True] * (self.n * self.n)
            for row in range(0, self.n * self.n):
                if self.table[row][col] == 0:
                    continue
                unused[self.table[row][col] - 1] = False
            if any(unused):
                return False
        return True

    def _validate_areas(self) -> bool:
        """Проверить, что каждый район содержит все значения без пропусков"""

        for arow in range(0, self.n):
            for acol in range(0, self.n):
                unused = [True] * (self.n * self.n)
                for row in range(0, self.n):
                    for col in range(0, self.n):
                        value = self.table[arow * self.n + row][acol * self.n + col]
                        if value == 0:
                            continue
                        unused[value - 1] = False
                if any(unused):
                    return False
        return True

    def validate(self) -> bool:
        """Проверка таблицы с судоку на валидность"""

        return (
            self._validate_rows()
            and self._validate_columns()
            and self._validate_areas()
        )

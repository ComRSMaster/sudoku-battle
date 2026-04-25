import random
from typing import Generator


class Sudoku:
    """Класс таблицы судоку.
    `self.n` - размер района (по умолчанию 3)
    0 - пустая клетка (hole).
    Клетки с 1 до `self.n * self.n` - заполненные."""

    def __init__(
        self,
        n: int = 3,
        shuffle_count: int = 15,
        holes_count: int = 20,
    ) -> None:
        """Создание таблицы судоку"""
        self.n: int = n
        self.holes_count: int = holes_count
        self.table: list[list[int]] = [
            [((i * n + i // n + j) % (n * n) + 1) for j in range(n * n)]
            for i in range(n * n)
        ]
        self.shuffle(shuffle_count)
        self.create_holes(holes_count)

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
        l1 = random.randint(0, self.n * self.n - 1)
        while True:
            l2 = random.randint(0, self.n * self.n - 1)
            if l1 != l2:
                break

        self.table[l1], self.table[l2] = self.table[l2], self.table[l1]

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

    def shuffle(self, count: int = 15) -> None:
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

    def create_holes(self, count: int = 20) -> None:
        """Вычеркивание `count` случайных ячеек"""
        cells = random.sample(range(self.n**4), count)
        for cell in cells:
            self.table[cell // (self.n * self.n)][cell % (self.n * self.n)] = 0

    def available_values(self, row: int, col: int) -> Generator[int, None, None]:
        """Возвращает список доступных значений для ячейки (`row`, `col`)"""
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

    def solve_hole(self, row: int, col: int, value: int) -> bool:
        """Ход пользователя и его проверка в ячейке (`row`, `col`)"""
        if not (1 <= value <= self.n * self.n) or self.table[row][col] != 0:
            return False

        if value not in self.available_values(row, col):
            return False

        self.table[row][col] = value
        self.holes_count -= 1
        return True

    def validate(self) -> bool:
        """Проверка таблицы с судоку на валидность"""

        # Проверка строк
        for i in range(0, self.n * self.n):
            unused = [True] * (self.n * self.n)
            for j in range(0, self.n * self.n):
                if self.table[i][j] == 0:
                    continue
                unused[self.table[i][j] - 1] = False
            if any(unused):
                return False

        # Проверка столбцов
        for j in range(0, self.n * self.n):
            unused = [True] * (self.n * self.n)
            for i in range(0, self.n * self.n):
                if self.table[i][j] == 0:
                    continue
                unused[self.table[i][j] - 1] = False
            if any(unused):
                return False

        # Проверка районов
        for ai in range(0, self.n):
            for aj in range(0, self.n):
                unused = [True] * (self.n * self.n)
                for i in range(0, self.n):
                    for j in range(0, self.n):
                        if self.table[ai * self.n + i][aj * self.n + j] == 0:
                            continue
                        unused[self.table[ai * self.n + i][aj * self.n + j] - 1] = False
                if any(unused):
                    return False
        return True

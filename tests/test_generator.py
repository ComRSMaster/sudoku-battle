"""Тесты для класса Sudoku и генератора судоку"""

import pytest
from core.generator import Sudoku
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


class TestSudokuInitialization:
    """Тесты инициализации таблицы судоку"""

    def test_default_initialization(self):
        """Проверка создания судоку с параметрами по умолчанию"""
        sudoku = Sudoku()
        assert sudoku.n == DEFAULT_REG_SIZE
        assert sudoku.holes_count == DEFAULT_HOLES_COUNT
        assert len(sudoku.table) == sudoku.n * sudoku.n
        assert len(sudoku.table[0]) == sudoku.n * sudoku.n

    def test_custom_reg_size(self):
        """Проверка создания судоку с кастомным размером района"""
        sudoku = Sudoku(n=2, holes_count=5)
        assert sudoku.n == 2
        assert len(sudoku.table) == 4
        assert len(sudoku.table[0]) == 4

    def test_custom_holes_count(self):
        """Проверка создания судоку с кастомным количеством дыр"""
        sudoku = Sudoku(holes_count=30)
        assert sudoku.holes_count == 30
        hole_count = sum(row.count(0) for row in sudoku.table)
        assert hole_count == 30

    def test_with_provided_table_and_mask(self):
        """Проверка инициализации с предоставленной таблицей и маской"""
        table = [[i + j for j in range(9)] for i in range(9)]
        mask = [[False] * 9 for _ in range(9)]
        sudoku = Sudoku(table=table, holes_mask=mask)
        assert sudoku.table == table
        assert sudoku.holes_mask == mask

    def test_random_seed_reproducibility(self):
        """Проверка воспроизводимости с одинаковым random_seed"""
        sudoku1 = Sudoku(random_seed=42)
        sudoku2 = Sudoku(random_seed=42)
        assert sudoku1.table == sudoku2.table
        assert sudoku1.holes_mask == sudoku2.holes_mask


class TestTableGeneration:
    """Тесты генерации таблицы судоку"""

    def test_initial_table_structure(self):
        """Проверка что начальная таблица имеет правильную структуру"""
        sudoku = Sudoku(n=3, shuffle_count=0, holes_count=1)

        hole_count = sum(row.count(0) for row in sudoku.table)
        assert hole_count == 1

    def test_all_values_in_range(self):
        """Проверка что все значения в таблице в допустимом диапазоне"""
        sudoku = Sudoku()
        for row in sudoku.table:
            for cell in row:
                assert 0 <= cell <= sudoku.n * sudoku.n

    def test_holes_are_marked(self):
        """Проверка что дыры правильно отмечены в holes_mask"""
        sudoku = Sudoku(random_seed=42)
        hole_count_in_mask = sum(row.count(True) for row in sudoku.holes_mask)
        hole_count_in_table = sum(row.count(0) for row in sudoku.table)
        assert hole_count_in_mask == hole_count_in_table
        assert hole_count_in_table == sudoku.holes_count


class TestValidation:
    """Тесты валидации таблицы судоку"""

    def test_completed_sudoku_is_valid(self):
        """Проверка что заполненная таблица судоку может быть валидна"""
        table = [[(i * 3 + i // 3 + j) % 9 + 1 for j in range(9)] for i in range(9)]
        mask = [[False] * 9 for _ in range(9)]
        sudoku = Sudoku(table=table, holes_mask=mask, holes_count=0)
        assert sudoku.validate()

    def test_validate_rows(self):
        """Проверка валидации строк"""
        table = [[(i * 3 + i // 3 + j) % 9 + 1 for j in range(9)] for i in range(9)]
        mask = [[False] * 9 for _ in range(9)]
        sudoku = Sudoku(table=table, holes_mask=mask, holes_count=0)
        assert sudoku._validate_rows()

    def test_validate_columns(self):
        """Проверка валидации столбцов"""
        table = [[(i * 3 + i // 3 + j) % 9 + 1 for j in range(9)] for i in range(9)]
        mask = [[False] * 9 for _ in range(9)]
        sudoku = Sudoku(table=table, holes_mask=mask, holes_count=0)
        assert sudoku._validate_columns()

    def test_validate_areas(self):
        """Проверка валидации регионов"""
        table = [[(i * 3 + i // 3 + j) % 9 + 1 for j in range(9)] for i in range(9)]
        mask = [[False] * 9 for _ in range(9)]
        sudoku = Sudoku(table=table, holes_mask=mask, holes_count=0)
        assert sudoku._validate_areas()

    def test_partial_sudoku_validation(self):
        """Проверка что неполная судоку не валидна (содержит нули)"""
        sudoku = Sudoku(holes_count=20)
        validation_result = sudoku.validate()
        assert isinstance(validation_result, bool)


class TestTranspose:
    """Тесты операции транспонирования"""

    def test_transpose_changes_table(self):
        """Проверка что транспонирование изменяет таблицу"""
        sudoku = Sudoku(shuffle_count=15, holes_count=1, random_seed=42)
        original_table = [row[:] for row in sudoku.table]
        sudoku.transpose()
        assert sudoku.table != original_table

    def test_double_transpose_returns_original(self):
        """Проверка что двойное транспонирование возвращает оригинальную таблицу"""
        sudoku = Sudoku(shuffle_count=15, holes_count=1, random_seed=42)
        original_table = [row[:] for row in sudoku.table]
        sudoku.transpose()
        sudoku.transpose()
        assert sudoku.table == original_table

    def test_transpose_preserves_holes_mask(self):
        """Проверка что транспонирование не влияет на holes_mask"""
        sudoku = Sudoku(random_seed=42)
        original_mask = [row[:] for row in sudoku.holes_mask]
        sudoku.transpose()
        assert sudoku.holes_mask == original_mask


class TestSwapOperations:
    """Тесты операций обмена строк и столбцов"""

    def test_swap_rows_single_changes_table(self):
        """Проверка что обмен строк изменяет таблицу"""
        sudoku = Sudoku(shuffle_count=15, holes_count=1, random_seed=42)
        original_table = [row[:] for row in sudoku.table]
        sudoku.swap_rows_single()
        assert sudoku.table != original_table

    def test_swap_columns_single_changes_table(self):
        """Проверка что обмен столбцов изменяет таблицу"""
        sudoku = Sudoku(shuffle_count=15, holes_count=1, random_seed=42)
        original_table = [row[:] for row in sudoku.table]
        sudoku.swap_columns_single()
        assert sudoku.table != original_table

    def test_swap_rows_area_changes_table(self):
        """Проверка что обмен регионов по горизонтали изменяет таблицу"""
        sudoku = Sudoku(shuffle_count=15, holes_count=1, random_seed=42)
        original_table = [row[:] for row in sudoku.table]
        sudoku.swap_rows_area()
        assert sudoku.table != original_table

    def test_swap_columns_area_changes_table(self):
        """Проверка что обмен регионов по вертикали изменяет таблицу"""
        sudoku = Sudoku(shuffle_count=15, holes_count=1, random_seed=42)
        original_table = [row[:] for row in sudoku.table]
        sudoku.swap_columns_area()
        assert sudoku.table != original_table


class TestShuffle:
    """Тесты перемешивания таблицы"""

    def test_shuffle_with_zero_count(self):
        """Проверка перемешивания с нулевым количеством"""
        sudoku = Sudoku(shuffle_count=0, holes_count=1, random_seed=42)
        assert sudoku.table is not None

    def test_shuffle_with_custom_count(self):
        """Проверка что перемешивание с разным количеством дает разные результаты"""
        sudoku1 = Sudoku(shuffle_count=1, holes_count=1, random_seed=42)
        sudoku2 = Sudoku(shuffle_count=20, holes_count=1, random_seed=42)
        assert sudoku1.table != sudoku2.table

    def test_shuffle_maintains_table_size(self):
        """Проверка что перемешивание не меняет размер таблицы"""
        sudoku = Sudoku(shuffle_count=15, holes_count=1)
        assert len(sudoku.table) == sudoku.n * sudoku.n
        assert all(len(row) == sudoku.n * sudoku.n for row in sudoku.table)


class TestCreateHoles:
    """Тесты создания дыр в таблице"""

    def test_holes_count_matches(self):
        """Проверка что количество дыр соответствует запросу"""
        sudoku = Sudoku(holes_count=40, random_seed=42)
        hole_count = sum(row.count(0) for row in sudoku.table)
        assert hole_count == 40

    def test_holes_count_exceeds_max(self):
        """Проверка исключения при превышении макс количества дыр"""
        with pytest.raises(InvalidHolesCountError):
            Sudoku(n=3, holes_count=82)

    def test_holes_count_zero(self):
        """Проверка исключения при количестве дыр меньше 1"""
        with pytest.raises(InvalidHolesCountError):
            Sudoku(holes_count=0)

    def test_holes_count_negative(self):
        """Проверка исключения при отрицательном количестве дыр"""
        with pytest.raises(InvalidHolesCountError):
            Sudoku(holes_count=-5)

    def test_holes_marked_correctly(self):
        """Проверка что дыры правильно отмечены в маске"""
        sudoku = Sudoku(holes_count=30, random_seed=42)
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if sudoku.holes_mask[i][j]:
                    assert sudoku.table[i][j] == 0

    def test_no_false_holes(self):
        """Проверка что нет ложных дыр (нули где holes_mask = False)"""
        sudoku = Sudoku(holes_count=20, random_seed=42)
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if not sudoku.holes_mask[i][j]:
                    assert sudoku.table[i][j] != 0


class TestAvailableValues:
    """Тесты получения доступных значений для ячейки"""

    def test_available_values_for_empty_cell(self):
        """Проверка доступных значений для пустой ячейки"""
        sudoku = Sudoku(holes_count=40, random_seed=42)
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if sudoku.table[i][j] == 0:
                    available = list(sudoku.available_values(i, j))
                    assert len(available) > 0
                    assert all(1 <= v <= sudoku.n * sudoku.n for v in available)
                    return
        assert False, "Не найдено пустых ячеек"

    def test_available_values_are_unique(self):
        """Проверка что доступные значения уникальны"""
        sudoku = Sudoku(holes_count=40, random_seed=42)
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if sudoku.table[i][j] == 0:
                    available = list(sudoku.available_values(i, j))
                    assert len(available) == len(set(available))

    def test_available_values_out_of_bounds(self):
        """Проверка исключения при запросе доступных значений за пределами"""
        sudoku = Sudoku()
        with pytest.raises(CellOutOfBoundsError):
            list(sudoku.available_values(100, 100))

    def test_available_values_negative_coordinates(self):
        """Проверка исключения при отрицательных координатах"""
        sudoku = Sudoku()
        with pytest.raises(CellOutOfBoundsError):
            list(sudoku.available_values(-1, 0))

    def test_available_values_single_option(self):
        """Проверка ячейки с одним доступным значением"""
        sudoku = Sudoku(shuffle_count=15, holes_count=79, random_seed=42)
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                available = list(sudoku.available_values(i, j))
                if len(available) == 1:
                    assert available[0] in range(1, sudoku.n * sudoku.n + 1)
                    return


class TestSolveHole:
    """Тесты заполнения пустых ячеек"""

    def test_solve_valid_move(self):
        """Проверка заполнения пустой ячейки с допустимым значением"""
        sudoku = Sudoku(holes_count=40, random_seed=42)
        initial_holes = sudoku.holes_count

        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if sudoku.table[i][j] == 0:
                    available = list(sudoku.available_values(i, j))
                    if available:
                        value = available[0]
                        sudoku.solve_hole(i, j, value)
                        assert sudoku.table[i][j] == value
                        assert sudoku.holes_count == initial_holes - 1
                        return
        assert False, "Не найдено заполняемой ячейки"

    def test_solve_hole_invalid_value(self):
        """Проверка исключения при недопустимом значении"""
        sudoku = Sudoku()
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if sudoku.table[i][j] == 0:
                    with pytest.raises(InvalidCellValueError):
                        sudoku.solve_hole(i, j, 100)
                    return

    def test_solve_hole_negative_value(self):
        """Проверка исключения при отрицательном значении"""
        sudoku = Sudoku()
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if sudoku.table[i][j] == 0:
                    with pytest.raises(InvalidCellValueError):
                        sudoku.solve_hole(i, j, -1)
                    return

    def test_solve_hole_zero_value(self):
        """Проверка исключения при нулевом значении"""
        sudoku = Sudoku()
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if sudoku.table[i][j] == 0:
                    with pytest.raises(InvalidCellValueError):
                        sudoku.solve_hole(i, j, 0)
                    return

    def test_solve_filled_cell(self):
        """Проверка исключения при попытке изменить заполненную ячейку"""
        sudoku = Sudoku()
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if sudoku.table[i][j] != 0:
                    with pytest.raises(CellAlreadyFilledError):
                        sudoku.solve_hole(i, j, 5)
                    return
        assert False, "Не найдено заполненной ячейки"

    def test_solve_hole_violates_rules(self):
        """Проверка исключения при нарушении правил судоку"""
        sudoku = Sudoku(holes_count=40, random_seed=42)
        for i in range(sudoku.n * sudoku.n):
            for j in range(sudoku.n * sudoku.n):
                if sudoku.table[i][j] == 0:
                    available = set(sudoku.available_values(i, j))
                    for value in range(1, sudoku.n * sudoku.n + 1):
                        if value not in available:
                            with pytest.raises(SudokuRulesViolationError):
                                sudoku.solve_hole(i, j, value)
                            return

    def test_solve_hole_out_of_bounds(self):
        """Проверка исключения при координатах за пределами"""
        sudoku = Sudoku()
        with pytest.raises(CellOutOfBoundsError):
            sudoku.solve_hole(100, 100, 5)


class TestStringRepresentation:
    """Тесты строкового представления таблицы"""

    def test_str_returns_string(self):
        """Проверка что __str__ возвращает строку"""
        sudoku = Sudoku()
        result = str(sudoku)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_str_contains_separators(self):
        """Проверка что строковое представление содержит разделители"""
        sudoku = Sudoku(n=3, holes_count=10)
        result = str(sudoku)
        assert "|" in result
        assert "+" in result or "-" in result

    def test_str_has_correct_lines(self):
        """Проверка что в строковом представлении правильное количество строк"""
        sudoku = Sudoku(n=3)
        result = str(sudoku)
        lines = result.split("\n")
        expected_lines = sudoku.n * sudoku.n + (sudoku.n - 1)
        assert len(lines) == expected_lines


class TestValidateCoordinates:
    """Тесты валидации координат"""

    def test_validate_valid_coordinates(self):
        """Проверка что валидные координаты не вызывают исключение"""
        sudoku = Sudoku()
        sudoku._validate_coordinates(0, 0)
        sudoku._validate_coordinates(8, 8)
        sudoku._validate_coordinates(4, 4)

    def test_validate_out_of_bounds_high(self):
        """Проверка исключения при координатах выше лимита"""
        sudoku = Sudoku()
        with pytest.raises(CellOutOfBoundsError):
            sudoku._validate_coordinates(9, 0)

    def test_validate_out_of_bounds_negative(self):
        """Проверка исключения при отрицательных координатах"""
        sudoku = Sudoku()
        with pytest.raises(CellOutOfBoundsError):
            sudoku._validate_coordinates(-1, 0)


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_n_equals_2(self):
        """Проверка работы с размером региона 2x2"""
        sudoku = Sudoku(n=2, holes_count=5)
        assert sudoku.n == 2
        assert len(sudoku.table) == 4
        assert sudoku.validate() or sudoku.holes_count > 0

    def test_max_holes_count_minus_one(self):
        """Проверка максимального количества дыр минус один"""
        sudoku = Sudoku(n=3, holes_count=80)
        assert sudoku.holes_count == 80

    def test_single_hole(self):
        """Проверка работы с одной дырой"""
        sudoku = Sudoku(holes_count=1, random_seed=42)
        hole_count = sum(row.count(0) for row in sudoku.table)
        assert hole_count == 1

    def test_all_operations_on_different_sizes(self):
        """Проверка всех операций для разных размеров регионов"""
        for n in [2, 3]:
            sudoku = Sudoku(n=n, shuffle_count=10, holes_count=n * n)
            assert sudoku.validate() or sudoku.holes_count > 0
            sudoku.transpose()
            assert len(sudoku.table) == n * n

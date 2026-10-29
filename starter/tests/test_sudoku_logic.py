import pytest

import sudoku_logic


def _assert_valid_solution(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(set(row) == expected for row in board)
    assert all(
        {board[row][column] for row in range(sudoku_logic.SIZE)} == expected
        for column in range(sudoku_logic.SIZE)
    )
    for box_row in range(0, sudoku_logic.SIZE, 3):
        for box_column in range(0, sudoku_logic.SIZE, 3):
            box = {
                board[row][column]
                for row in range(box_row, box_row + 3)
                for column in range(box_column, box_column + 3)
            }
            assert box == expected


def test_create_empty_board_returns_nine_by_nine_grid():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_is_independent_of_original_board():
    board = sudoku_logic.create_empty_board()
    copied_board = sudoku_logic.deep_copy(board)

    copied_board[0][0] = 1

    assert board[0][0] == sudoku_logic.EMPTY
    assert copied_board[0][0] == 1


def test_is_safe_checks_candidate_against_row_column_and_box():
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.is_safe(board, 0, 0, 1)

    board[0][0] = 1
    assert not sudoku_logic.is_safe(board, 0, 1, 1)
    assert not sudoku_logic.is_safe(board, 1, 0, 1)
    assert not sudoku_logic.is_safe(board, 1, 1, 1)


def test_fill_board_completes_a_valid_sudoku():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    _assert_valid_solution(board)


def test_remove_cells_leaves_the_requested_number_of_clues():
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.fill_board(board)

    sudoku_logic.remove_cells(board, clues=40)

    assert sum(cell != sudoku_logic.EMPTY for row in board for cell in row) == 40


def test_generate_puzzle_returns_consistent_puzzle_and_solution():
    clues = 35

    puzzle, solution = sudoku_logic.generate_puzzle(clues)

    _assert_valid_solution(solution)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues
    assert sudoku_logic.count_solutions(puzzle) == 1
    assert all(
        puzzle[row][column] in (sudoku_logic.EMPTY, solution[row][column])
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )


def test_count_solutions_returns_one_for_a_completed_valid_board():
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.fill_board(board)

    assert sudoku_logic.count_solutions(board) == 1


def test_count_solutions_stops_after_finding_multiple_solutions():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(board) == 2


def test_count_solutions_returns_zero_for_conflicting_clues():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 1

    assert sudoku_logic.count_solutions(board) == 0


@pytest.mark.parametrize("clues", [16, 0, 82, True, 35.0])
def test_generate_puzzle_rejects_invalid_clue_counts(clues):
    with pytest.raises(ValueError, match="Clue count must be an integer"):
        sudoku_logic.generate_puzzle(clues)


def test_generate_puzzle_returns_unique_consistent_results_repeatedly():
    for _ in range(3):
        puzzle, solution = sudoku_logic.generate_puzzle(40)

        _assert_valid_solution(solution)
        assert sudoku_logic.count_solutions(puzzle) == 1
        assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 40
        assert all(
            puzzle[row][column] in (sudoku_logic.EMPTY, solution[row][column])
            for row in range(sudoku_logic.SIZE)
            for column in range(sudoku_logic.SIZE)
        )


def test_generate_puzzle_raises_when_unique_generation_attempts_are_exhausted(
    monkeypatch,
):
    def fail_removal(board, clues):
        raise sudoku_logic.SudokuGenerationError("No candidate found.")

    monkeypatch.setattr(sudoku_logic, "remove_cells", fail_removal)

    with pytest.raises(sudoku_logic.SudokuGenerationError, match="after 10 attempts"):
        sudoku_logic.generate_puzzle(35)


def test_count_solutions_accepts_tuple_board_without_mutating_input():
    board = tuple(tuple(0 for _ in range(9)) for _ in range(9))
    original_board = board

    result = sudoku_logic.count_solutions(board)

    assert result == 2
    assert board == original_board
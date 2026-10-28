import copy
import random

SIZE = 9
EMPTY = 0
MIN_CLUES = 17
MAX_CLUES = SIZE * SIZE
_FULL_MASK = (1 << SIZE) - 1
_MAX_GENERATION_ATTEMPTS = 10


class SudokuGenerationError(RuntimeError):
    """Raised when a unique puzzle cannot be generated for the requested clues."""


def _validate_clue_count(clues):
    if type(clues) is not int or not MIN_CLUES <= clues <= MAX_CLUES:
        raise ValueError(
            f"Clue count must be an integer between {MIN_CLUES} and {MAX_CLUES}."
        )


def _validate_board_shape(board):
    if not isinstance(board, (list, tuple)) or len(board) != SIZE:
        raise ValueError(f"Board must contain exactly {SIZE} rows.")
    if any(not isinstance(row, (list, tuple)) or len(row) != SIZE for row in board):
        raise ValueError(f"Each board row must contain exactly {SIZE} cells.")


def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board):
    """Count solutions up to two, returning early when uniqueness is disproved."""
    _validate_board_shape(board)
    working = deep_copy(board)
    row_masks = [0] * SIZE
    column_masks = [0] * SIZE
    box_masks = [0] * SIZE

    for row in range(SIZE):
        for column in range(SIZE):
            value = working[row][column]
            if type(value) is not int or not EMPTY <= value <= SIZE:
                raise ValueError("Board cells must be integers between 0 and 9.")
            if value == EMPTY:
                continue

            bit = 1 << (value - 1)
            box = (row // 3) * 3 + column // 3
            if row_masks[row] & bit or column_masks[column] & bit or box_masks[box] & bit:
                return 0
            row_masks[row] |= bit
            column_masks[column] |= bit
            box_masks[box] |= bit

    def search():
        best_cell = None
        best_candidates = 0
        fewest_candidates = SIZE + 1

        for row in range(SIZE):
            for column in range(SIZE):
                if working[row][column] != EMPTY:
                    continue
                box = (row // 3) * 3 + column // 3
                candidates = _FULL_MASK & ~(
                    row_masks[row] | column_masks[column] | box_masks[box]
                )
                candidate_count = candidates.bit_count()
                if candidate_count == 0:
                    return 0
                if candidate_count < fewest_candidates:
                    best_cell = (row, column, box)
                    best_candidates = candidates
                    fewest_candidates = candidate_count
                    if candidate_count == 1:
                        break
            if fewest_candidates == 1:
                break

        if best_cell is None:
            return 1

        row, column, box = best_cell
        solutions = 0
        while best_candidates:
            bit = best_candidates & -best_candidates
            best_candidates &= best_candidates - 1
            working[row][column] = bit.bit_length()
            row_masks[row] |= bit
            column_masks[column] |= bit
            box_masks[box] |= bit

            solutions += search()

            working[row][column] = EMPTY
            row_masks[row] ^= bit
            column_masks[column] ^= bit
            box_masks[box] ^= bit
            if solutions >= 2:
                return 2

        return solutions

    return search()


def remove_cells(board, clues):
    _validate_clue_count(clues)
    _validate_board_shape(board)

    if count_solutions(board) != 1:
        raise ValueError("Cell removal requires a board with exactly one solution.")

    cells = [(row, column) for row in range(SIZE) for column in range(SIZE)]
    random.shuffle(cells)
    remaining = sum(cell != EMPTY for row in board for cell in row)

    for row, column in cells:
        if remaining <= clues:
            break
        value = board[row][column]
        if value == EMPTY:
            continue

        board[row][column] = EMPTY
        if count_solutions(board) == 1:
            remaining -= 1
        else:
            board[row][column] = value

    if remaining != clues:
        raise SudokuGenerationError(
            f"Could not generate a unique puzzle with exactly {clues} clues."
        )


def generate_puzzle(clues=35):
    _validate_clue_count(clues)

    for _ in range(_MAX_GENERATION_ATTEMPTS):
        solution = create_empty_board()
        if not fill_board(solution):
            continue
        puzzle = deep_copy(solution)
        try:
            remove_cells(puzzle, clues)
        except SudokuGenerationError:
            continue

        if count_solutions(puzzle) == 1:
            return puzzle, solution

    raise SudokuGenerationError(
        f"Unable to generate a unique puzzle with exactly {clues} clues "
        f"after {_MAX_GENERATION_ATTEMPTS} attempts."
    )

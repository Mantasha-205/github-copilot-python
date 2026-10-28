class InputValidationError(ValueError):
    """Raised when a request contains invalid Sudoku input."""


DIFFICULTY_CLUES = {
    "easy": 40,
    "medium": 35,
    "hard": 30,
}


def validate_clue_count(values):
    if not values:
        return 35
    if len(values) != 1:
        raise InputValidationError("The clues parameter must be provided once.")

    try:
        clues = int(values[0])
    except (TypeError, ValueError):
        raise InputValidationError("The clues parameter must be an integer.") from None

    if not 17 <= clues <= 81:
        raise InputValidationError("The clues parameter must be between 17 and 81.")

    return clues


def validate_game_clues(difficulty_values, clue_values):
    if difficulty_values and clue_values:
        raise InputValidationError(
            "Specify either the difficulty or clues parameter, not both."
        )

    if not difficulty_values:
        return validate_clue_count(clue_values)
    if len(difficulty_values) != 1:
        raise InputValidationError(
            "The difficulty parameter must be provided once."
        )

    difficulty = difficulty_values[0].strip().lower()
    if difficulty not in DIFFICULTY_CLUES:
        options = ", ".join(DIFFICULTY_CLUES)
        raise InputValidationError(
            f"Difficulty must be one of: {options}."
        )

    return DIFFICULTY_CLUES[difficulty]


def validate_board_payload(payload):
    if not isinstance(payload, dict):
        raise InputValidationError("The request body must be a JSON object.")

    if "board" not in payload:
        raise InputValidationError("The request body must include a board.")

    board = payload["board"]
    if not isinstance(board, list) or len(board) != 9:
        raise InputValidationError("The board must contain exactly 9 rows.")

    for row_index, row in enumerate(board):
        if not isinstance(row, list) or len(row) != 9:
            raise InputValidationError(
                f"Board row {row_index} must contain exactly 9 cells."
            )
        for column_index, value in enumerate(row):
            if type(value) is not int or not 0 <= value <= 9:
                raise InputValidationError(
                    f"Board cell ({row_index}, {column_index}) must be an integer "
                    "between 0 and 9."
                )

    return board

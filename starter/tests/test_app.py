from pathlib import Path

import pytest

import app as app_module


def _valid_solution():
    return [
        [((row * 3 + row // 3 + column) % 9) + 1 for column in range(9)]
        for row in range(9)
    ]


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    previous_current = dict(app_module.CURRENT)
    app_module.CURRENT.update({"puzzle": None, "solution": None})

    with app_module.app.test_client() as test_client:
        yield test_client

    app_module.CURRENT.update(previous_current)


@pytest.mark.parametrize(
    ("query_string", "expected_clues"),
    [
        ({}, 35),
        ({"clues": "42"}, 42),
        ({"difficulty": "easy"}, 40),
        ({"difficulty": "medium"}, 35),
        ({"difficulty": "hard"}, 30),
    ],
)
def test_new_game_generates_and_stores_puzzle(
    client, monkeypatch, query_string, expected_clues
):
    puzzle = [[0] * 9 for _ in range(9)]
    solution = [[1] * 9 for _ in range(9)]
    received_clues = []

    def generate_puzzle(clues):
        received_clues.append(clues)
        return puzzle, solution

    monkeypatch.setattr(app_module.sudoku_logic, "generate_puzzle", generate_puzzle)

    response = client.get("/new", query_string=query_string)

    assert response.status_code == 200
    assert response.get_json() == {"puzzle": puzzle}
    assert received_clues == [expected_clues]
    assert app_module.CURRENT == {"puzzle": puzzle, "solution": solution}


def test_index_returns_sudoku_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"<h1>Sudoku Game</h1>" in response.data


def test_check_solution_returns_bad_request_when_no_game_is_active(client):
    response = client.post("/check", json={"board": [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No game in progress"}


def test_check_solution_returns_no_incorrect_cells_for_solution(client):
    solution = _valid_solution()
    app_module.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": solution})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": []}


def test_check_solution_reports_incorrect_cell_coordinates(client):
    solution = _valid_solution()
    board = [row.copy() for row in solution]
    board[0][0] = 2
    board[8][8] = 7
    app_module.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [[0, 0], [8, 8]]}


def test_hint_returns_one_correct_value_without_revealing_solution(client):
    solution = _valid_solution()
    puzzle = [row.copy() for row in solution]
    puzzle[0][0] = 0
    puzzle[0][1] = 0
    app_module.CURRENT.update({"puzzle": puzzle, "solution": solution})
    board = [row.copy() for row in puzzle]
    board[0][0] = 4

    response = client.post("/hint", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {"row": 0, "col": 1, "value": solution[0][1]}
    assert "solution" not in response.get_json()


def test_hint_returns_bad_request_when_game_has_no_available_empty_cell(client):
    solution = _valid_solution()
    app_module.CURRENT.update({"puzzle": solution, "solution": solution})

    response = client.post("/hint", json={"board": solution})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No empty cells available for a hint."}


def test_hint_requires_an_active_game(client):
    response = client.post("/hint", json={"board": [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No game in progress"}


def test_hint_rejects_invalid_board_payload(client):
    response = client.post("/hint", json={"board": [[0] * 9 for _ in range(8)]})

    assert response.status_code == 400
    assert response.get_json() == {"error": "The board must contain exactly 9 rows."}


def test_check_solution_returns_json_error_for_malformed_json(client):
    response = client.post(
        "/check", data='{"board": [}', content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Request body must contain valid JSON."}


def test_check_solution_rejects_non_json_content_type(client):
    response = client.post("/check", data="{}", content_type="text/plain")

    assert response.status_code == 415
    assert response.get_json() == {
        "error": "Content-Type must be application/json."
    }


@pytest.mark.parametrize(
    ("payload", "expected_error"),
    [
        ("null", "The request body must be a JSON object."),
        ({}, "The request body must include a board."),
        ({"board": "not a board"}, "The board must contain exactly 9 rows."),
        ({"board": [[0] * 9 for _ in range(8)]},
         "The board must contain exactly 9 rows."),
        (
            {"board": [[0] * 8] + [[0] * 9 for _ in range(8)]},
            "Board row 0 must contain exactly 9 cells.",
        ),
        (
            {"board": [[0] * 8 + [10]] + [[0] * 9 for _ in range(8)]},
            "Board cell (0, 8) must be an integer between 0 and 9.",
        ),
        (
            {"board": [[0] * 8 + [True]] + [[0] * 9 for _ in range(8)]},
            "Board cell (0, 8) must be an integer between 0 and 9.",
        ),
    ],
)
def test_check_solution_rejects_invalid_board_payload(client, payload, expected_error):
    if isinstance(payload, str):
        response = client.post(
            "/check", data=payload, content_type="application/json"
        )
    else:
        response = client.post("/check", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": expected_error}


@pytest.mark.parametrize(
    ("query_string", "expected_error"),
    [
        ({"clues": "many"}, "The clues parameter must be an integer."),
        ({"clues": "16"}, "The clues parameter must be between 17 and 81."),
        ({"clues": "0"}, "The clues parameter must be between 17 and 81."),
        ({"clues": "82"}, "The clues parameter must be between 17 and 81."),
        (
            [("clues", "35"), ("clues", "40")],
            "The clues parameter must be provided once.",
        ),
        (
            {"difficulty": "expert"},
            "Difficulty must be one of: easy, medium, hard.",
        ),
        (
            [("difficulty", "easy"), ("difficulty", "hard")],
            "The difficulty parameter must be provided once.",
        ),
        (
            {"difficulty": "easy", "clues": "40"},
            "Specify either the difficulty or clues parameter, not both.",
        ),
    ],
)
def test_new_game_rejects_invalid_clue_parameters(
    client, query_string, expected_error
):
    response = client.get("/new", query_string=query_string)

    assert response.status_code == 400
    assert response.get_json() == {"error": expected_error}


@pytest.mark.parametrize(
    ("difficulty", "expected_clues"),
    [("easy", 40), ("medium", 35), ("hard", 30)],
)
def test_each_difficulty_generates_a_unique_puzzle(difficulty, expected_clues):
    assert app_module.request_validation.DIFFICULTY_CLUES[difficulty] == expected_clues
    puzzle, solution = app_module.sudoku_logic.generate_puzzle(expected_clues)

    assert sum(cell != 0 for row in puzzle for cell in row) == expected_clues
    assert app_module.sudoku_logic.count_solutions(puzzle) == 1
    assert all(
        puzzle[row][column] in (0, solution[row][column])
        for row in range(app_module.sudoku_logic.SIZE)
        for column in range(app_module.sudoku_logic.SIZE)
    )


def test_difficulty_selector_is_rendered_and_prefilled_cells_are_locked(client):
    response = client.get("/")
    script = Path(app_module.app.root_path) / "static" / "main.js"
    with script.open(encoding="utf-8") as javascript:
        source = javascript.read()

    assert response.status_code == 200
    assert b'<select id="difficulty" name="difficulty">' in response.data
    assert b'value="easy">Easy' in response.data
    assert b'value="medium" selected>Medium' in response.data
    assert b'value="hard">Hard' in response.data
    assert "inp.disabled = true;" in source
    assert "inp.classList.add('prefilled');" in source


def test_phase_four_controls_and_delegated_input_handler_are_present(client):
    response = client.get("/")
    script = Path(app_module.app.root_path) / "static" / "main.js"
    with script.open(encoding="utf-8") as javascript:
        source = javascript.read()

    assert b'id="check-solution"' in response.data
    assert b'id="get-hint"' in response.data
    assert b'id="hints-used"' in response.data
    assert b'id="completion"' in response.data
    assert b'id="player-name"' in response.data
    assert (
        "document.getElementById('sudoku-board').addEventListener("
        "'input', handleBoardInput)"
    ) in source
    assert "input.addEventListener('input'" not in source
    assert "function updateConflicts()" in source
    assert "function finishGame()" in source


def test_phase_five_timer_and_leaderboard_ui_are_wired(client):
    response = client.get("/")
    script = Path(app_module.app.root_path) / "static" / "main.js"
    with script.open(encoding="utf-8") as javascript:
        source = javascript.read()

    assert b'id="timer"' in response.data
    assert b'id="save-score"' in response.data
    assert b'id="leaderboard-entries"' in response.data
    assert all(
        heading in response.data
        for heading in (
            b"Name",
            b"Time",
            b"Hints used",
            b"Difficulty",
        )
    )
    assert "setInterval(updateTimerDisplay, 1000)" in source
    assert "function startTimer()" in source
    assert "function stopTimer()" in source
    assert "startTimer();" in source
    assert "stopTimer();" in source
    assert "localStorage.getItem(LEADERBOARD_STORAGE_KEY)" in source
    assert "localStorage.setItem(LEADERBOARD_STORAGE_KEY" in source
    assert ".sort((first, second) => first.timeSeconds - second.timeSeconds)" in source
    assert ".slice(0, 10)" in source
    assert all(
        field in source
        for field in ("name: name.slice(0, 40)", "timeSeconds:", "hintsUsed,", "difficulty:")
    )
    assert "Invalid saved scores were ignored." in source
    assert "Browser storage is unavailable" in source


def test_phase_six_theme_control_and_accessible_responsive_page(client):
    response = client.get("/")
    script = Path(app_module.app.root_path) / "static" / "main.js"
    styles = Path(app_module.app.root_path) / "static" / "styles.css"
    with script.open(encoding="utf-8") as javascript:
        source = javascript.read()
    with styles.open(encoding="utf-8") as stylesheet:
        css = stylesheet.read()

    assert response.status_code == 200
    assert b'name="viewport"' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'aria-pressed="false"' in response.data
    assert b'role="group" aria-label="Sudoku puzzle board"' in response.data
    assert b'<main>' in response.data
    assert "const THEME_STORAGE_KEY = 'sudokuTheme';" in source
    assert "function loadTheme()" in source
    assert "function toggleTheme()" in source
    assert "localStorage.getItem(THEME_STORAGE_KEY)" in source
    assert "localStorage.setItem(THEME_STORAGE_KEY, nextTheme)" in source
    assert 'data-theme="dark"' in css
    assert "--alternate-box-background" in css
    assert "@media (max-width: 520px)" in css
    assert ".sudoku-cell:focus-visible" in css
    assert "#sudoku-board .sudoku-cell.prefilled" in css
    assert "#sudoku-board .sudoku-cell.incorrect" in css
    assert "#sudoku-board .sudoku-cell.conflict" in css
    assert "#sudoku-board .sudoku-cell.hinted" in css
    assert "width: min(94vw, 450px)" in css


def test_leaderboard_storage_errors_do_not_report_a_saved_score(client):
    client.get("/")
    script = Path(app_module.app.root_path) / "static" / "main.js"
    with script.open(encoding="utf-8") as javascript:
        source = javascript.read()

    read_failure = source.index(
        "Score could not be saved because browser storage is unavailable."
    )
    write_operation = source.index(
        "localStorage.setItem(LEADERBOARD_STORAGE_KEY"
    )
    write_failure = source.index(
        "Browser storage is unavailable; this score was not saved."
    )
    success_message = source.index(
        "Your score was saved.",
        write_operation,
    )

    assert read_failure < write_operation
    assert write_operation < write_failure < success_message
    assert "return;" in source[read_failure:write_operation]
    assert "return;" in source[write_failure:success_message]


def test_new_game_returns_json_error_when_unique_generation_fails(client, monkeypatch):
    def fail_generation(clues):
        raise app_module.sudoku_logic.SudokuGenerationError("Generation failed.")

    monkeypatch.setattr(
        app_module.sudoku_logic, "generate_puzzle", fail_generation
    )

    response = client.get("/new")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Generation failed."}

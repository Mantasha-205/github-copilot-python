# Refactor a Sudoku Game Written in Python Flask

## Project Overview

This project refactors a legacy Sudoku game built using Python and Flask into a more maintainable, user-friendly, and responsive web application with the assistance of GitHub Copilot.

The application generates Sudoku puzzles, validates user input, provides hints, tracks solving time, and maintains a leaderboard of the ten fastest completed games. It also supports light and dark themes and a responsive layout for desktop and mobile screens.

## Features Implemented

- **Sudoku Puzzle Generation:** Generates valid Sudoku puzzles with exactly one unique solution.
- **Difficulty Selection:** Supports Easy, Medium, and Hard difficulty levels with different numbers of prefilled clues.
- **Locked Clues:** Prevents users from modifying prefilled cells.
- **Input Validation:** Provides immediate visual feedback for invalid entries and conflicts in rows, columns, and 3×3 boxes.
- **Solution Checker:** Checks the user's current entries and highlights incorrect cells.
- **Hint System:** Fills one correct empty cell, visually identifies the hint, and tracks the number of hints used.
- **Timer:** Tracks the time taken to solve a puzzle, resets when a new game starts, and stops upon correct completion.
- **Completion Message:** Displays a congratulatory message with the elapsed time and hints used.
- **Top 10 Leaderboard:** Records the player's name, completion time, hints used, and difficulty level, and displays the ten fastest games.
- **Local Storage:** Saves leaderboard entries and theme preferences in the browser's `localStorage`.
- **Light and Dark Themes:** Allows users to switch between light and dark modes.
- **Responsive Design:** Adapts the Sudoku board, controls, and leaderboard to different screen sizes.
- **Accessible Interface:** Includes labeled controls, visible keyboard focus, and clear status messages.
- **Automated Tests:** Includes pytest tests for Sudoku logic, puzzle generation, validation, Flask routes, and other implemented functionality.

## Technologies Used

- Python 3
- Flask
- HTML5
- CSS3
- JavaScript
- pytest
- Browser `localStorage`
- GitHub Copilot

## Getting Started

### Prerequisites

- Python 3 installed on your system
- A modern web browser such as Google Chrome, Microsoft Edge, or Firefox
- Git installed if cloning the repository
- The project repository cloned to your local machine

### Installation

1. Fork this repository to your GitHub account.
2. Clone your fork to your local machine.
3. Open PowerShell at the root of the cloned repository.
4. Move into the `starter` directory:

```powershell
Set-Location ".\starter"
```

5. Install the required dependencies using the existing virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the virtual environment does not exist, create and activate it from the `starter` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

6. Start the Flask application from the `starter` directory:

```powershell
.\.venv\Scripts\python.exe app.py
```

7. Open the following URL in your browser:

http://127.0.0.1:5000/

To stop the Flask server, press `Ctrl+C` in the terminal.

## Running Tests

Run the automated test suite from the `starter` directory using the existing Python virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The test suite covers Sudoku logic, unique-solution puzzle generation, request validation, Flask endpoints, difficulty selection, locked prefilled cells, and other implemented functionality.

The latest recorded test run completed successfully with **55 tests passed in 1.43 seconds**. The `git diff --check` command also completed without reporting errors. Test counts and execution times may change as the project evolves.

Run the full test suite after significant code changes. Before submitting the project, ensure that all tests pass and review any reported errors.

## Project Structure

```text
github-copilot-python/
├── Screenshots/
├── starter/
│   ├── app.py
│   ├── request_validation.py
│   ├── sudoku_logic.py
│   ├── requirements.txt
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   ├── main.js
│   │   └── styles.css
│   └── tests/
│       ├── test_app.py
│       └── test_sudoku_logic.py
├── instruction.md
├── README.md
├── .gitignore
├── CODEOWNERS
└── LICENSE.txt
```

This is a simplified view of the project structure. Additional files, tests, and configuration files may be present in the repository.

## Project Instructions and Development Process

GitHub Copilot was used to analyze and refactor the legacy application in incremental phases. Changes were reviewed and tested after implementation to preserve existing functionality and improve maintainability.

The project emphasizes modular code, reusable logic, input validation, graceful error handling, accessible styling, and automated testing.

The implementation was organized into six phases:

1. **Phase 1 — Baseline Testing and Validation:** Established automated tests and improved request validation.
2. **Phase 2 — Unique-Solution Generation:** Added solution counting and ensured generated puzzles have exactly one solution.
3. **Phase 3 — Difficulty Selection:** Added Easy, Medium, and Hard difficulty levels and preserved locked clues.
4. **Phase 4 — Gameplay Enhancements:** Added immediate conflict feedback, solution checking, hints, and completion messaging.
5. **Phase 5 — Timer and Leaderboard:** Added elapsed-time tracking, score saving, and a Top 10 leaderboard.
6. **Phase 6 — User Interface Improvements:** Added light/dark themes, alternating 3×3 box colors, responsive styling, and accessibility improvements.

## Leaderboard and Theme Storage

The Top 10 fastest completed games are stored in the current browser's local storage. The leaderboard records the player's name, completion time, hints used, and difficulty level.

Theme preferences are also stored in browser `localStorage`. These values are local to the browser origin and profile being used. They are not uploaded to the Flask server and are not automatically shared across browsers or devices. Clearing browser site data may remove saved leaderboard entries and theme preferences.

## Screenshots and Evidence

The `Screenshots/` directory contains development evidence, including project setup, baseline tests, GitHub Copilot prompts and responses, implementation milestones, test results, and Sudoku gameplay demonstrations.

These screenshots document the development process and provide evidence of the implemented features.

## Limitations

- Leaderboard scores and theme preferences are stored locally in the browser rather than in a central database.
- Saved data is not automatically synchronized between devices or browser profiles.
- The application requires the Flask development server to be running locally to access the game.

## Conclusion

This project demonstrates how GitHub Copilot can assist with incrementally refactoring a legacy Flask application, improving code quality, adding interactive Sudoku features, and enhancing the user experience. Automated testing and screenshot evidence support the development and validation process.

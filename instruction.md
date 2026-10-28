# GitHub Copilot Instructions — Flask Sudoku Project

## Project Goal
Refactor the existing Python Flask Sudoku application into a modern, maintainable, responsive Sudoku game. Work incrementally, preserve existing functionality, and use the existing project structure.

## Important Rules
1. Work only inside the `starter/` directory for application code, tests, and dependencies.
2. Read the existing code before making changes.
3. Implement one phase at a time. Do not start the next phase until the current phase is implemented, tested, and reviewed.
4. Do not overwrite working functionality unnecessarily.
5. Explain the files changed, the reason for each change, and the test results after every phase.
6. Ask before making destructive changes or deleting existing code.
7. Keep the code modular, reusable, readable, and properly documented.
8. Handle errors gracefully and avoid exposing sensitive information.
9. Do not claim a feature works unless it has been tested.
10. Run the full pytest suite after each major change and fix any regressions before continuing.

## Testing Requirements
- Use the existing Python virtual environment in `starter/.venv/`.
- Run tests from the `starter/` directory using:

  `.\.venv\Scripts\python.exe -m pytest -v`

- Preserve existing tests and add regression tests for new features.
- Check code formatting issues with `git diff --check`.
- Document the test command in `README.md`.
- Save the initial baseline test screenshot as `Screenshots/initial_tests.png`.
- Save relevant Copilot prompt and response screenshots for each major milestone in the `Screenshots/` directory.
- Use descriptive screenshot filenames.

## Required Features
1. Generate valid Sudoku puzzles with exactly one unique solution.
2. Provide Easy, Medium, and Hard difficulty levels with different numbers of prefilled clues.
3. Keep original puzzle clues locked.
4. Highlight invalid entries and row, column, and 3×3 box conflicts.
5. Provide a Check Solution button.
6. Provide a Hint button that reveals one correct empty cell and tracks hints used.
7. Display a timer that starts with a new game and stops when the puzzle is correctly completed.
8. Show a congratulatory message with completion time and hints used.
9. Allow the player to enter a name and save a completed score.
10. Display the Top 10 fastest games, sorted by completion time.
11. Store leaderboard data in browser localStorage and handle missing, invalid, or unavailable storage gracefully.
12. Add a light/dark theme toggle and persist the theme preference when browser storage is available.
13. Use alternating 3×3 box backgrounds and clear Sudoku grid boundaries.
14. Make the layout responsive for desktop and mobile devices.
15. Provide accessible labels, visible keyboard focus, and appropriate status messages.

## Implementation Workflow
- Inspect the current code and tests before each phase.
- Propose a small, focused implementation plan.
- Implement only the requested phase.
- Review the diff and check for unrelated changes.
- Run the complete pytest suite and any relevant browser checks.
- Report passed and failed tests honestly.
- Stop after the requested phase and wait for approval before proceeding.

## Final Verification
Before submission:
- Run all tests.
- Verify every required feature in the browser.
- Check leaderboard persistence after refreshing the same browser origin.
- Test both themes and a narrow mobile viewport.
- Update `README.md` with setup, run, test, and feature instructions.
- Ensure the `Screenshots/` directory contains the required evidence.
- Review the final project structure and Git diff.

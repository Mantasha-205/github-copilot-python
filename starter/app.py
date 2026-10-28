from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest

import request_validation
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution.
CURRENT = {
    'puzzle': None,
    'solution': None
}


def _get_request_board():
    if not request.is_json:
        return None, (jsonify({'error': 'Content-Type must be application/json.'}), 415)

    try:
        data = request.get_json()
    except BadRequest:
        return None, (jsonify({'error': 'Request body must contain valid JSON.'}), 400)

    try:
        return request_validation.validate_board_payload(data), None
    except request_validation.InputValidationError as error:
        return None, (jsonify({'error': str(error)}), 400)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new_game():
    try:
        clues = request_validation.validate_game_clues(
            request.args.getlist('difficulty'),
            request.args.getlist('clues'),
        )
    except request_validation.InputValidationError as error:
        return jsonify({'error': str(error)}), 400

    try:
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
    except sudoku_logic.SudokuGenerationError as error:
        return jsonify({'error': str(error)}), 500

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})


@app.route('/check', methods=['POST'])
def check_solution():
    board, error_response = _get_request_board()
    if error_response is not None:
        return error_response

    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def get_hint():
    board, error_response = _get_request_board()
    if error_response is not None:
        return error_response

    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    for row in range(sudoku_logic.SIZE):
        for column in range(sudoku_logic.SIZE):
            if puzzle[row][column] == sudoku_logic.EMPTY and board[row][column] == sudoku_logic.EMPTY:
                return jsonify({
                    'row': row,
                    'col': column,
                    'value': solution[row][column],
                })

    return jsonify({'error': 'No empty cells available for a hint.'}), 400


if __name__ == '__main__':
    app.run(debug=True)
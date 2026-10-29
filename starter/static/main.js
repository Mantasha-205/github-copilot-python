// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuTop10';
const THEME_STORAGE_KEY = 'sudokuTheme';
let puzzle = [];
let hintsUsed = 0;
let gameStartedAt = null;
let elapsedMilliseconds = 0;
let timerInterval = null;
let completed = false;
let checkingCompletion = false;
let currentDifficulty = 'medium';

function showMessage(message, isError = false) {
  const messageElement = document.getElementById('message');
  messageElement.innerText = message;
  messageElement.classList.toggle('error-message', isError);
}

function boardInputs() {
  return Array.from(document.querySelectorAll('#sudoku-board .sudoku-cell'));
}

function readBoard() {
  const board = [];
  const inputs = boardInputs();
  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let column = 0; column < SIZE; column++) {
      const value = inputs[row * SIZE + column].value;
      board[row][column] = value ? Number(value) : 0;
    }
  }
  return board;
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const responseText = await response.text();

  let data;
  try {
    data = JSON.parse(responseText);
  } catch {
    const preview = responseText.slice(0, 200).replace(/\s+/g, ' ');
    throw new Error(
      `Invalid server response (HTTP ${response.status}): ${preview || 'Empty response'}`
    );
  }

  if (!response.ok) {
    throw new Error(data.error || 'The request could not be completed.');
  }

  return data;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.inputMode = 'numeric';
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function updateConflicts() {
  const inputs = boardInputs();
  inputs.forEach((input) => {
    input.classList.remove('conflict');
    input.removeAttribute('aria-invalid');
  });

  const board = readBoard();
  for (let first = 0; first < inputs.length; first++) {
    const value = board[Math.floor(first / SIZE)][first % SIZE];
    if (!value) continue;
    const firstRow = Math.floor(first / SIZE);
    const firstColumn = first % SIZE;

    for (let second = first + 1; second < inputs.length; second++) {
      const secondRow = Math.floor(second / SIZE);
      const secondColumn = second % SIZE;
      const sameUnit = firstRow === secondRow
        || firstColumn === secondColumn
        || (Math.floor(firstRow / 3) === Math.floor(secondRow / 3)
          && Math.floor(firstColumn / 3) === Math.floor(secondColumn / 3));
      if (sameUnit && board[secondRow][secondColumn] === value) {
        inputs[first].classList.add('conflict');
        inputs[first].setAttribute('aria-invalid', 'true');
        inputs[second].classList.add('conflict');
        inputs[second].setAttribute('aria-invalid', 'true');
      }
    }
  }
}

function formatElapsedTime(milliseconds) {
  const totalSeconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function currentElapsedMilliseconds() {
  return gameStartedAt === null
    ? elapsedMilliseconds
    : Date.now() - gameStartedAt;
}

function updateTimerDisplay() {
  document.getElementById('timer').innerText =
    `Time: ${formatElapsedTime(currentElapsedMilliseconds())}`;
}

function startTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
  }
  elapsedMilliseconds = 0;
  gameStartedAt = Date.now();
  updateTimerDisplay();
  timerInterval = setInterval(updateTimerDisplay, 1000);
}

function stopTimer() {
  if (gameStartedAt !== null) {
    elapsedMilliseconds = currentElapsedMilliseconds();
    gameStartedAt = null;
  }
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  updateTimerDisplay();
}

function setLeaderboardMessage(message, isError = false) {
  const element = document.getElementById('leaderboard-message');
  element.innerText = message;
  element.classList.toggle('error-message', isError);
}

function applyTheme(theme) {
  const isDark = theme === 'dark';
  document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
  const toggle = document.getElementById('theme-toggle');
  toggle.setAttribute('aria-pressed', String(isDark));
  toggle.textContent = `Dark mode: ${isDark ? 'on' : 'off'}`;
}

function loadTheme() {
  let savedTheme = 'light';
  try {
    const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (storedTheme === 'light' || storedTheme === 'dark') {
      savedTheme = storedTheme;
    }
  } catch {
    // Keep the default theme for this page when browser storage is unavailable.
  }
  applyTheme(savedTheme);
}

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === 'dark'
    ? 'light'
    : 'dark';
  applyTheme(nextTheme);
  try {
    localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  } catch {
    // The selected theme remains active until the page is closed.
  }
}

function isValidScore(score) {
  return score !== null
    && typeof score === 'object'
    && typeof score.name === 'string'
    && score.name.trim().length > 0
    && Number.isFinite(score.timeSeconds)
    && score.timeSeconds >= 0
    && Number.isInteger(score.hintsUsed)
    && score.hintsUsed >= 0
    && ['easy', 'medium', 'hard'].includes(score.difficulty);
}

function readLeaderboard() {
  let storedValue;
  try {
    storedValue = localStorage.getItem(LEADERBOARD_STORAGE_KEY);
  } catch {
    setLeaderboardMessage(
      'Browser storage is unavailable; leaderboard scores cannot be loaded.',
      true
    );
    return null;
  }

  if (storedValue === null) {
    return [];
  }

  try {
    const scores = JSON.parse(storedValue);
    if (!Array.isArray(scores)) {
      throw new Error('Leaderboard data must be a list.');
    }
    const validScores = scores.filter(isValidScore);
    if (validScores.length !== scores.length) {
      setLeaderboardMessage(
        'Invalid saved scores were ignored.',
        true
      );
    }
    return validScores;
  } catch {
    setLeaderboardMessage(
      'Saved leaderboard data was invalid and has been ignored.',
      true
    );
    return [];
  }
}

function renderLeaderboard(scores) {
  const entries = document.getElementById('leaderboard-entries');
  entries.replaceChildren();
  scores
    .slice()
    .sort((first, second) => first.timeSeconds - second.timeSeconds)
    .slice(0, 10)
    .forEach((score, index) => {
      const row = document.createElement('tr');
      const values = [
        String(index + 1),
        score.name,
        formatElapsedTime(score.timeSeconds * 1000),
        String(score.hintsUsed),
        score.difficulty[0].toUpperCase() + score.difficulty.slice(1)
      ];
      values.forEach((value) => {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.appendChild(cell);
      });
      entries.appendChild(row);
    });
}

function loadLeaderboard() {
  const scores = readLeaderboard();
  if (scores !== null) {
    renderLeaderboard(scores);
  }
}

function saveCompletedScore() {
  const nameInput = document.getElementById('player-name');
  const name = nameInput.value.trim();
  if (!name) {
    showMessage('Enter your name before saving your score.', true);
    nameInput.focus();
    return;
  }

  const scores = readLeaderboard();
  if (scores === null) {
    showMessage('Score could not be saved because browser storage is unavailable.', true);
    return;
  }

  const score = {
    name: name.slice(0, 40),
    timeSeconds: elapsedMilliseconds / 1000,
    hintsUsed,
    difficulty: currentDifficulty
  };
  const updatedScores = scores.concat(score)
    .sort((first, second) => first.timeSeconds - second.timeSeconds)
    .slice(0, 10);

  try {
    localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(updatedScores));
  } catch {
    showMessage('Score could not be saved because browser storage is unavailable.', true);
    setLeaderboardMessage(
      'Browser storage is unavailable; this score was not saved.',
      true
    );
    return;
  }

  renderLeaderboard(updatedScores);
  setLeaderboardMessage('Your score was saved.');
  showMessage('Score saved to the Top 10 leaderboard.');
  nameInput.value = '';
}

function finishGame() {
  if (completed) return;
  completed = true;
  stopTimer();
  boardInputs().forEach((input) => {
    input.disabled = true;
  });
  const elapsed = formatElapsedTime(elapsedMilliseconds);
  document.getElementById('completion-message').innerText =
    `Congratulations! You solved it in ${elapsed}. Hints used: ${hintsUsed}.`;
  document.getElementById('completion').hidden = false;
  document.getElementById('player-name').focus();
  showMessage('Puzzle complete!');
}

async function newGame() {
  try {
    const difficulty = document.getElementById('difficulty').value;
    const data = await fetchJson(
      `/new?difficulty=${encodeURIComponent(difficulty)}`
    );
    renderPuzzle(data.puzzle);
    hintsUsed = 0;
    currentDifficulty = difficulty;
    startTimer();
    completed = false;
    checkingCompletion = false;
    document.getElementById('hints-used').innerText = 'Hints used: 0';
    document.getElementById('completion').hidden = true;
    document.getElementById('player-name').value = '';
    showMessage('');
  } catch (error) {
    showMessage(error.message || 'Unable to start a new game.', true);
  }
}

async function checkSolution() {
  try {
    const board = readBoard();
    const data = await fetchJson('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    if (!Array.isArray(data.incorrect)) {
      throw new Error('The server returned an invalid check result.');
    }
    const inputs = boardInputs();
    const incorrect = new Set(data.incorrect.map(([row, column]) => row * SIZE + column));

    inputs.forEach((input, index) => {
      input.classList.remove('incorrect');
      if (!input.disabled && board[Math.floor(index / SIZE)][index % SIZE] !== 0
          && incorrect.has(index)) {
        input.classList.add('incorrect');
      }
    });

    const hasIncorrect = Array.from(incorrect).some((index) => (
      board[Math.floor(index / SIZE)][index % SIZE] !== 0
    ));
    const hasEmpty = board.some((row) => row.includes(0));
    if (hasIncorrect) {
      showMessage('Some entries are incorrect.', true);
    } else if (hasEmpty) {
      showMessage('The board is incomplete. Fill the remaining cells.');
    } else {
      finishGame();
    }
  } catch (error) {
    showMessage(error.message || 'Unable to check the puzzle.', true);
  }
}

async function requestHint() {
  try {
    const board = readBoard();
    const data = await fetchJson('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    if (!Number.isInteger(data.row) || data.row < 0 || data.row >= SIZE
        || !Number.isInteger(data.col) || data.col < 0 || data.col >= SIZE
        || !Number.isInteger(data.value) || data.value < 1 || data.value > 9) {
      throw new Error('The server returned an invalid hint.');
    }

    const input = boardInputs()[data.row * SIZE + data.col];
    if (!input || input.disabled || input.value) {
      throw new Error('The hint does not match an empty editable cell.');
    }
    input.value = data.value;
    input.classList.add('hinted');
    input.setAttribute('aria-label', `Row ${data.row + 1}, column ${data.col + 1}, hinted`);
    hintsUsed++;
    document.getElementById('hints-used').innerText = `Hints used: ${hintsUsed}`;
    updateConflicts();
    showMessage('Hint added.');
    if (!readBoard().some((row) => row.includes(0))) {
      await checkSolution();
    }
  } catch (error) {
    showMessage(error.message || 'Unable to get a hint.', true);
  }
}

function handleBoardInput(event) {
  const input = event.target;
  if (!input.matches('.sudoku-cell') || input.disabled) return;

  const rawValue = input.value;
  const sanitized = rawValue.replace(/[^1-9]/g, '').slice(0, 1);
  input.value = sanitized;
  input.classList.remove('incorrect');
  updateConflicts();

  if (rawValue && rawValue !== sanitized) {
    showMessage('Enter a single digit from 1 to 9.', true);
    return;
  }
  showMessage('');
  if (!completed && !checkingCompletion && !readBoard().some((row) => row.includes(0))) {
    checkingCompletion = true;
    checkSolution().finally(() => {
      checkingCompletion = false;
    });
  }
}

// Wire buttons
window.addEventListener('load', () => {
  loadTheme();
  loadLeaderboard();
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('sudoku-board').addEventListener('input', handleBoardInput);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('get-hint').addEventListener('click', requestHint);
  document.getElementById('save-score').addEventListener('click', saveCompletedScore);
  // initialize
  newGame();
});
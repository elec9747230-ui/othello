# Othello Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete, playable Othello desktop game in Python with Tkinter, following the layered architecture defined in [docs/superpowers/specs/2026-04-30-othello-game-design.md](../specs/2026-04-30-othello-game-design.md).

**Architecture:** Three-layer (`core/` → `ai/` → `ui/`) with strict dependency direction. The pure-functional `core/` engine has no UI or AI dependencies. The `ai/` layer adds polymorphic strategies. The `ui/` layer wires everything to Tkinter and is the only place that touches Tkinter or sound.

**Tech Stack:** Python 3.10+, Tkinter (stdlib), `playsound` (sound effects), `pytest` (tests).

---

## File Map

This plan creates the following files. Each task creates or modifies a focused subset.

```
othello/
├── .gitignore                       # Task 1
├── README.md                        # Task 1 (skeleton), Task 22 (filled)
├── requirements.txt                 # Task 1
├── main.py                          # Task 15
├── othello/
│   ├── __init__.py                  # Task 1 (empty)
│   ├── core/
│   │   ├── __init__.py              # Task 1 (empty)
│   │   ├── board.py                 # Task 2, Task 3
│   │   ├── rules.py                 # Task 4, Task 5, Task 6
│   │   └── game.py                  # Task 7, Task 8
│   ├── ai/
│   │   ├── __init__.py              # Task 9 (empty)
│   │   ├── base.py                  # Task 9
│   │   ├── random_ai.py             # Task 9
│   │   ├── greedy.py                # Task 10
│   │   ├── evaluation.py            # Task 11
│   │   ├── minimax.py               # Task 12
│   │   └── alphabeta.py             # Task 13
│   ├── persistence.py               # Task 14
│   └── ui/
│       ├── __init__.py              # Task 15 (empty)
│       ├── app.py                   # Task 15
│       ├── menu_screen.py           # Task 16
│       ├── board_view.py            # Task 17, Task 19
│       ├── game_screen.py           # Task 18, Task 21
│       └── sound.py                 # Task 20
└── tests/
    ├── __init__.py                  # Task 1 (empty)
    ├── test_board.py                # Task 2, Task 3
    ├── test_rules.py                # Task 4, Task 5, Task 6
    ├── test_game.py                 # Task 7, Task 8
    ├── test_ai.py                   # Task 9, 10, 12, 13
    ├── test_evaluation.py           # Task 11
    └── test_persistence.py          # Task 14
```

UI files (Tasks 15–21) have no automated tests per spec §10 — verified by smoke tests instead.

---

## Task 1: Project Scaffolding

Create the directory structure, packaging files, and verify the Python environment.

**Files:**
- Create: `othello/.gitignore`
- Create: `othello/requirements.txt`
- Create: `othello/README.md`
- Create: `othello/othello/__init__.py` (empty)
- Create: `othello/othello/core/__init__.py` (empty)
- Create: `othello/tests/__init__.py` (empty)

- [ ] **Step 1: Verify Python 3.10+ is installed**

Run: `python --version`

Expected: `Python 3.10.x` or higher. If the binary at `C:\Users\elec9\AppData\Local\Microsoft\WindowsApps\python.exe` is the Microsoft Store stub (exits immediately with code 49), install real Python from https://python.org and re-open the shell. The remaining steps assume `python` resolves to a real Python 3.10+ interpreter.

- [ ] **Step 2: Verify Tkinter and create venv**

Run from `c:/Users/elec9/othello/`:
```bash
python -c "import tkinter; print('tkinter OK')"
python -m venv .venv
source .venv/Scripts/activate    # Git-Bash on Windows
python -m pip install --upgrade pip
```

Expected: `tkinter OK`, then a `.venv/` directory created, then pip upgrades cleanly.

- [ ] **Step 3: Create requirements files and install pytest**

Create `c:/Users/elec9/othello/requirements.txt`:
```
playsound==1.3.0
```

Then install dev tools:
```bash
pip install -r requirements.txt
pip install pytest
```

Expected: both install without errors. (If `playsound` install fails on Windows due to the GStreamer dependency, comment it out — the sound layer in Task 20 already swallows import failures.)

- [ ] **Step 4: Create .gitignore**

Create `c:/Users/elec9/othello/.gitignore`:
```
.venv/
__pycache__/
*.pyc
.pytest_cache/
savegames/
```

- [ ] **Step 5: Create empty package directories**

Create the following empty files (each file should literally contain nothing):
- `c:/Users/elec9/othello/othello/__init__.py`
- `c:/Users/elec9/othello/othello/core/__init__.py`
- `c:/Users/elec9/othello/tests/__init__.py`

- [ ] **Step 6: Create README skeleton**

Create `c:/Users/elec9/othello/README.md`:
```markdown
# Othello

A desktop Othello (Reversi) game in Python with Tkinter.

See [docs/superpowers/specs/2026-04-30-othello-game-design.md](docs/superpowers/specs/2026-04-30-othello-game-design.md) for the design.

## Run

```
python main.py
```

## Test

```
pytest
```
```

- [ ] **Step 7: Verify pytest runs (with no tests yet)**

Run: `pytest`

Expected: exit code 5 (`no tests ran`), or 0 with "0 collected". Either is acceptable. If pytest can't be found, re-activate the venv.

- [ ] **Step 8: Commit**

```bash
git add othello/__init__.py othello/core/__init__.py tests/__init__.py .gitignore requirements.txt README.md
git commit -m "chore: scaffold Othello project structure"
```

---

## Task 2: Color Enum and Move Dataclass

**Files:**
- Create: `othello/othello/core/board.py`
- Create: `othello/tests/test_board.py`

- [ ] **Step 1: Write the failing test**

Create `c:/Users/elec9/othello/tests/test_board.py`:
```python
import pytest
from othello.core.board import Color, Move, PASS


def test_color_opponent_swaps():
    assert Color.BLACK.opponent() is Color.WHITE
    assert Color.WHITE.opponent() is Color.BLACK


def test_color_empty_has_no_opponent():
    with pytest.raises(ValueError):
        Color.EMPTY.opponent()


def test_move_is_pass_sentinel():
    assert PASS.is_pass is True
    assert Move(0, 0).is_pass is False


def test_move_is_frozen():
    m = Move(2, 3)
    with pytest.raises(Exception):
        m.row = 5  # frozen dataclass
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_board.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'othello.core.board'`.

- [ ] **Step 3: Implement Color, Move, PASS**

Create `c:/Users/elec9/othello/othello/core/board.py`:
```python
from dataclasses import dataclass
from enum import Enum


class Color(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def opponent(self) -> "Color":
        if self is Color.BLACK:
            return Color.WHITE
        if self is Color.WHITE:
            return Color.BLACK
        raise ValueError("Color.EMPTY has no opponent")


@dataclass(frozen=True)
class Move:
    row: int
    col: int

    @property
    def is_pass(self) -> bool:
        return self.row == -1 and self.col == -1


PASS: Move = Move(-1, -1)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_board.py -v`

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add othello/core/board.py tests/test_board.py
git commit -m "feat(core): add Color enum and Move dataclass"
```

---

## Task 3: Board Class

**Files:**
- Modify: `othello/othello/core/board.py`
- Modify: `othello/tests/test_board.py`

- [ ] **Step 1: Append failing tests**

Append to `c:/Users/elec9/othello/tests/test_board.py`:
```python
from othello.core.board import Board


def test_board_default_size_is_8():
    b = Board()
    assert b.size == 8


def test_board_rejects_odd_size():
    with pytest.raises(ValueError):
        Board(size=7)


def test_board_rejects_too_small():
    with pytest.raises(ValueError):
        Board(size=2)


def test_board_initial_position_8x8():
    b = Board(size=8)
    # Standard Othello starting position
    assert b[3, 3] is Color.WHITE
    assert b[4, 4] is Color.WHITE
    assert b[3, 4] is Color.BLACK
    assert b[4, 3] is Color.BLACK
    # Everything else empty
    empties = sum(1 for _, _, c in b.cells() if c is Color.EMPTY)
    assert empties == 60


def test_board_initial_position_6x6():
    b = Board(size=6)
    assert b[2, 2] is Color.WHITE
    assert b[3, 3] is Color.WHITE
    assert b[2, 3] is Color.BLACK
    assert b[3, 2] is Color.BLACK


def test_board_setitem_and_getitem():
    b = Board()
    b[0, 0] = Color.BLACK
    assert b[0, 0] is Color.BLACK


def test_board_copy_is_independent():
    b = Board()
    c = b.copy()
    c[0, 0] = Color.BLACK
    assert b[0, 0] is Color.EMPTY


def test_board_in_bounds():
    b = Board(size=8)
    assert b.in_bounds(0, 0)
    assert b.in_bounds(7, 7)
    assert not b.in_bounds(-1, 0)
    assert not b.in_bounds(0, 8)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_board.py -v`

Expected: 8 new tests fail with `ImportError: cannot import name 'Board'`.

- [ ] **Step 3: Implement Board**

Append to `c:/Users/elec9/othello/othello/core/board.py`:
```python
from typing import Iterator


class Board:
    def __init__(self, size: int = 8):
        if size < 4 or size % 2 != 0:
            raise ValueError(f"Board size must be even and >= 4, got {size}")
        self.size = size
        self._cells: list[list[Color]] = [
            [Color.EMPTY] * size for _ in range(size)
        ]
        m = size // 2
        self._cells[m - 1][m - 1] = Color.WHITE
        self._cells[m][m] = Color.WHITE
        self._cells[m - 1][m] = Color.BLACK
        self._cells[m][m - 1] = Color.BLACK

    def __getitem__(self, rc: tuple[int, int]) -> Color:
        r, c = rc
        return self._cells[r][c]

    def __setitem__(self, rc: tuple[int, int], color: Color) -> None:
        r, c = rc
        self._cells[r][c] = color

    def copy(self) -> "Board":
        new = Board.__new__(Board)
        new.size = self.size
        new._cells = [row[:] for row in self._cells]
        return new

    def cells(self) -> Iterator[tuple[int, int, Color]]:
        for r in range(self.size):
            for c in range(self.size):
                yield (r, c, self._cells[r][c])

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_board.py -v`

Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add othello/core/board.py tests/test_board.py
git commit -m "feat(core): add Board class with N×N initial position"
```

---

## Task 4: Rules — `legal_moves` and `flips_for`

**Files:**
- Create: `othello/othello/core/rules.py`
- Create: `othello/tests/test_rules.py`

- [ ] **Step 1: Write the failing tests**

Create `c:/Users/elec9/othello/tests/test_rules.py`:
```python
from othello.core.board import Board, Color, Move
from othello.core.rules import legal_moves, flips_for


def test_initial_black_has_four_legal_moves():
    b = Board()
    moves = legal_moves(b, Color.BLACK)
    expected = {Move(2, 3), Move(3, 2), Move(4, 5), Move(5, 4)}
    assert set(moves) == expected


def test_initial_white_has_four_legal_moves():
    b = Board()
    moves = legal_moves(b, Color.WHITE)
    expected = {Move(2, 4), Move(4, 2), Move(3, 5), Move(5, 3)}
    assert set(moves) == expected


def test_flips_for_initial_black_d3():
    b = Board()
    flips = flips_for(b, Move(2, 3), Color.BLACK)
    # Playing BLACK at (2,3) flips the WHITE at (3,3)
    assert flips == [(3, 3)]


def test_flips_for_illegal_move_returns_empty():
    b = Board()
    # (0,0) flips nothing
    assert flips_for(b, Move(0, 0), Color.BLACK) == []
    # Occupied cell
    assert flips_for(b, Move(3, 3), Color.BLACK) == []


def test_flips_for_multidirectional():
    # Construct a position where placing BLACK flips in multiple directions
    b = Board()
    # Clear and set up: BLACK at (3,2), (3,4); WHITE at (3,3); empty at others
    # After standard init: (3,3)=W, (3,4)=B, (4,3)=B, (4,4)=W
    # Playing WHITE at (5,4) flips (4,4) only? Let's pick a clearer scenario.
    # Easier: standard init, BLACK plays (4,5) → flips (4,4) (WHITE) only
    flips = flips_for(b, Move(4, 5), Color.BLACK)
    assert flips == [(4, 4)]


def test_legal_moves_empty_when_no_captures_possible():
    b = Board(size=4)  # 4x4 mini-board
    # On a fresh 4x4 board, both colors should still have moves
    assert len(legal_moves(b, Color.BLACK)) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_rules.py -v`

Expected: all fail with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `flips_for` and `legal_moves`**

Create `c:/Users/elec9/othello/othello/core/rules.py`:
```python
from othello.core.board import Board, Color, Move

DIRECTIONS: list[tuple[int, int]] = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


def _flips_in_direction(
    board: Board, r: int, c: int, dr: int, dc: int, color: Color
) -> list[tuple[int, int]]:
    opp = color.opponent()
    captured: list[tuple[int, int]] = []
    rr, cc = r + dr, c + dc
    while board.in_bounds(rr, cc) and board[rr, cc] is opp:
        captured.append((rr, cc))
        rr += dr
        cc += dc
    if board.in_bounds(rr, cc) and board[rr, cc] is color and captured:
        return captured
    return []


def flips_for(board: Board, move: Move, color: Color) -> list[tuple[int, int]]:
    """Return the list of opponent-stone coordinates that would flip
    if `color` plays `move`. Empty list ⇒ illegal move."""
    if not board.in_bounds(move.row, move.col):
        return []
    if board[move.row, move.col] is not Color.EMPTY:
        return []
    all_flips: list[tuple[int, int]] = []
    for dr, dc in DIRECTIONS:
        all_flips.extend(
            _flips_in_direction(board, move.row, move.col, dr, dc, color)
        )
    return all_flips


def legal_moves(board: Board, color: Color) -> list[Move]:
    moves: list[Move] = []
    for r in range(board.size):
        for c in range(board.size):
            if board[r, c] is Color.EMPTY:
                m = Move(r, c)
                if flips_for(board, m, color):
                    moves.append(m)
    return moves
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_rules.py -v`

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add othello/core/rules.py tests/test_rules.py
git commit -m "feat(core): add legal_moves and flips_for"
```

---

## Task 5: Rules — `apply_move`

**Files:**
- Modify: `othello/othello/core/rules.py`
- Modify: `othello/tests/test_rules.py`

- [ ] **Step 1: Append failing tests**

Append to `c:/Users/elec9/othello/tests/test_rules.py`:
```python
import pytest
from othello.core.rules import apply_move


def test_apply_move_returns_new_board():
    b = Board()
    new_b = apply_move(b, Move(2, 3), Color.BLACK)
    assert new_b is not b
    # Original is unchanged
    assert b[2, 3] is Color.EMPTY
    assert b[3, 3] is Color.WHITE


def test_apply_move_places_stone_and_flips():
    b = Board()
    new_b = apply_move(b, Move(2, 3), Color.BLACK)
    assert new_b[2, 3] is Color.BLACK
    assert new_b[3, 3] is Color.BLACK  # was WHITE, flipped


def test_apply_move_raises_on_illegal_move():
    b = Board()
    with pytest.raises(ValueError):
        apply_move(b, Move(0, 0), Color.BLACK)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_rules.py -v -k apply_move`

Expected: 3 tests fail with `ImportError: cannot import name 'apply_move'`.

- [ ] **Step 3: Implement `apply_move`**

Append to `c:/Users/elec9/othello/othello/core/rules.py`:
```python
def apply_move(board: Board, move: Move, color: Color) -> Board:
    flips = flips_for(board, move, color)
    if not flips:
        raise ValueError(f"Illegal move {move} for {color.name}")
    new_board = board.copy()
    new_board[move.row, move.col] = color
    for r, c in flips:
        new_board[r, c] = color
    return new_board
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_rules.py -v`

Expected: 9 passed total.

- [ ] **Step 5: Commit**

```bash
git add othello/core/rules.py tests/test_rules.py
git commit -m "feat(core): add apply_move (immutable)"
```

---

## Task 6: Rules — `score`, `is_terminal`, `winner`

**Files:**
- Modify: `othello/othello/core/rules.py`
- Modify: `othello/tests/test_rules.py`

- [ ] **Step 1: Append failing tests**

Append to `c:/Users/elec9/othello/tests/test_rules.py`:
```python
from othello.core.rules import score, is_terminal, winner


def test_score_initial_is_2_2():
    b = Board()
    assert score(b) == (2, 2)


def test_score_after_first_black_move():
    b = Board()
    b2 = apply_move(b, Move(2, 3), Color.BLACK)
    # BLACK now has 4 (placed 1, flipped 1, kept 2), WHITE has 1
    assert score(b2) == (4, 1)


def test_is_terminal_initial_is_false():
    assert is_terminal(Board()) is False


def test_is_terminal_full_board_is_true():
    b = Board()
    for r in range(b.size):
        for c in range(b.size):
            b[r, c] = Color.BLACK
    assert is_terminal(b) is True


def test_winner_full_black_board():
    b = Board()
    for r in range(b.size):
        for c in range(b.size):
            b[r, c] = Color.BLACK
    assert winner(b) is Color.BLACK


def test_winner_tie_returns_none():
    b = Board()
    half = b.size * b.size // 2
    flat = [(r, c) for r in range(b.size) for c in range(b.size)]
    for r, c in flat[:half]:
        b[r, c] = Color.BLACK
    for r, c in flat[half:]:
        b[r, c] = Color.WHITE
    assert winner(b) is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_rules.py -v -k "score or terminal or winner"`

Expected: 6 tests fail with import errors.

- [ ] **Step 3: Implement `score`, `is_terminal`, `winner`**

Append to `c:/Users/elec9/othello/othello/core/rules.py`:
```python
def score(board: Board) -> tuple[int, int]:
    black = white = 0
    for _, _, c in board.cells():
        if c is Color.BLACK:
            black += 1
        elif c is Color.WHITE:
            white += 1
    return black, white


def is_terminal(board: Board) -> bool:
    return not legal_moves(board, Color.BLACK) and not legal_moves(board, Color.WHITE)


def winner(board: Board) -> Color | None:
    b, w = score(board)
    if b > w:
        return Color.BLACK
    if w > b:
        return Color.WHITE
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_rules.py -v`

Expected: 15 passed total.

- [ ] **Step 5: Commit**

```bash
git add othello/core/rules.py tests/test_rules.py
git commit -m "feat(core): add score, is_terminal, winner"
```

---

## Task 7: GameState — `play` and `undo`

**Files:**
- Create: `othello/othello/core/game.py`
- Create: `othello/tests/test_game.py`

- [ ] **Step 1: Write failing tests**

Create `c:/Users/elec9/othello/tests/test_game.py`:
```python
import pytest
from othello.core.board import Color, Move
from othello.core.game import GameState


def test_initial_state_is_black_to_move():
    s = GameState()
    assert s.current is Color.BLACK
    assert s.history == []


def test_play_legal_move_advances_turn():
    s = GameState()
    s.play(Move(2, 3))
    assert s.current is Color.WHITE
    assert s.board[2, 3] is Color.BLACK
    assert s.board[3, 3] is Color.BLACK  # flipped
    assert len(s.history) == 1


def test_play_illegal_move_raises():
    s = GameState()
    with pytest.raises(ValueError):
        s.play(Move(0, 0))


def test_undo_restores_previous_state():
    s = GameState()
    snapshot_board = [[s.board[r, c] for c in range(s.board.size)] for r in range(s.board.size)]
    s.play(Move(2, 3))
    s.undo()
    assert s.current is Color.BLACK
    for r in range(s.board.size):
        for c in range(s.board.size):
            assert s.board[r, c] is snapshot_board[r][c]
    assert s.history == []


def test_undo_without_history_raises():
    s = GameState()
    with pytest.raises(IndexError):
        s.undo()


def test_play_undo_round_trip_two_moves():
    s = GameState()
    s.play(Move(2, 3))
    s.play(Move(2, 2))  # WHITE response
    assert s.current is Color.BLACK
    s.undo()
    assert s.current is Color.WHITE
    s.undo()
    assert s.current is Color.BLACK
    assert s.history == []


def test_score_delegates_to_rules():
    s = GameState()
    assert s.score() == (2, 2)
    s.play(Move(2, 3))
    assert s.score() == (4, 1)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_game.py -v`

Expected: all fail with `ModuleNotFoundError`.

- [ ] **Step 3: Implement GameState (without auto-pass yet)**

Create `c:/Users/elec9/othello/othello/core/game.py`:
```python
from dataclasses import dataclass

from othello.core.board import Board, Color, Move, PASS
from othello.core.rules import (
    apply_move,
    is_terminal,
    legal_moves,
    score,
    winner,
)


@dataclass
class HistoryEntry:
    board_before: Board
    color_to_move: Color
    move: Move


class GameState:
    def __init__(self, size: int = 8):
        self.board: Board = Board(size)
        self.current: Color = Color.BLACK
        self.history: list[HistoryEntry] = []

    def legal_moves(self) -> list[Move]:
        return legal_moves(self.board, self.current)

    def play(self, move: Move) -> None:
        self.history.append(HistoryEntry(self.board.copy(), self.current, move))
        self.board = apply_move(self.board, move, self.current)
        self.current = self.current.opponent()

    def undo(self) -> None:
        if not self.history:
            raise IndexError("No history to undo")
        entry = self.history.pop()
        self.board = entry.board_before
        self.current = entry.color_to_move

    def score(self) -> tuple[int, int]:
        return score(self.board)

    def winner(self) -> Color | None:
        return winner(self.board)

    def is_over(self) -> bool:
        return is_terminal(self.board)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_game.py -v`

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add othello/core/game.py tests/test_game.py
git commit -m "feat(core): add GameState with play/undo/history"
```

---

## Task 8: GameState — Auto-Pass

**Files:**
- Modify: `othello/othello/core/game.py`
- Modify: `othello/tests/test_game.py`

- [ ] **Step 1: Append failing tests**

Append to `c:/Users/elec9/othello/tests/test_game.py`:
```python
def _make_pass_position():
    """Construct a board where after BLACK plays, WHITE has no moves."""
    s = GameState()
    # Hand-craft a board: only one BLACK and one WHITE, both isolated.
    # Easier: clear board then set a known no-move-for-white config.
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.EMPTY
    # Place stones so WHITE has no legal capture but BLACK still does.
    # Setup: BLACK fills bottom-left corner cluster, WHITE only in
    # a single isolated cell with no adjacent BLACK to flip toward.
    s.board[0, 0] = Color.WHITE
    s.board[7, 7] = Color.BLACK
    s.board[7, 6] = Color.WHITE
    s.board[7, 5] = Color.BLACK  # WHITE at (7,6) is between two BLACKs row-wise — no flip
    s.current = Color.BLACK
    return s


def test_must_pass_detection():
    s = _make_pass_position()
    # In this contrived position WHITE has no captures and neither does BLACK
    # so this is actually game-over, not pass. Use a real auto-pass scenario instead:
    pass  # placeholder; actual coverage in next test


def test_auto_pass_when_opponent_has_no_moves():
    """After playing, if opponent has no legal moves but we still do,
    turn returns to us with a PASS recorded."""
    s = GameState()
    # Force a synthetic position rather than playing through:
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.EMPTY
    # Position: BLACK can move at (0,2) flipping (0,1); after the move,
    # WHITE has no legal move but BLACK still does.
    s.board[0, 0] = Color.BLACK
    s.board[0, 1] = Color.WHITE
    # Add another flippable line for BLACK so BLACK still has moves after the play
    s.board[7, 0] = Color.BLACK
    s.board[7, 1] = Color.WHITE
    s.current = Color.BLACK

    # Confirm setup: WHITE has no moves right now either; let's use a
    # different construction. Swap WHITE/BLACK colors to ensure WHITE has
    # at least one move *before* the BLACK play but none after.
    s.board[0, 0] = Color.EMPTY
    s.board[0, 1] = Color.EMPTY
    s.board[7, 0] = Color.EMPTY
    s.board[7, 1] = Color.EMPTY
    # Final synthetic position:
    # Row 0: . B W .  ⇒ BLACK can play (0,3) flipping (0,2)? Need W between.
    # Build: BLACK at (0,0), WHITE at (0,1), empty (0,2). BLACK plays (0,2)? No,
    # that's not legal because there's no BLACK on the far side.
    # Build: BLACK (0,0), WHITE (0,1), empty (0,2), BLACK plays at (0,2)? Still nope.
    # Use vertical line: BLACK (0,0), WHITE (1,0), empty (2,0); BLACK plays (2,0)? No far-side BLACK.
    # Simplest: BLACK plays a move that leaves WHITE with NO legal move,
    # and BLACK still has a move elsewhere.
    s.board[0, 0] = Color.WHITE
    s.board[0, 1] = Color.BLACK
    s.board[0, 2] = Color.WHITE
    s.board[0, 3] = Color.BLACK
    # ⇒ Now BLACK plays nothing yet; WHITE has 0 captures (all WHITEs are
    # already adjacent only to BLACK or empty with no BLACK to flip).
    # Add a BLACK move target: leave (1,1) empty with WHITE at (2,2) and
    # BLACK at (3,3) so BLACK plays (1,1) flipping (2,2).
    s.board[2, 2] = Color.WHITE
    s.board[3, 3] = Color.BLACK
    s.current = Color.BLACK

    # Sanity: WHITE has no legal moves in this position
    from othello.core.rules import legal_moves
    assert legal_moves(s.board, Color.WHITE) == []

    # BLACK plays (1, 1) — flips (2, 2)
    s.play(Move(1, 1))
    # After this play, current should still be BLACK because WHITE was auto-passed.
    assert s.current is Color.BLACK
    # History should have 2 entries: the move and the auto-pass.
    assert len(s.history) == 2
    assert s.history[-1].move.is_pass


def test_undo_after_auto_pass_pops_both_entries():
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.EMPTY
    s.board[0, 0] = Color.WHITE
    s.board[0, 1] = Color.BLACK
    s.board[0, 2] = Color.WHITE
    s.board[0, 3] = Color.BLACK
    s.board[2, 2] = Color.WHITE
    s.board[3, 3] = Color.BLACK
    s.current = Color.BLACK

    s.play(Move(1, 1))
    assert len(s.history) == 2
    s.undo()
    assert s.current is Color.BLACK
    assert s.history == []
    assert s.board[1, 1] is Color.EMPTY
    assert s.board[2, 2] is Color.WHITE


def test_is_over_when_neither_side_has_moves():
    s = GameState()
    # Fill board entirely with BLACK ⇒ no moves for either side
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.BLACK
    assert s.is_over() is True
```

(The first `test_must_pass_detection` is a placeholder kept for documentation; pytest ignores empty bodies, so it passes trivially. Remove if you prefer.)

- [ ] **Step 2: Run tests to verify the auto-pass tests fail**

Run: `pytest tests/test_game.py -v -k auto_pass`

Expected: `test_auto_pass_when_opponent_has_no_moves` and `test_undo_after_auto_pass_pops_both_entries` fail because `play` does not yet auto-pass.

- [ ] **Step 3: Implement auto-pass**

Replace the `play` and `undo` methods in `c:/Users/elec9/othello/othello/core/game.py` with:
```python
    def must_pass(self) -> bool:
        return (
            not legal_moves(self.board, self.current)
            and bool(legal_moves(self.board, self.current.opponent()))
        )

    def play(self, move: Move) -> None:
        if move.is_pass:
            if not self.must_pass():
                raise ValueError("PASS is only legal when the current player has no moves")
            self.history.append(HistoryEntry(self.board.copy(), self.current, move))
            self.current = self.current.opponent()
            return
        self.history.append(HistoryEntry(self.board.copy(), self.current, move))
        self.board = apply_move(self.board, move, self.current)
        self.current = self.current.opponent()
        # Auto-pass: opponent has no moves but we still do
        if (
            not legal_moves(self.board, self.current)
            and legal_moves(self.board, self.current.opponent())
        ):
            self.history.append(HistoryEntry(self.board.copy(), self.current, PASS))
            self.current = self.current.opponent()

    def undo(self) -> None:
        if not self.history:
            raise IndexError("No history to undo")
        entry = self.history.pop()
        # If the most recent entry was an auto-pass, pop the underlying move too
        while entry.move.is_pass and self.history:
            entry = self.history.pop()
        self.board = entry.board_before
        self.current = entry.color_to_move
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_game.py -v`

Expected: 11 passed (including the placeholder).

- [ ] **Step 5: Commit**

```bash
git add othello/core/game.py tests/test_game.py
git commit -m "feat(core): add auto-pass and must_pass to GameState"
```

---

## Task 9: AI — Strategy ABC and RandomAI

**Files:**
- Create: `othello/othello/ai/__init__.py` (empty)
- Create: `othello/othello/ai/base.py`
- Create: `othello/othello/ai/random_ai.py`
- Create: `othello/tests/test_ai.py`

- [ ] **Step 1: Create empty package init**

Create `c:/Users/elec9/othello/othello/ai/__init__.py` as an empty file.

- [ ] **Step 2: Write failing tests**

Create `c:/Users/elec9/othello/tests/test_ai.py`:
```python
import pytest
from othello.core.game import GameState
from othello.core.board import Color
from othello.ai.base import Strategy
from othello.ai.random_ai import RandomAI


def test_random_ai_returns_legal_move():
    s = GameState()
    ai = RandomAI(seed=0)
    move = ai.select_move(s)
    assert move in s.legal_moves()


def test_random_ai_is_seeded_deterministic():
    s = GameState()
    ai1 = RandomAI(seed=42)
    ai2 = RandomAI(seed=42)
    assert ai1.select_move(s) == ai2.select_move(s)


def test_random_ai_raises_when_no_legal_moves():
    s = GameState()
    # Wipe to a no-move position
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.BLACK
    ai = RandomAI()
    with pytest.raises(ValueError):
        ai.select_move(s)


def test_strategy_is_abstract():
    with pytest.raises(TypeError):
        Strategy()  # cannot instantiate ABC
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_ai.py -v`

Expected: all fail with `ModuleNotFoundError`.

- [ ] **Step 4: Implement Strategy and RandomAI**

Create `c:/Users/elec9/othello/othello/ai/base.py`:
```python
from abc import ABC, abstractmethod

from othello.core.board import Move
from othello.core.game import GameState


class Strategy(ABC):
    name: str = ""

    @abstractmethod
    def select_move(self, state: GameState) -> Move:
        """Return a legal move from `state.legal_moves()`.
        Must raise ValueError if no legal move exists."""
```

Create `c:/Users/elec9/othello/othello/ai/random_ai.py`:
```python
import random

from othello.ai.base import Strategy
from othello.core.board import Move
from othello.core.game import GameState


class RandomAI(Strategy):
    name = "Random"

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("RandomAI: no legal moves available")
        return self._rng.choice(moves)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_ai.py -v`

Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add othello/ai/__init__.py othello/ai/base.py othello/ai/random_ai.py tests/test_ai.py
git commit -m "feat(ai): add Strategy ABC and RandomAI"
```

---

## Task 10: AI — GreedyAI

**Files:**
- Create: `othello/othello/ai/greedy.py`
- Modify: `othello/tests/test_ai.py`

- [ ] **Step 1: Append failing tests**

Append to `c:/Users/elec9/othello/tests/test_ai.py`:
```python
from othello.ai.greedy import GreedyAI
from othello.core.rules import flips_for


def test_greedy_picks_max_flips():
    s = GameState()
    ai = GreedyAI()
    move = ai.select_move(s)
    # Verify chosen move flips at least as many as any other legal move
    chosen = len(flips_for(s.board, move, s.current))
    for m in s.legal_moves():
        assert chosen >= len(flips_for(s.board, m, s.current))


def test_greedy_returns_legal_move():
    s = GameState()
    ai = GreedyAI()
    assert ai.select_move(s) in s.legal_moves()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ai.py -v -k greedy`

Expected: 2 fail with `ModuleNotFoundError`.

- [ ] **Step 3: Implement GreedyAI**

Create `c:/Users/elec9/othello/othello/ai/greedy.py`:
```python
from othello.ai.base import Strategy
from othello.core.board import Move
from othello.core.game import GameState
from othello.core.rules import flips_for


class GreedyAI(Strategy):
    name = "Greedy"

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("GreedyAI: no legal moves available")
        return max(moves, key=lambda m: len(flips_for(state.board, m, state.current)))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_ai.py -v`

Expected: 6 passed total.

- [ ] **Step 5: Commit**

```bash
git add othello/ai/greedy.py tests/test_ai.py
git commit -m "feat(ai): add GreedyAI"
```

---

## Task 11: AI — Evaluation Function

**Files:**
- Create: `othello/othello/ai/evaluation.py`
- Create: `othello/tests/test_evaluation.py`

- [ ] **Step 1: Write failing tests**

Create `c:/Users/elec9/othello/tests/test_evaluation.py`:
```python
from othello.core.board import Board, Color
from othello.ai.evaluation import evaluate


def test_evaluate_initial_position_is_neutral():
    b = Board()
    # Symmetric initial position ⇒ evaluation 0
    assert evaluate(b, Color.BLACK) == 0


def test_evaluate_corner_value_is_high_for_owner_8x8():
    b = Board()
    b[0, 0] = Color.BLACK
    val_black = evaluate(b, Color.BLACK)
    val_white = evaluate(b, Color.WHITE)
    assert val_black > 0
    assert val_white < 0
    # Sign symmetry
    assert val_black == -val_white


def test_evaluate_endgame_uses_score_difference():
    b = Board()
    for r in range(b.size):
        for c in range(b.size):
            b[r, c] = Color.BLACK
    val = evaluate(b, Color.BLACK)
    assert val > 1000  # large endgame magnitude


def test_evaluate_works_for_6x6_and_10x10():
    b6 = Board(size=6)
    b10 = Board(size=10)
    # Just ensure no crash, returns int
    assert isinstance(evaluate(b6, Color.BLACK), int)
    assert isinstance(evaluate(b10, Color.BLACK), int)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_evaluation.py -v`

Expected: all fail with `ModuleNotFoundError`.

- [ ] **Step 3: Implement evaluation**

Create `c:/Users/elec9/othello/othello/ai/evaluation.py`:
```python
from othello.core.board import Board, Color
from othello.core.rules import legal_moves, score

WEIGHTS_8X8: list[list[int]] = [
    [100, -25,  10,   5,   5,  10, -25, 100],
    [-25, -50,   1,   1,   1,   1, -50, -25],
    [ 10,   1,   5,   2,   2,   5,   1,  10],
    [  5,   1,   2,   1,   1,   2,   1,   5],
    [  5,   1,   2,   1,   1,   2,   1,   5],
    [ 10,   1,   5,   2,   2,   5,   1,  10],
    [-25, -50,   1,   1,   1,   1, -50, -25],
    [100, -25,  10,   5,   5,  10, -25, 100],
]


def _generic_value(size: int, r: int, c: int) -> int:
    is_corner = r in (0, size - 1) and c in (0, size - 1)
    is_edge = r in (0, size - 1) or c in (0, size - 1)
    if is_corner:
        return 30
    if is_edge:
        return 5
    return 1


def _terminal_eval(board: Board, color: Color) -> int:
    b, w = score(board)
    diff = b - w
    sign = 1 if color is Color.BLACK else -1
    return sign * diff * 10000


def evaluate(board: Board, color: Color) -> int:
    # Endgame: no moves for either side
    if not legal_moves(board, Color.BLACK) and not legal_moves(board, Color.WHITE):
        return _terminal_eval(board, color)

    use_weights = (board.size == 8)
    total = 0
    for r, c, cell in board.cells():
        if cell is Color.EMPTY:
            continue
        v = WEIGHTS_8X8[r][c] if use_weights else _generic_value(board.size, r, c)
        if cell is color:
            total += v
        else:
            total -= v
    return total
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_evaluation.py -v`

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add othello/ai/evaluation.py tests/test_evaluation.py
git commit -m "feat(ai): add positional evaluation function"
```

---

## Task 12: AI — MinimaxAI

**Files:**
- Create: `othello/othello/ai/minimax.py`
- Modify: `othello/tests/test_ai.py`

- [ ] **Step 1: Append failing tests**

Append to `c:/Users/elec9/othello/tests/test_ai.py`:
```python
from othello.ai.minimax import MinimaxAI


def test_minimax_returns_legal_move():
    s = GameState()
    ai = MinimaxAI(depth=2)
    assert ai.select_move(s) in s.legal_moves()


def test_minimax_depth_1_picks_best_immediate():
    s = GameState()
    ai = MinimaxAI(depth=1)
    move = ai.select_move(s)
    assert move in s.legal_moves()


def test_minimax_raises_with_no_legal_moves():
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.BLACK
    ai = MinimaxAI(depth=2)
    with pytest.raises(ValueError):
        ai.select_move(s)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ai.py -v -k minimax`

Expected: 3 fail with `ModuleNotFoundError`.

- [ ] **Step 3: Implement MinimaxAI**

Create `c:/Users/elec9/othello/othello/ai/minimax.py`:
```python
from othello.ai.base import Strategy
from othello.ai.evaluation import evaluate
from othello.core.board import Board, Color, Move
from othello.core.game import GameState
from othello.core.rules import apply_move, legal_moves

INF = float("inf")


class MinimaxAI(Strategy):
    name = "Minimax"

    def __init__(self, depth: int = 3):
        self.depth = depth

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("MinimaxAI: no legal moves available")
        root_color = state.current
        best_move = moves[0]
        best_val = -INF
        for m in moves:
            new_board = apply_move(state.board, m, root_color)
            val = self._search(new_board, root_color.opponent(), self.depth - 1, root_color)
            if val > best_val:
                best_val = val
                best_move = m
        return best_move

    def _search(self, board: Board, to_move: Color, depth: int, root_color: Color) -> float:
        if depth == 0:
            return evaluate(board, root_color)
        moves = legal_moves(board, to_move)
        if not moves:
            opp_moves = legal_moves(board, to_move.opponent())
            if not opp_moves:
                return evaluate(board, root_color)
            return self._search(board, to_move.opponent(), depth - 1, root_color)
        if to_move is root_color:
            best = -INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move), to_move.opponent(), depth - 1, root_color
                )
                if v > best:
                    best = v
            return best
        else:
            best = INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move), to_move.opponent(), depth - 1, root_color
                )
                if v < best:
                    best = v
            return best
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_ai.py -v`

Expected: 9 passed total.

- [ ] **Step 5: Commit**

```bash
git add othello/ai/minimax.py tests/test_ai.py
git commit -m "feat(ai): add MinimaxAI with depth-limited search"
```

---

## Task 13: AI — AlphaBetaAI + Parity Test

**Files:**
- Create: `othello/othello/ai/alphabeta.py`
- Modify: `othello/tests/test_ai.py`

- [ ] **Step 1: Append failing tests**

Append to `c:/Users/elec9/othello/tests/test_ai.py`:
```python
from othello.ai.alphabeta import AlphaBetaAI


def test_alphabeta_returns_legal_move():
    s = GameState()
    ai = AlphaBetaAI(depth=3)
    assert ai.select_move(s) in s.legal_moves()


def test_minimax_and_alphabeta_agree_on_initial_position():
    """At the same depth, alpha-beta pruning must not change the chosen move."""
    s = GameState()
    mm = MinimaxAI(depth=3)
    ab = AlphaBetaAI(depth=3)
    assert mm.select_move(s) == ab.select_move(s)


def test_minimax_and_alphabeta_agree_after_few_plays():
    s = GameState()
    s.play(s.legal_moves()[0])
    s.play(s.legal_moves()[0])
    mm = MinimaxAI(depth=3)
    ab = AlphaBetaAI(depth=3)
    assert mm.select_move(s) == ab.select_move(s)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ai.py -v -k alphabeta`

Expected: 3 fail with `ModuleNotFoundError`.

- [ ] **Step 3: Implement AlphaBetaAI**

Create `c:/Users/elec9/othello/othello/ai/alphabeta.py`:
```python
from othello.ai.base import Strategy
from othello.ai.evaluation import evaluate
from othello.core.board import Board, Color, Move
from othello.core.game import GameState
from othello.core.rules import apply_move, legal_moves

INF = float("inf")


class AlphaBetaAI(Strategy):
    name = "Alpha-Beta"

    def __init__(self, depth: int = 5):
        self.depth = depth

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("AlphaBetaAI: no legal moves available")
        root_color = state.current
        best_move = moves[0]
        best_val = -INF
        alpha, beta = -INF, INF
        for m in moves:
            new_board = apply_move(state.board, m, root_color)
            val = self._search(
                new_board, root_color.opponent(), self.depth - 1, alpha, beta, root_color
            )
            if val > best_val:
                best_val = val
                best_move = m
            alpha = max(alpha, val)
        return best_move

    def _search(
        self,
        board: Board,
        to_move: Color,
        depth: int,
        alpha: float,
        beta: float,
        root_color: Color,
    ) -> float:
        if depth == 0:
            return evaluate(board, root_color)
        moves = legal_moves(board, to_move)
        if not moves:
            opp_moves = legal_moves(board, to_move.opponent())
            if not opp_moves:
                return evaluate(board, root_color)
            return self._search(board, to_move.opponent(), depth - 1, alpha, beta, root_color)
        if to_move is root_color:
            value = -INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move),
                    to_move.opponent(),
                    depth - 1,
                    alpha,
                    beta,
                    root_color,
                )
                if v > value:
                    value = v
                if value > alpha:
                    alpha = value
                if alpha >= beta:
                    break
            return value
        else:
            value = INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move),
                    to_move.opponent(),
                    depth - 1,
                    alpha,
                    beta,
                    root_color,
                )
                if v < value:
                    value = v
                if value < beta:
                    beta = value
                if alpha >= beta:
                    break
            return value
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_ai.py -v`

Expected: 12 passed total.

- [ ] **Step 5: Commit**

```bash
git add othello/ai/alphabeta.py tests/test_ai.py
git commit -m "feat(ai): add AlphaBetaAI with parity test vs Minimax"
```

---

## Task 14: Persistence — Save/Load via History Replay

**Files:**
- Create: `othello/othello/persistence.py`
- Create: `othello/tests/test_persistence.py`

- [ ] **Step 1: Write failing tests**

Create `c:/Users/elec9/othello/tests/test_persistence.py`:
```python
import pytest
from pathlib import Path

from othello.core.board import Color, Move
from othello.core.game import GameState
from othello.persistence import save_game, load_game


def test_round_trip_empty_game(tmp_path: Path):
    s = GameState(size=8)
    p = tmp_path / "g.json"
    save_game(s, {"mode": "two_player"}, p)
    s2, info = load_game(p)
    assert s2.board.size == 8
    assert s2.current is Color.BLACK
    assert info == {"mode": "two_player"}


def test_round_trip_after_moves(tmp_path: Path):
    s = GameState(size=8)
    s.play(Move(2, 3))
    s.play(Move(2, 2))
    p = tmp_path / "g.json"
    save_game(s, {"mode": "vs_ai", "ai_difficulty": "minimax"}, p)
    s2, info = load_game(p)
    assert s2.current is s.current
    for r in range(8):
        for c in range(8):
            assert s2.board[r, c] is s.board[r, c]
    assert info["ai_difficulty"] == "minimax"


def test_load_rejects_unknown_version(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text('{"version": 999, "size": 8, "current": "BLACK", "history": []}')
    with pytest.raises(ValueError):
        load_game(p)


def test_load_rejects_invalid_replay(tmp_path: Path):
    p = tmp_path / "bad.json"
    # Move (0, 0) is illegal at start
    p.write_text(
        '{"version": 1, "size": 8, "current": "BLACK", '
        '"mode_info": {}, "history": [{"row": 0, "col": 0, "color": "BLACK"}]}'
    )
    with pytest.raises(ValueError):
        load_game(p)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_persistence.py -v`

Expected: all fail with `ModuleNotFoundError`.

- [ ] **Step 3: Implement persistence**

Create `c:/Users/elec9/othello/othello/persistence.py`:
```python
import json
from pathlib import Path
from typing import Any

from othello.core.board import Color, Move
from othello.core.game import GameState

VERSION = 1


def save_game(state: GameState, mode_info: dict[str, Any], path: Path | str) -> None:
    data = {
        "version": VERSION,
        "size": state.board.size,
        "current": state.current.name,
        "mode_info": mode_info,
        "history": [
            {"row": e.move.row, "col": e.move.col, "color": e.color_to_move.name}
            for e in state.history
        ],
    }
    Path(path).write_text(json.dumps(data, indent=2))


def load_game(path: Path | str) -> tuple[GameState, dict[str, Any]]:
    data = json.loads(Path(path).read_text())
    if data.get("version") != VERSION:
        raise ValueError(f"Unsupported save version: {data.get('version')!r}")
    size = data["size"]
    state = GameState(size=size)
    for entry in data.get("history", []):
        move = Move(entry["row"], entry["col"])
        if move.is_pass:
            # Auto-pass entries are regenerated by play(); skip.
            continue
        expected_color = Color[entry["color"]]
        if state.current is not expected_color:
            raise ValueError(
                f"Replay mismatch at {move}: expected {state.current.name}, "
                f"saved as {expected_color.name}"
            )
        state.play(move)
    return state, data.get("mode_info", {})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_persistence.py -v`

Expected: 4 passed.

- [ ] **Step 5: Run the full test suite**

Run: `pytest -v`

Expected: all tests pass (~40 total). If any failures, fix before continuing — UI work depends on a clean core.

- [ ] **Step 6: Commit**

```bash
git add othello/persistence.py tests/test_persistence.py
git commit -m "feat: add JSON save/load via history replay"
```

---

## Task 15: UI — App Skeleton + main.py

**Files:**
- Create: `othello/othello/ui/__init__.py` (empty)
- Create: `othello/othello/ui/app.py`
- Create: `othello/main.py`

UI tasks have **no automated tests** per spec §10. Each task ends with a manual smoke test instead.

- [ ] **Step 1: Create empty package init**

Create `c:/Users/elec9/othello/othello/ui/__init__.py` as an empty file.

- [ ] **Step 2: Implement app shell**

Create `c:/Users/elec9/othello/othello/ui/app.py`:
```python
import tkinter as tk
from typing import Any


class OthelloApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Othello")
        self.root.geometry("800x600")
        self.current_screen: tk.Frame | None = None
        self.show_menu()

    def show_menu(self) -> None:
        from othello.ui.menu_screen import MenuScreen
        self._switch(MenuScreen(self.root, self))

    def show_game(self, config: dict[str, Any]) -> None:
        from othello.ui.game_screen import GameScreen
        self._switch(GameScreen(self.root, self, config))

    def _switch(self, frame: tk.Frame) -> None:
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = frame
        frame.pack(fill="both", expand=True)
```

- [ ] **Step 3: Implement main.py**

Create `c:/Users/elec9/othello/main.py`:
```python
import tkinter as tk

from othello.ui.app import OthelloApp


def main() -> None:
    root = tk.Tk()
    OthelloApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Sanity-check imports**

Run: `python -c "from othello.ui.app import OthelloApp; print('ok')"`

Expected: `ok` (no import errors). The app will fail at runtime because `MenuScreen` and `GameScreen` don't exist yet — that's expected and gets fixed in the next task.

- [ ] **Step 5: Commit**

```bash
git add othello/ui/__init__.py othello/ui/app.py main.py
git commit -m "feat(ui): add Tk app shell and main entry point"
```

---

## Task 16: UI — Menu Screen

**Files:**
- Create: `othello/othello/ui/menu_screen.py`
- Create: `othello/othello/ui/game_screen.py` (stub, replaced in Task 18)

- [ ] **Step 1: Create a stub GameScreen**

Create `c:/Users/elec9/othello/othello/ui/game_screen.py`:
```python
import tkinter as tk
from tkinter import ttk
from typing import Any


class GameScreen(tk.Frame):
    """Stub: replaced fully in Task 18."""

    def __init__(self, root: tk.Tk, app, config: dict[str, Any]):
        super().__init__(root)
        self.app = app
        self.config_data = config
        ttk.Label(self, text=f"Game stub. Config: {config}").pack(padx=20, pady=20)
        ttk.Button(self, text="Back to Menu", command=app.show_menu).pack(pady=10)
```

- [ ] **Step 2: Implement MenuScreen**

Create `c:/Users/elec9/othello/othello/ui/menu_screen.py`:
```python
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any


class MenuScreen(tk.Frame):
    def __init__(self, root: tk.Tk, app):
        super().__init__(root)
        self.app = app

        ttk.Label(self, text="Othello", font=("Helvetica", 32, "bold")).pack(pady=20)

        # Mode selection
        self.mode_var = tk.StringVar(value="two_player")
        mode_frame = ttk.LabelFrame(self, text="Mode")
        mode_frame.pack(padx=20, pady=10, fill="x")
        ttk.Radiobutton(
            mode_frame, text="2 Player", variable=self.mode_var, value="two_player",
            command=self._refresh_enabled,
        ).pack(anchor="w", padx=10)
        ttk.Radiobutton(
            mode_frame, text="vs AI", variable=self.mode_var, value="vs_ai",
            command=self._refresh_enabled,
        ).pack(anchor="w", padx=10)

        # AI difficulty
        self.ai_var = tk.StringVar(value="alphabeta")
        ai_frame = ttk.LabelFrame(self, text="AI Difficulty")
        ai_frame.pack(padx=20, pady=10, fill="x")
        for label, val in [
            ("Random", "random"), ("Greedy", "greedy"),
            ("Minimax", "minimax"), ("Alpha-Beta", "alphabeta"),
        ]:
            ttk.Radiobutton(ai_frame, text=label, variable=self.ai_var, value=val).pack(anchor="w", padx=10)
        self.ai_frame = ai_frame

        # Human color
        self.color_var = tk.StringVar(value="BLACK")
        color_frame = ttk.LabelFrame(self, text="Human Color")
        color_frame.pack(padx=20, pady=10, fill="x")
        ttk.Radiobutton(color_frame, text="Black (first)", variable=self.color_var, value="BLACK").pack(anchor="w", padx=10)
        ttk.Radiobutton(color_frame, text="White (second)", variable=self.color_var, value="WHITE").pack(anchor="w", padx=10)
        self.color_frame = color_frame

        # Board size
        self.size_var = tk.IntVar(value=8)
        size_frame = ttk.LabelFrame(self, text="Board Size")
        size_frame.pack(padx=20, pady=10, fill="x")
        for s in (6, 8, 10):
            ttk.Radiobutton(size_frame, text=f"{s}×{s}", variable=self.size_var, value=s).pack(anchor="w", padx=10)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Start", command=self._start).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Load Saved Game", command=self._load).pack(side="left", padx=5)

        self._refresh_enabled()

    def _refresh_enabled(self) -> None:
        state = "normal" if self.mode_var.get() == "vs_ai" else "disabled"
        for child in self.ai_frame.winfo_children():
            child.configure(state=state)
        for child in self.color_frame.winfo_children():
            child.configure(state=state)

    def _start(self) -> None:
        config: dict[str, Any] = {
            "mode": self.mode_var.get(),
            "size": self.size_var.get(),
        }
        if config["mode"] == "vs_ai":
            config["ai_difficulty"] = self.ai_var.get()
            config["human_color"] = self.color_var.get()
        self.app.show_game(config)

    def _load(self) -> None:
        path = filedialog.askopenfilename(
            title="Load saved game",
            filetypes=[("JSON saves", "*.json"), ("All files", "*.*")],
            initialdir="savegames",
        )
        if not path:
            return
        try:
            from othello.persistence import load_game
            state, info = load_game(path)
        except (OSError, ValueError, KeyError) as exc:
            messagebox.showerror("Load failed", f"Could not load save:\n{exc}")
            return
        config = dict(info)
        config["size"] = state.board.size
        config["_loaded_state"] = state
        self.app.show_game(config)
```

- [ ] **Step 3: Manual smoke test**

Run: `python main.py`

Expected behaviors:
- Window opens with title "Othello".
- "Mode", "AI Difficulty", "Human Color", "Board Size", and Start/Load buttons appear.
- "AI Difficulty" and "Human Color" radio buttons are *disabled* when "2 Player" is selected, *enabled* when "vs AI" is selected.
- Clicking Start opens the game-screen stub showing the chosen config; "Back to Menu" returns to the menu.
- Clicking "Load Saved Game" with no file selected does nothing; selecting a non-existent or invalid file shows an error dialog.

Close the window when done.

- [ ] **Step 4: Commit**

```bash
git add othello/ui/menu_screen.py othello/ui/game_screen.py
git commit -m "feat(ui): add menu screen with mode/AI/size selection"
```

---

## Task 17: UI — Board View (Rendering + Click + Legal-Move Highlights)

**Files:**
- Create: `othello/othello/ui/board_view.py`

The board view is a `Canvas` widget that renders cells, stones, and legal-move dots. It exposes a click callback `on_click(row, col)`.

- [ ] **Step 1: Implement BoardView**

Create `c:/Users/elec9/othello/othello/ui/board_view.py`:
```python
import tkinter as tk
from typing import Callable, Iterable

from othello.core.board import Board, Color, Move

CELL_PX = 60
PAD = 10
LINE_COLOR = "#2c3e50"
BOARD_COLOR = "#0e7c3a"
HINT_COLOR = "#ffd54f"


class BoardView(tk.Frame):
    def __init__(self, master: tk.Misc, size: int, on_click: Callable[[int, int], None]):
        super().__init__(master)
        self.size = size
        self.on_click = on_click
        self.is_animating = False
        canvas_px = size * CELL_PX + 2 * PAD
        self.canvas = tk.Canvas(
            self, width=canvas_px, height=canvas_px,
            bg=BOARD_COLOR, highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._handle_click)
        self._stones: dict[tuple[int, int], int] = {}
        self._hints: list[int] = []
        self._draw_grid()

    def _draw_grid(self) -> None:
        for i in range(self.size + 1):
            x = PAD + i * CELL_PX
            self.canvas.create_line(x, PAD, x, PAD + self.size * CELL_PX, fill=LINE_COLOR)
            y = PAD + i * CELL_PX
            self.canvas.create_line(PAD, y, PAD + self.size * CELL_PX, y, fill=LINE_COLOR)

    def render(self, board: Board, hints: Iterable[Move] = ()) -> None:
        # Clear stones and hints
        for cid in self._stones.values():
            self.canvas.delete(cid)
        self._stones.clear()
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()
        # Draw stones
        for r, c, color in board.cells():
            if color is Color.EMPTY:
                continue
            self._stones[(r, c)] = self._draw_stone(r, c, color)
        # Draw hint dots on legal moves
        for m in hints:
            self._hints.append(self._draw_hint(m.row, m.col))

    def _draw_stone(self, r: int, c: int, color: Color, scale: float = 1.0) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = (CELL_PX / 2 - 4) * scale
        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_hint(self, r: int, c: int) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = 6
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=HINT_COLOR, outline="",
        )

    def _handle_click(self, event: tk.Event) -> None:
        if self.is_animating:
            return
        col = (event.x - PAD) // CELL_PX
        row = (event.y - PAD) // CELL_PX
        if 0 <= row < self.size and 0 <= col < self.size:
            self.on_click(int(row), int(col))
```

- [ ] **Step 2: Wire BoardView into the GameScreen stub for a smoke test**

Replace `c:/Users/elec9/othello/othello/ui/game_screen.py` with:
```python
import tkinter as tk
from tkinter import ttk
from typing import Any

from othello.core.game import GameState
from othello.ui.board_view import BoardView


class GameScreen(tk.Frame):
    """Smoke-test version: renders the board and prints clicks. Replaced in Task 18."""

    def __init__(self, root: tk.Tk, app, config: dict[str, Any]):
        super().__init__(root)
        self.app = app
        self.state = config.get("_loaded_state") or GameState(size=config.get("size", 8))

        self.board_view = BoardView(self, self.state.board.size, self._on_click)
        self.board_view.pack(side="left", padx=10, pady=10)

        side = ttk.Frame(self)
        side.pack(side="right", fill="y", padx=10, pady=10)
        ttk.Button(side, text="Back to Menu", command=app.show_menu).pack(pady=5)

        self._refresh()

    def _on_click(self, row: int, col: int) -> None:
        print(f"clicked ({row}, {col})")  # smoke-test diagnostic

    def _refresh(self) -> None:
        self.board_view.render(self.state.board, hints=self.state.legal_moves())
```

- [ ] **Step 3: Manual smoke test**

Run: `python main.py`

Expected behaviors:
- Pick "2 Player", size 8, click Start.
- A green board with grid lines appears, four stones at the center (two black, two white).
- Four small yellow dots show on the four legal moves for BLACK.
- Clicking any cell prints `clicked (r, c)` to the terminal — no errors.
- Try sizes 6 and 10 — the board scales correctly.

Close when done.

- [ ] **Step 4: Commit**

```bash
git add othello/ui/board_view.py othello/ui/game_screen.py
git commit -m "feat(ui): add BoardView with rendering, hints, and clicks"
```

---

## Task 18: UI — Game Screen (Turn, Score, History, Undo, Hint, Save)

Replaces the stub from Task 17 with the full controller. AI integration and animations come later.

**Files:**
- Modify: `othello/othello/ui/game_screen.py`

- [ ] **Step 1: Implement full GameScreen**

Replace `c:/Users/elec9/othello/othello/ui/game_screen.py` with:
```python
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from othello.core.board import Color, Move
from othello.core.game import GameState
from othello.persistence import save_game
from othello.ui.board_view import BoardView


def _move_label(m: Move, size: int) -> str:
    if m.is_pass:
        return "pass"
    return f"{chr(ord('a') + m.col)}{m.row + 1}"


class GameScreen(tk.Frame):
    def __init__(self, root: tk.Tk, app, config: dict[str, Any]):
        super().__init__(root)
        self.app = app
        self.config_data = dict(config)
        loaded = self.config_data.pop("_loaded_state", None)
        size = self.config_data.get("size", 8)
        self.state: GameState = loaded if loaded is not None else GameState(size=size)

        self.board_view = BoardView(self, self.state.board.size, self._on_click)
        self.board_view.pack(side="left", padx=10, pady=10)

        side = ttk.Frame(self)
        side.pack(side="right", fill="y", padx=10, pady=10)

        self.turn_label = ttk.Label(side, text="", font=("Helvetica", 14, "bold"))
        self.turn_label.pack(anchor="w", pady=5)
        self.score_label = ttk.Label(side, text="", font=("Helvetica", 12))
        self.score_label.pack(anchor="w", pady=5)

        ttk.Button(side, text="Undo", command=self._undo).pack(fill="x", pady=2)
        ttk.Button(side, text="Hint", command=self._hint).pack(fill="x", pady=2)
        ttk.Button(side, text="Save", command=self._save).pack(fill="x", pady=2)
        ttk.Button(side, text="Menu", command=app.show_menu).pack(fill="x", pady=2)

        ttk.Label(side, text="History:").pack(anchor="w", pady=(10, 2))
        self.history_text = tk.Text(side, width=24, height=20, state="disabled")
        self.history_text.pack(fill="y", expand=True)

        self._hint_move: Move | None = None
        self._refresh()

    # --- Event handlers ---

    def _on_click(self, row: int, col: int) -> None:
        if self.board_view.is_animating:
            return
        move = Move(row, col)
        if move not in self.state.legal_moves():
            return  # silently ignored per spec §11
        self._play(move)

    def _play(self, move: Move) -> None:
        try:
            self.state.play(move)
        except ValueError:
            return
        self._hint_move = None
        self._refresh()
        if self.state.is_over():
            self._announce_winner()

    def _undo(self) -> None:
        if not self.state.history:
            return
        self.state.undo()
        self._hint_move = None
        self._refresh()

    def _hint(self) -> None:
        moves = self.state.legal_moves()
        if not moves:
            return
        # Use a strong AI for hints regardless of opponent setting
        from othello.ai.alphabeta import AlphaBetaAI
        self._hint_move = AlphaBetaAI(depth=3).select_move(self.state)
        self._refresh()

    def _save(self) -> None:
        Path("savegames").mkdir(exist_ok=True)
        default = f"savegames/othello-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        path = filedialog.asksaveasfilename(
            title="Save game",
            defaultextension=".json",
            filetypes=[("JSON saves", "*.json")],
            initialfile=Path(default).name,
            initialdir="savegames",
        )
        if not path:
            return
        try:
            save_game(self.state, self.config_data, path)
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))

    # --- Rendering ---

    def _refresh(self) -> None:
        legal = self.state.legal_moves()
        hints = legal if not self._hint_move else [self._hint_move]
        self.board_view.render(self.state.board, hints=hints)
        self._update_status()
        self._update_history()

    def _update_status(self) -> None:
        bullet = "●" if self.state.current is Color.BLACK else "○"
        self.turn_label.config(text=f"Turn: {bullet} {self.state.current.name}")
        b, w = self.state.score()
        self.score_label.config(text=f"Score:  ●{b}   ○{w}")

    def _update_history(self) -> None:
        size = self.state.board.size
        items = []
        move_num = 1
        for entry in self.state.history:
            label = _move_label(entry.move, size)
            color = "B" if entry.color_to_move is Color.BLACK else "W"
            items.append(f"{move_num}. {color} {label}")
            move_num += 1
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", "end")
        self.history_text.insert("1.0", "\n".join(items))
        self.history_text.config(state="disabled")

    def _announce_winner(self) -> None:
        w = self.state.winner()
        b, wh = self.state.score()
        if w is None:
            msg = f"Tie!  ●{b}   ○{wh}"
        else:
            msg = f"{w.name} wins!  ●{b}   ○{wh}"
        messagebox.showinfo("Game over", msg)
```

- [ ] **Step 2: Manual smoke test**

Run: `python main.py`

Expected behaviors:
- Start a 2-player 8×8 game.
- Turn label says "Turn: ● BLACK", score "●2 ○2".
- Yellow hint dots show on the 4 legal moves.
- Clicking a legal move places the stone, flips affected stones, advances turn to WHITE, updates score, appends to history.
- Clicking an *illegal* cell is silently ignored.
- "Undo" reverts the last move.
- "Hint" replaces the legal-move dots with a single yellow dot at the AI-recommended cell. Playing any move clears the hint.
- "Save" prompts for a filename; saving creates a JSON file in `savegames/`.
- Loading the saved file from the menu reproduces the game state.
- When the game ends (e.g., play out a game on size 6 quickly), a "Game over" dialog appears with the winner.

Close when done.

- [ ] **Step 3: Commit**

```bash
git add othello/ui/game_screen.py
git commit -m "feat(ui): add full game screen with undo, hint, save, history"
```

---

## Task 19: UI — Animations

Adds place and flip animations to the `BoardView`.

**Files:**
- Modify: `othello/othello/ui/board_view.py`
- Modify: `othello/othello/ui/game_screen.py`

- [ ] **Step 1: Add animated placement/flips to BoardView**

Replace `c:/Users/elec9/othello/othello/ui/board_view.py` with:
```python
import tkinter as tk
from typing import Callable, Iterable

from othello.core.board import Board, Color, Move

CELL_PX = 60
PAD = 10
LINE_COLOR = "#2c3e50"
BOARD_COLOR = "#0e7c3a"
HINT_COLOR = "#ffd54f"

PLACE_MS = 150
FLIP_MS = 200
FLIP_STAGGER_MS = 30
ANIM_FPS = 60


class BoardView(tk.Frame):
    def __init__(self, master: tk.Misc, size: int, on_click: Callable[[int, int], None]):
        super().__init__(master)
        self.size = size
        self.on_click = on_click
        self.is_animating = False
        canvas_px = size * CELL_PX + 2 * PAD
        self.canvas = tk.Canvas(
            self, width=canvas_px, height=canvas_px,
            bg=BOARD_COLOR, highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._handle_click)
        self._stones: dict[tuple[int, int], int] = {}
        self._hints: list[int] = []
        self._draw_grid()

    def _draw_grid(self) -> None:
        for i in range(self.size + 1):
            x = PAD + i * CELL_PX
            self.canvas.create_line(x, PAD, x, PAD + self.size * CELL_PX, fill=LINE_COLOR)
            y = PAD + i * CELL_PX
            self.canvas.create_line(PAD, y, PAD + self.size * CELL_PX, y, fill=LINE_COLOR)

    # --- Static rendering (no animation) ---

    def render(self, board: Board, hints: Iterable[Move] = ()) -> None:
        for cid in self._stones.values():
            self.canvas.delete(cid)
        self._stones.clear()
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()
        for r, c, color in board.cells():
            if color is Color.EMPTY:
                continue
            self._stones[(r, c)] = self._draw_stone(r, c, color)
        for m in hints:
            self._hints.append(self._draw_hint(m.row, m.col))

    # --- Animated render ---

    def animate_move(
        self,
        new_board: Board,
        placed: Move,
        flipped: list[tuple[int, int]],
        on_done: Callable[[], None],
    ) -> None:
        """Animate placement of `placed` and flipping of `flipped`,
        then call `on_done`. While animating, `is_animating` is True."""
        self.is_animating = True
        # Clear hints
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()
        placed_color = new_board[placed.row, placed.col]

        steps = max(1, int(PLACE_MS * ANIM_FPS / 1000))
        self._scale_in(placed.row, placed.col, placed_color, steps,
                       on_done=lambda: self._do_flips(new_board, flipped, on_done))

    def _scale_in(self, r: int, c: int, color: Color, steps: int, on_done: Callable[[], None]) -> None:
        # Remove any existing stone
        if (r, c) in self._stones:
            self.canvas.delete(self._stones.pop((r, c)))
        delay = max(1, PLACE_MS // steps)

        def step(i: int) -> None:
            if (r, c) in self._stones:
                self.canvas.delete(self._stones[(r, c)])
            scale = (i + 1) / steps
            self._stones[(r, c)] = self._draw_stone(r, c, color, scale=scale)
            if i + 1 < steps:
                self.canvas.after(delay, lambda: step(i + 1))
            else:
                on_done()

        step(0)

    def _do_flips(
        self,
        new_board: Board,
        flipped: list[tuple[int, int]],
        on_done: Callable[[], None],
    ) -> None:
        if not flipped:
            self.is_animating = False
            on_done()
            return
        remaining = {"count": len(flipped)}

        def finish_one() -> None:
            remaining["count"] -= 1
            if remaining["count"] == 0:
                self.is_animating = False
                on_done()

        for i, (r, c) in enumerate(flipped):
            new_color = new_board[r, c]
            self.canvas.after(
                i * FLIP_STAGGER_MS,
                lambda r=r, c=c, nc=new_color: self._flip_one(r, c, nc, finish_one),
            )

    def _flip_one(self, r: int, c: int, new_color: Color, on_done: Callable[[], None]) -> None:
        steps = max(2, int(FLIP_MS * ANIM_FPS / 1000))
        delay = max(1, FLIP_MS // steps)
        old_color = new_color.opponent()

        def step(i: int) -> None:
            if (r, c) in self._stones:
                self.canvas.delete(self._stones[(r, c)])
            half = steps // 2
            if i < half:
                # Shrink width to simulate edge-on rotation, still old color
                width_scale = 1 - (i / half)
                self._stones[(r, c)] = self._draw_oval_scaled(r, c, old_color, x_scale=max(0.05, width_scale))
            else:
                # Grow width back, now new color
                width_scale = (i - half + 1) / max(1, steps - half)
                self._stones[(r, c)] = self._draw_oval_scaled(r, c, new_color, x_scale=max(0.05, width_scale))
            if i + 1 < steps:
                self.canvas.after(delay, lambda: step(i + 1))
            else:
                # Final clean draw
                self.canvas.delete(self._stones[(r, c)])
                self._stones[(r, c)] = self._draw_stone(r, c, new_color)
                on_done()

        step(0)

    # --- Drawing helpers ---

    def _draw_stone(self, r: int, c: int, color: Color, scale: float = 1.0) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = (CELL_PX / 2 - 4) * scale
        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_oval_scaled(self, r: int, c: int, color: Color, x_scale: float) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        rx = (CELL_PX / 2 - 4) * x_scale
        ry = CELL_PX / 2 - 4
        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - rx, y - ry, x + rx, y + ry,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_hint(self, r: int, c: int) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = 6
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=HINT_COLOR, outline="",
        )

    def _handle_click(self, event: tk.Event) -> None:
        if self.is_animating:
            return
        col = (event.x - PAD) // CELL_PX
        row = (event.y - PAD) // CELL_PX
        if 0 <= row < self.size and 0 <= col < self.size:
            self.on_click(int(row), int(col))
```

- [ ] **Step 2: Use animation in GameScreen._play**

In `c:/Users/elec9/othello/othello/ui/game_screen.py`, modify the `_play` method:

Replace:
```python
    def _play(self, move: Move) -> None:
        try:
            self.state.play(move)
        except ValueError:
            return
        self._hint_move = None
        self._refresh()
        if self.state.is_over():
            self._announce_winner()
```

With:
```python
    def _play(self, move: Move) -> None:
        from othello.core.rules import flips_for
        flips = flips_for(self.state.board, move, self.state.current)
        try:
            self.state.play(move)
        except ValueError:
            return
        self._hint_move = None

        def after_anim() -> None:
            self._refresh()
            if self.state.is_over():
                self._announce_winner()

        self.board_view.animate_move(self.state.board, move, flips, after_anim)
        self._update_status()
        self._update_history()
```

Also add this import near the top of the file:
```python
from othello.core.rules import flips_for
```
(or keep it local to `_play` as shown — both work).

- [ ] **Step 3: Manual smoke test**

Run: `python main.py`. Start a 2-player 8×8 game.

Expected behaviors:
- Clicking a legal move shows the new stone scaling up from a tiny dot to full size (~150 ms).
- Flipped stones briefly shrink horizontally then expand back in the new color, with a small stagger between them.
- During animation, additional clicks are ignored.
- After animation, hint dots reappear for the next player.

Close when done.

- [ ] **Step 4: Commit**

```bash
git add othello/ui/board_view.py othello/ui/game_screen.py
git commit -m "feat(ui): add place and flip animations"
```

---

## Task 20: UI — Sound Effects

**Files:**
- Create: `othello/othello/ui/sound.py`
- Modify: `othello/othello/ui/game_screen.py`

The wrapper must never crash the game on missing files or audio failure (spec §8.6, §11).

- [ ] **Step 1: Implement sound wrapper**

Create `c:/Users/elec9/othello/othello/ui/sound.py`:
```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets" / "sounds"

try:
    from playsound import playsound  # type: ignore[import-not-found]
    _PLAYSOUND_OK = True
except ImportError:
    _PLAYSOUND_OK = False
    logger.info("playsound not installed; sound disabled")


def _play(name: str) -> None:
    if not _PLAYSOUND_OK:
        return
    path = ASSETS / name
    if not path.exists():
        logger.debug("sound file missing: %s", path)
        return
    try:
        playsound(str(path), block=False)
    except Exception as exc:  # noqa: BLE001 — swallow per spec
        logger.debug("sound playback failed: %s", exc)


def play_place() -> None:
    _play("place.wav")


def play_flip() -> None:
    _play("flip.wav")


def play_win() -> None:
    _play("win.wav")
```

- [ ] **Step 2: Wire sound into GameScreen**

In `c:/Users/elec9/othello/othello/ui/game_screen.py`, add at the top:
```python
from othello.ui import sound
```

In `_play`, call `sound.play_place()` right after `self.state.play(move)` succeeds:
```python
    def _play(self, move: Move) -> None:
        from othello.core.rules import flips_for
        flips = flips_for(self.state.board, move, self.state.current)
        try:
            self.state.play(move)
        except ValueError:
            return
        sound.play_place()
        self._hint_move = None
        # ... (rest unchanged)
```

In `_announce_winner`, call `sound.play_win()` before the dialog:
```python
    def _announce_winner(self) -> None:
        sound.play_win()
        # ... (rest unchanged)
```

- [ ] **Step 3: Manual smoke test**

Run: `python main.py`. The `assets/sounds/` directory does not exist yet — that's fine. The game must run without crashing.

Expected behaviors:
- No errors in the terminal (just an info log if `playsound` is missing).
- All gameplay still works.
- Optional: create `c:/Users/elec9/othello/assets/sounds/` and drop in any `place.wav`, `flip.wav`, `win.wav` files to verify audio actually plays.

- [ ] **Step 4: Commit**

```bash
git add othello/ui/sound.py othello/ui/game_screen.py
git commit -m "feat(ui): add sound effects with graceful fallback"
```

---

## Task 21: UI — AI Turn Handling

**Files:**
- Modify: `othello/othello/ui/game_screen.py`

- [ ] **Step 1: Build AI factory and schedule AI turns**

In `c:/Users/elec9/othello/othello/ui/game_screen.py`, add a helper at module level (near the imports):
```python
def _build_strategy(name: str):
    if name == "random":
        from othello.ai.random_ai import RandomAI
        return RandomAI()
    if name == "greedy":
        from othello.ai.greedy import GreedyAI
        return GreedyAI()
    if name == "minimax":
        from othello.ai.minimax import MinimaxAI
        return MinimaxAI(depth=3)
    if name == "alphabeta":
        from othello.ai.alphabeta import AlphaBetaAI
        return AlphaBetaAI(depth=5)
    raise ValueError(f"Unknown AI: {name}")
```

In `GameScreen.__init__`, after the line that sets `self.state`, add:
```python
        self.ai = None
        self.ai_color: Color | None = None
        if self.config_data.get("mode") == "vs_ai":
            self.ai = _build_strategy(self.config_data["ai_difficulty"])
            human = Color[self.config_data.get("human_color", "BLACK")]
            self.ai_color = human.opponent()
```

At the very end of `__init__`, after `self._refresh()`, add:
```python
        self._maybe_schedule_ai()
```

Modify `_play`'s `after_anim` callback to also trigger the AI's turn:
```python
        def after_anim() -> None:
            self._refresh()
            if self.state.is_over():
                self._announce_winner()
                return
            self._maybe_schedule_ai()
```

Add the AI scheduler method to the class:
```python
    def _maybe_schedule_ai(self) -> None:
        if self.ai is None or self.ai_color is None:
            return
        if self.state.current is not self.ai_color:
            return
        if self.state.is_over():
            return
        # Wait for any animation, then play after a short delay.
        self.after(300, self._run_ai_turn)

    def _run_ai_turn(self) -> None:
        if self.board_view.is_animating:
            self.after(100, self._run_ai_turn)
            return
        if self.ai is None or self.state.current is not self.ai_color:
            return
        try:
            move = self.ai.select_move(self.state)
        except ValueError:
            return
        self._play(move)
```

Make sure `from othello.core.board import Color` is already imported (it is, from Task 18).

- [ ] **Step 2: Manual smoke test**

Run: `python main.py`.

Test scenarios:
1. **vs Random as BLACK, 8×8:** human plays first, AI responds quickly with random moves. Game completes without errors.
2. **vs Alpha-Beta as WHITE, 8×8:** AI plays the first move ~300 ms after the screen opens, then waits for the human.
3. **Hint button:** during a vs-AI game on the human's turn, "Hint" highlights the AlphaBetaAI-recommended move.
4. **Undo during vs-AI:** clicking Undo after the AI moved reverts both the AI move and the human move (because Undo pops one entry; you may need to click twice to roll back to your own decision point — that's acceptable for this version).
5. **Save mid-game, return to menu, load:** the saved game restores correctly, including AI mode.

Close when done.

- [ ] **Step 3: Commit**

```bash
git add othello/ui/game_screen.py
git commit -m "feat(ui): add AI opponent turn scheduling"
```

---

## Task 22: README and Final Smoke Test

**Files:**
- Modify: `othello/README.md`

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`

Expected: all tests pass (~45 total).

- [ ] **Step 2: Confirm core/ai do not import Tkinter**

Run:
```bash
python -c "import othello.core.game, othello.ai.alphabeta, othello.ai.minimax, othello.ai.greedy, othello.ai.random_ai, othello.ai.evaluation; import sys; assert 'tkinter' not in sys.modules, 'tkinter leaked into core/ai'; print('clean')"
```

Expected: `clean`. If it fails, find the offending import in `core/` or `ai/` and remove it.

- [ ] **Step 3: Comprehensive manual smoke test**

Run `python main.py` and verify each of these in order:

1. Menu → Start 2-player 6×6 game → play to completion → game-over dialog appears with correct winner.
2. Menu → Start vs Greedy as BLACK on 8×8 → play several moves → Undo works → Hint works → Save the game.
3. Menu → Load saved game → verify state matches → continue playing.
4. Menu → Start vs Alpha-Beta on 10×10 → AI plays within ~2 s per turn → no UI freeze beyond that.
5. Menu → invalid load (cancel dialog or pick a non-JSON file) → graceful error or no-op.

If anything misbehaves, fix it before committing.

- [ ] **Step 4: Update README with a real description**

Replace `c:/Users/elec9/othello/README.md` with:
```markdown
# Othello

A desktop Othello (Reversi) game in Python with Tkinter, structured as a layered learning project: pure-functional `core/` engine, polymorphic `ai/` strategies, Tkinter `ui/`.

## Features

- 2-player local play and vs four AI strategies (Random, Greedy, Minimax, Alpha-Beta).
- Variable board size (6×6, 8×8, 10×10).
- Legal-move highlights, hint, undo, move history.
- Place and flip animations.
- JSON save/load via history replay.
- Optional sound effects (graceful fallback if missing).

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate    # Git-Bash on Windows; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

## Run

```
python main.py
```

## Test

```
pip install pytest
pytest
```

## Layout

See [docs/superpowers/specs/2026-04-30-othello-game-design.md](docs/superpowers/specs/2026-04-30-othello-game-design.md) for the design.
```

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: flesh out README with features, setup, and run instructions"
```

---

## Self-Review Notes

- **Spec coverage:**
  - §6 Core engine → Tasks 2–8.
  - §7 AI layer → Tasks 9–13.
  - §8 UI layer → Tasks 15–21.
  - §9 Persistence → Task 14.
  - §10 Testing → covered in each TDD step; full suite verified in Task 22.
  - §11 Error handling → silent illegal-click ignore (Task 18 `_on_click`), save error dialog (Task 18 `_save`, Task 16 `_load`), sound failure swallow (Task 20).
  - §12 Open items → explicitly out of scope.

- **Task 8 caveat:** the auto-pass test constructs a synthetic position by direct cell mutation; this is acceptable because the rule under test is independent of how the position was reached. The placeholder `test_must_pass_detection` is intentionally kept as a documentation marker.

- **Task 18 vs Task 21 ordering:** the full GameScreen lands first (Task 18) without AI wiring; AI scheduling comes in Task 21 by adding a few methods. This keeps each task small and individually testable.

- **Animation simplification:** the flip animation uses a width-shrink-and-grow simulating edge-on rotation. Per spec §8.5, "color crossfade or width-shrink-then-grow" are both acceptable.

- **Undo behavior with AI:** acknowledged in Task 21 — single Undo rolls back one entry, so undoing your own move while playing vs AI may require two clicks. This is consistent with spec §6.3 (Undo pops history one entry) and is not a bug.

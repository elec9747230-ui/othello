# Othello Game — Design Spec

- Date: 2026-04-30
- Status: Approved (brainstorming complete)
- Project type: Learning project (clean architecture practice)

## 1. Overview

Build an Othello (Reversi) desktop game in Python with Tkinter. The primary goal is to practice clean architecture: cleanly separating game logic, AI strategies, and UI, with each layer testable and replaceable.

The game supports 2-player local play and play against four AI opponents of increasing strength (Random, Greedy, Minimax, Alpha-Beta with weighted evaluation). Board size is configurable (6×6, 8×8, 10×10).

## 2. Goals

- A complete, playable Othello game with a Tkinter GUI.
- A pure-Python core engine with no UI or AI dependencies — fully unit-testable.
- Four AI strategies sharing a single `Strategy` interface to demonstrate polymorphism.
- Quality-of-life UX: legal-move highlighting, score, undo, hint, move history, save/load, animations, sound effects.
- Variable board size (6/8/10) without hard-coded magic numbers.

## 3. Non-Goals

- Online multiplayer / networking.
- Mobile / web targets.
- Tournament-strength AI (e.g., MCTS, deep learning).
- Localization beyond a single language.
- Custom themes / skinnable UI.

## 4. Constraints

- Python 3.10+ (uses `dataclasses`, `match`, `Enum`, type hints, ABC).
- Standard library first; external dependencies limited to:
  - `playsound` (sound effects, cross-platform)
  - `pytest` (tests, dev-only)
- Tkinter ships with Python — no extra GUI dependency.
- Cross-platform (Windows / macOS / Linux).

## 5. Architecture

Three-layer architecture with strict dependency direction:

```
ui/  →  ai/  →  core/
        ai/  ────→ core/
```

- `core/` imports nothing from `ai/` or `ui/`.
- `ai/` imports only from `core/`.
- `ui/` imports from both, and is the only layer that imports Tkinter / playsound.

### 5.1 Project Layout

```
othello/
├── README.md
├── requirements.txt              # playsound; pytest in [dev]
├── main.py                       # entry point
├── othello/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── board.py              # Board, Color, Move
│   │   ├── rules.py              # legal_moves, apply_move, is_terminal, winner, score
│   │   └── game.py               # GameState (history, undo, auto-pass)
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── base.py               # Strategy ABC
│   │   ├── random_ai.py
│   │   ├── greedy.py
│   │   ├── minimax.py
│   │   ├── alphabeta.py
│   │   └── evaluation.py         # weighted_position_score, generic_score
│   ├── persistence.py            # save_game, load_game (JSON)
│   └── ui/
│       ├── __init__.py
│       ├── app.py                # Tk root, screen switching
│       ├── menu_screen.py
│       ├── game_screen.py
│       ├── board_view.py         # Canvas rendering, animations
│       └── sound.py              # playsound wrapper
├── assets/
│   └── sounds/
│       ├── place.wav
│       ├── flip.wav
│       └── win.wav
├── savegames/                    # runtime, .gitignored
└── tests/
    ├── test_rules.py
    ├── test_game.py
    └── test_ai.py
```

## 6. Core Engine (`core/`)

### 6.1 Board Representation

8×8 (or N×N) **2D list** of `Color` enums. Chosen for clarity over speed.

```python
class Color(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def opponent(self) -> "Color": ...

@dataclass(frozen=True)
class Move:
    row: int
    col: int

# Module-level constant for pass:
PASS: Move  # sentinel; e.g., Move(-1, -1)
```

`Board` exposes:
- `Board(size: int = 8)` — initializes with four center stones in standard pattern; raises `ValueError` if `size` is odd or < 4.
- `size: int`
- `__getitem__((r, c)) -> Color` / `__setitem__`
- `copy() -> Board`
- `cells() -> Iterator[tuple[int, int, Color]]`

### 6.2 Rules (`rules.py`) — pure functions

```python
def legal_moves(board: Board, color: Color) -> list[Move]
def apply_move(board: Board, move: Move, color: Color) -> Board   # returns NEW board
def is_terminal(board: Board) -> bool
def winner(board: Board) -> Color | None                           # None = tie
def score(board: Board) -> tuple[int, int]                         # (black_count, white_count)
```

**Immutability:** `apply_move` returns a new `Board`. Originals are never mutated. Reasons:
- Natural for AI search trees (no need to undo within recursion).
- Trivializes undo at the `GameState` level (replace state, no inverse logic).
- Reinforces functional discipline as a learning goal.

### 6.3 GameState (`game.py`)

Owns game progression and history.

```python
@dataclass
class HistoryEntry:
    board_before: Board
    color_to_move: Color
    move: Move

class GameState:
    board: Board
    current: Color
    history: list[HistoryEntry]

    def __init__(self, size: int = 8): ...

    def legal_moves(self) -> list[Move]
    def must_pass(self) -> bool                # legal_moves(current) is empty but opponent has moves
    def is_over(self) -> bool                  # neither side has moves
    def play(self, move: Move) -> None         # delegates to rules; pushes history; auto-passes
    def undo(self) -> None                     # pops history, restores board+current
    def score(self) -> tuple[int, int]
    def winner(self) -> Color | None
```

**Auto-pass behavior:** After `play`, if the next player has no legal moves but the just-played player still has moves, the turn returns to the previous player (a pass is recorded as `Move.PASS` in history). If neither side has moves, `is_over()` returns True.

## 7. AI Layer (`ai/`)

### 7.1 Strategy Interface

```python
class Strategy(ABC):
    name: str

    @abstractmethod
    def select_move(self, state: GameState) -> Move:
        """Must return a legal move from state.legal_moves(). Raises if none."""
```

The UI never branches on AI type — it always calls `strategy.select_move(state)`. Hint reuses the same interface (calls a configured Strategy and renders the returned move as a hint marker).

### 7.2 Implementations

| Class | Module | Behavior |
|---|---|---|
| `RandomAI` | `random_ai.py` | Uniform random over legal moves |
| `GreedyAI` | `greedy.py` | Move maximizing immediate flip count |
| `MinimaxAI` | `minimax.py` | Minimax with depth-limited search, default depth 3 |
| `AlphaBetaAI` | `alphabeta.py` | Alpha-Beta pruning, default depth 5 |

`MinimaxAI` and `AlphaBetaAI` accept `depth: int` constructor parameter (defaults above).

### 7.3 Evaluation Function (`evaluation.py`)

```python
def evaluate(board: Board, color: Color) -> int
```

Dispatches by board size:
- **8×8:** `weighted_position_score` using the standard positional weight table (corners +100, X-squares -25, edges +10, etc.).
- **6×6 / 10×10 / other:** `generic_score` — corner +30, edge +5, interior +1, sign flipped for opponent.

End-game (no empty cells or terminal): returns large positive/negative based on piece-count winner.

## 8. UI Layer (`ui/`)

### 8.1 Screen Flow

```
Menu Screen ──Start──▶ Game Screen
     ▲                      │
     └────"Back to Menu"────┘
     │
     └────"Load Game"───────▶ Game Screen
```

`app.py` owns the `Tk` root and switches between `Frame` screens via `pack_forget()` / `pack()`.

### 8.2 Menu Screen

Controls:
- Mode: 2-Player / vs AI (radio)
- AI difficulty: Random / Greedy / Minimax / Alpha-Beta (enabled only for vs AI)
- Human color: Black / White (enabled only for vs AI)
- Board size: 6 / 8 / 10
- Buttons: [Start], [Load Saved Game]

### 8.3 Game Screen

Layout:
```
┌────────────────────────┬──────────────┐
│                        │ Turn: ● BLACK │
│                        │ Score: ●3 ○3  │
│      Board Canvas      │              │
│   (size × size grid)   │ [Undo]       │
│                        │ [Hint]       │
│                        │ [Save]       │
│                        │ [Menu]       │
└────────────────────────┴──────────────┘
                         History: 1.d3 2.c5 ...
```

### 8.4 Board Rendering (`board_view.py`)

- `tkinter.Canvas` draws cell rectangles + stone ovals.
- Legal moves: small dot or translucent ring on empty cells where current player can play.
- Click handler: maps pixel `(x, y)` → `(row, col)` → calls `controller.try_play(Move(row, col))`.
- Canvas resizes proportionally to chosen board size.

### 8.5 Animations

All animations live in the UI layer; `core/` has no animation concept.

- **Place:** scale-up from 0% to 100% over ~150 ms.
- **Flip:** color crossfade or width-shrink-then-grow simulating rotation, ~200 ms per stone, with ~30 ms stagger across stones in one play.
- During animation, `is_animating` flag disables clicks. AI moves are scheduled only after animation completes.

### 8.6 Sound Effects (`sound.py`)

Wrapper around `playsound`:
- `play_place()` on stone placement.
- `play_flip()` per flipped stone (or once per move — final decision during implementation; both are acceptable).
- `play_win()` on terminal state.

Failure to play (missing file, audio unavailable) must not crash the game — wrap in try/except, log only.

### 8.7 AI Turn Handling

When `state.current` belongs to an AI:
1. Wait for any pending animation to finish.
2. Disable input.
3. Schedule `root.after(300, run_ai)` for a short visible delay.
4. `run_ai` calls `strategy.select_move(state)` synchronously, plays the move, triggers animation.

Synchronous AI is acceptable for depth 5 Alpha-Beta on 8×8. If observable lag becomes a problem, move AI calls to a background thread; first-pass implementation stays synchronous.

## 9. Persistence (`persistence.py`)

Save format (JSON):

```json
{
  "version": 1,
  "size": 8,
  "current": "BLACK",
  "mode": "vs_ai",
  "ai_difficulty": "alphabeta",
  "human_color": "BLACK",
  "history": [
    {"row": 2, "col": 3, "color": "BLACK"},
    {"row": 2, "col": 4, "color": "WHITE"}
  ]
}
```

**History-based, not board-snapshot:** loading replays moves on a fresh board through the rules, guaranteeing rule-consistent state regardless of file content. Smaller, human-readable, and naturally extensible to a future kifu/notation export.

API:
```python
def save_game(state: GameState, mode_info: dict, path: Path) -> None
def load_game(path: Path) -> tuple[GameState, dict]
```

Saves go under `savegames/` by default with timestamped filenames; user can choose path via file dialog.

On load failure (corrupt file, version mismatch, illegal move during replay): show an error message box and remain on the current screen.

## 10. Testing

`pytest` is the only test runner. Tests cover `core/` + `ai/` only.

| File | Coverage |
|---|---|
| `test_rules.py` | Initial board for sizes 6/8/10; legal-move calculation across directions; flip correctness; terminal/winner; pass conditions |
| `test_game.py` | `play` → `undo` round-trip restores board + current; auto-pass; `is_over` end-game; history integrity |
| `test_ai.py` | Every Strategy returns only legal moves; Greedy maximizes flip count; Minimax and AlphaBeta produce identical move on same state at same depth (validates pruning correctness) |

Tests must pass with `pytest` from project root with no Tkinter installed runtime context (i.e., `core/` and `ai/` import paths must not transitively import Tkinter).

## 11. Error Handling

- **Invalid click** (empty cell that isn't a legal move, or non-empty cell): silently ignored at UI level; legal-move highlight already guides the user.
- **Save file corruption / version mismatch:** error dialog, return to menu screen.
- **Strategy called with no legal moves:** should be unreachable due to GameState's auto-pass; guarded by an `assert`.
- **Sound playback failure:** caught and logged, never crashes.

## 12. Open Items / Future Work

These are explicitly out of scope for the first version but worth flagging:

- Difficulty-tunable depth in the menu (currently fixed at depth 3 / 5).
- AI thread offloading if depth-5 Alpha-Beta lags on slower machines.
- Export game as standard kifu / notation file.
- Themed board colors / piece styles.
- Replay mode (step through saved history).

## 13. Summary

A clean, layered Othello implementation: pure-functional core, polymorphic AI, Tkinter UI with animations and sound. Designed for clarity, testability, and future extension while staying scoped to a learning project.

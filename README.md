# Othello

A desktop Othello (Reversi) game in Python with Tkinter, structured as a layered learning project: pure-functional `core/` engine, polymorphic `ai/` strategies, Tkinter `ui/`.

## Features

- 2-player local play and vs four AI strategies (Random, Greedy, Minimax, Alpha-Beta).
- Variable board size (6x6, 8x8, 10x10).
- Legal-move highlights, hint, undo, move history.
- Place and flip animations.
- JSON save/load via history replay.
- Optional sound effects (graceful fallback if missing).

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate    # Git-Bash on Windows; .venv/bin/activate on macOS/Linux
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

## Architecture

The codebase is organised in three layers with one-way dependencies (`ui` → `ai` → `core`), so the engine and AI run headless without Tkinter.

### Class diagrams

Split per layer for readability. Full single-diagram source: [docs/uml/classes_Othello.mmd](docs/uml/classes_Othello.mmd) (also available as [.puml](docs/uml/classes_Othello.puml), [.svg](docs/uml/classes_Othello.svg), [.png](docs/uml/classes_Othello.png)).

#### AI Strategy hierarchy

Four AI implementations share the abstract `Strategy` interface, swappable at runtime via `GameScreen`.

```mermaid
classDiagram
  direction TB
  class Strategy {
    <<abstract>>
    +name : str
    +select_move(state)*  Move
  }
  class RandomAI {
    +name = "Random"
  }
  class GreedyAI {
    +name = "Greedy"
  }
  class MinimaxAI {
    +depth = 3
    +name = "Minimax"
  }
  class AlphaBetaAI {
    +depth = 5
    +name = "Alpha-Beta"
  }
  RandomAI --|> Strategy
  GreedyAI --|> Strategy
  MinimaxAI --|> Strategy
  AlphaBetaAI --|> Strategy
```

#### Core domain

Pure-functional engine with no GUI dependencies. `GameState` owns a `Board` and a list of `HistoryEntry` snapshots for undo.

```mermaid
classDiagram
  direction TB
  class GameState {
    +board : Board
    +current : Color
    +history : list[HistoryEntry]
    +legal_moves() list[Move]
    +play(move)
    +undo()
    +is_over() bool
    +winner() Color | None
    +score() tuple[int, int]
  }
  class Board {
    +size : int
    +copy() Board
    +cells() Iterator
    +in_bounds(r, c) bool
  }
  class HistoryEntry {
    +move : Move
    +color_to_move : Color
    +board_before : Board
  }
  class Move {
    +row : int
    +col : int
    +is_pass : bool
  }
  class Color {
    <<Enum>>
    BLACK
    WHITE
    +opponent() Color
  }
  Board --* GameState : board
  GameState --> HistoryEntry : history
  HistoryEntry --> Move : move
  HistoryEntry --> Color : color_to_move
  HistoryEntry --> Board : board_before
```

#### UI composition

`OthelloApp` swaps between `MenuScreen` and `GameScreen`. The latter aggregates the live `GameState`, the rendered `BoardView`, and an optional `Strategy` (only in vs-AI mode).

```mermaid
classDiagram
  direction TB
  class OthelloApp {
    +root : Tk
    +current_screen : tk.Frame | None
    +show_menu()
    +show_game(config)
  }
  class MenuScreen {
    +mode_var : StringVar
    +ai_var : StringVar
    +color_var : StringVar
    +size_var : IntVar
  }
  class GameScreen {
    +state : GameState
    +board_view : BoardView
    +ai : Strategy | None
    +ai_color : Color | None
    +turn_label : Label
    +score_label : Label
  }
  class BoardView {
    +canvas : Canvas
    +size : int
    +is_animating : bool
    +on_click : Callable
    +render(board, hints)
    +animate_move(...)
  }
  GameScreen --> OthelloApp : app
  MenuScreen --> OthelloApp : app
  BoardView --* GameScreen : board_view
```

<details>
<summary>Show full single-diagram class diagram (wide)</summary>

```mermaid
classDiagram
  class AlphaBetaAI {
    depth : int
    name : str
    select_move(state: GameState) Move
  }
  class Board {
    size : int
    cells() Iterator[tuple[int, int, Color]]
    copy() 'Board'
    in_bounds(r: int, c: int) bool
  }
  class BoardView {
    canvas : Canvas
    is_animating : bool
    on_click : Callable[[int, int], None]
    size : int
    animate_move(new_board: Board, placed: Move, flipped: list[tuple[int, int]], on_done: Callable[[], None]) None
    render(board: Board, hints: Iterable[Move]) None
  }
  class Color {
    name
    opponent() 'Color'
  }
  class GameScreen {
    ai : NoneType
    ai_color : Color | None
    app
    board_view
    config_data : dict
    history_text : Text
    score_label : Label
    state
    turn_label : Label
  }
  class GameState {
    board
    current : BLACK, WHITE
    history : list[HistoryEntry]
    is_over() bool
    legal_moves() list[Move]
    must_pass() bool
    play(move: Move) None
    score() tuple[int, int]
    undo() None
    winner() Color | None
  }
  class GreedyAI {
    name : str
    select_move(state: GameState) Move
  }
  class HistoryEntry {
    board_before
    color_to_move
    move
  }
  class MenuScreen {
    ai_frame : Labelframe
    ai_var : StringVar
    app
    color_frame : Labelframe
    color_var : StringVar
    mode_var : StringVar
    size_var : IntVar
  }
  class MinimaxAI {
    depth : int
    name : str
    select_move(state: GameState) Move
  }
  class Move {
    col : int
    is_pass : bool
    row : int
  }
  class OthelloApp {
    current_screen : tk.Frame | None
    root : Tk
    show_game(config: dict[str, Any]) None
    show_menu() None
  }
  class RandomAI {
    name : str
    select_move(state: GameState) Move
  }
  class Strategy {
    name : str
    select_move(state: GameState)* Move
  }
  AlphaBetaAI --|> Strategy
  GreedyAI --|> Strategy
  MinimaxAI --|> Strategy
  RandomAI --|> Strategy
  HistoryEntry --> Board : board_before
  HistoryEntry --> Color : color_to_move
  HistoryEntry --> Move : move
  GameScreen --> GameState : state
  GameState --> HistoryEntry : history
  AlphaBetaAI --* GameScreen : ai
  GreedyAI --* GameScreen : ai
  MinimaxAI --* GameScreen : ai
  RandomAI --* GameScreen : ai
  Board --* GameState : board
  BoardView --* GameScreen : board_view
```

</details>

### Module dependency graph

19 modules, 41 imports — no cycles. Source: [docs/uml/packages_Othello.mmd](docs/uml/packages_Othello.mmd).

```mermaid
classDiagram
  class alphabeta
  class base
  class evaluation
  class greedy
  class minimax
  class random_ai
  class board
  class game
  class rules
  class persistence
  class app
  class board_view
  class game_screen
  class menu_screen
  class sound
  alphabeta --> base
  alphabeta --> evaluation
  alphabeta --> board
  alphabeta --> game
  alphabeta --> rules
  base --> board
  base --> game
  evaluation --> board
  evaluation --> rules
  greedy --> base
  greedy --> board
  greedy --> game
  greedy --> rules
  minimax --> base
  minimax --> evaluation
  minimax --> board
  minimax --> game
  minimax --> rules
  random_ai --> base
  random_ai --> board
  random_ai --> game
  game --> board
  game --> rules
  rules --> board
  persistence --> board
  persistence --> game
  app --> game_screen
  app --> menu_screen
  board_view --> board
  game_screen --> alphabeta
  game_screen --> greedy
  game_screen --> minimax
  game_screen --> random_ai
  game_screen --> board
  game_screen --> game
  game_screen --> rules
  game_screen --> persistence
  game_screen --> board_view
  game_screen --> sound
  menu_screen --> persistence
```

### Regenerating diagrams

```bash
pip install pylint                       # provides pyreverse
# Graphviz only needed for png/svg output:
#   winget install Graphviz.Graphviz     (Windows)
pyreverse -o mmd -p Othello -d docs/uml othello
pyreverse -o puml -p Othello -d docs/uml othello
pyreverse -o png  -p Othello -d docs/uml othello   # needs Graphviz on PATH
pyreverse -o svg  -p Othello -d docs/uml othello   # needs Graphviz on PATH
```

## Layout

See [docs/superpowers/specs/2026-04-30-othello-game-design.md](docs/superpowers/specs/2026-04-30-othello-game-design.md) for the design (English) and [docs/superpowers/specs/2026-04-30-othello-game-design-ko.md](docs/superpowers/specs/2026-04-30-othello-game-design-ko.md) for Korean.

Implementation plan: [docs/superpowers/plans/2026-04-30-othello-implementation.md](docs/superpowers/plans/2026-04-30-othello-implementation.md) (Korean: [-ko.md](docs/superpowers/plans/2026-04-30-othello-implementation-ko.md)).

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

## Layout

See [docs/superpowers/specs/2026-04-30-othello-game-design.md](docs/superpowers/specs/2026-04-30-othello-game-design.md) for the design (English) and [docs/superpowers/specs/2026-04-30-othello-game-design-ko.md](docs/superpowers/specs/2026-04-30-othello-game-design-ko.md) for Korean.

Implementation plan: [docs/superpowers/plans/2026-04-30-othello-implementation.md](docs/superpowers/plans/2026-04-30-othello-implementation.md) (Korean: [-ko.md](docs/superpowers/plans/2026-04-30-othello-implementation-ko.md)).

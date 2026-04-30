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
            continue
        expected_color = Color[entry["color"]]
        if state.current is not expected_color:
            raise ValueError(
                f"Replay mismatch at {move}: expected {state.current.name}, "
                f"saved as {expected_color.name}"
            )
        state.play(move)
    return state, data.get("mode_info", {})

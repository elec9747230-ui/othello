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
    p.write_text(
        '{"version": 1, "size": 8, "current": "BLACK", '
        '"mode_info": {}, "history": [{"row": 0, "col": 0, "color": "BLACK"}]}'
    )
    with pytest.raises(ValueError):
        load_game(p)

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

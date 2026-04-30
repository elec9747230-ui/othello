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
    assert b[3, 3] is Color.WHITE
    assert b[4, 4] is Color.WHITE
    assert b[3, 4] is Color.BLACK
    assert b[4, 3] is Color.BLACK
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

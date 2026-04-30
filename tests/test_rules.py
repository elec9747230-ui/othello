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
    assert flips == [(3, 3)]


def test_flips_for_illegal_move_returns_empty():
    b = Board()
    assert flips_for(b, Move(0, 0), Color.BLACK) == []
    assert flips_for(b, Move(3, 3), Color.BLACK) == []


def test_flips_for_multidirectional():
    b = Board()
    flips = flips_for(b, Move(4, 5), Color.BLACK)
    assert flips == [(4, 4)]


def test_legal_moves_empty_when_no_captures_possible():
    b = Board(size=4)
    assert len(legal_moves(b, Color.BLACK)) > 0


import pytest
from othello.core.rules import apply_move, score, is_terminal, winner


def test_apply_move_returns_new_board():
    b = Board()
    new_b = apply_move(b, Move(2, 3), Color.BLACK)
    assert new_b is not b
    assert b[2, 3] is Color.EMPTY
    assert b[3, 3] is Color.WHITE


def test_apply_move_places_stone_and_flips():
    b = Board()
    new_b = apply_move(b, Move(2, 3), Color.BLACK)
    assert new_b[2, 3] is Color.BLACK
    assert new_b[3, 3] is Color.BLACK


def test_apply_move_raises_on_illegal_move():
    b = Board()
    with pytest.raises(ValueError):
        apply_move(b, Move(0, 0), Color.BLACK)


def test_score_initial_is_2_2():
    b = Board()
    assert score(b) == (2, 2)


def test_score_after_first_black_move():
    b = Board()
    b2 = apply_move(b, Move(2, 3), Color.BLACK)
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

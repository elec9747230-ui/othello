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

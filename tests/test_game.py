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
    assert s.board[3, 3] is Color.BLACK
    assert len(s.history) == 1


def test_play_illegal_move_raises():
    s = GameState()
    with pytest.raises(ValueError):
        s.play(Move(0, 0))


def test_undo_restores_previous_state():
    s = GameState()
    snapshot = [[s.board[r, c] for c in range(s.board.size)] for r in range(s.board.size)]
    s.play(Move(2, 3))
    s.undo()
    assert s.current is Color.BLACK
    for r in range(s.board.size):
        for c in range(s.board.size):
            assert s.board[r, c] is snapshot[r][c]
    assert s.history == []


def test_undo_without_history_raises():
    s = GameState()
    with pytest.raises(IndexError):
        s.undo()


def test_play_undo_round_trip_two_moves():
    s = GameState()
    s.play(Move(2, 3))
    s.play(Move(2, 2))
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


def _build_auto_pass_position() -> GameState:
    """Construct a synthetic position where after BLACK plays (1,2),
    WHITE has no legal moves but BLACK still does.

    Setup:
        (2,2)=W, (3,2)=B → BLACK at (1,2) flips (2,2) vertically.
        (5,5)=W boxed in by (5,6)=B, (5,7)=B (corner) so WHITE cannot capture.
    After play: only (5,5) remains WHITE; WHITE has no captures.
    BLACK can still play (5,4) which flips (5,5)."""
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.EMPTY
    # Vertical line: WHITE at (2,2), BLACK column extending all the way
    # to the bottom edge so WHITE has no flipping line in this column.
    s.board[2, 2] = Color.WHITE
    for r in range(3, s.board.size):
        s.board[r, 2] = Color.BLACK
    # Isolated WHITE corner cluster: (5,5)=W, sandwiched only by BLACK on
    # one side reaching the corner — WHITE cannot capture into the corner.
    s.board[5, 5] = Color.WHITE
    s.board[5, 6] = Color.BLACK
    s.board[5, 7] = Color.BLACK
    s.current = Color.BLACK
    return s


def test_auto_pass_when_opponent_has_no_moves():
    s = _build_auto_pass_position()
    from othello.core.rules import legal_moves
    assert legal_moves(s.board, Color.WHITE) == []
    s.play(Move(1, 2))
    assert s.current is Color.BLACK
    assert len(s.history) == 2
    assert s.history[-1].move.is_pass


def test_undo_after_auto_pass_pops_both_entries():
    s = _build_auto_pass_position()
    s.play(Move(1, 2))
    assert len(s.history) == 2
    s.undo()
    assert s.current is Color.BLACK
    assert s.history == []
    assert s.board[1, 2] is Color.EMPTY
    assert s.board[2, 2] is Color.WHITE
    assert s.board[3, 2] is Color.BLACK


def test_is_over_when_neither_side_has_moves():
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.BLACK
    assert s.is_over() is True

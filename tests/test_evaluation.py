from othello.core.board import Board, Color
from othello.ai.evaluation import evaluate


def test_evaluate_initial_position_is_neutral():
    b = Board()
    assert evaluate(b, Color.BLACK) == 0


def test_evaluate_corner_value_is_high_for_owner_8x8():
    b = Board()
    b[0, 0] = Color.BLACK
    val_black = evaluate(b, Color.BLACK)
    val_white = evaluate(b, Color.WHITE)
    assert val_black > 0
    assert val_white < 0
    assert val_black == -val_white


def test_evaluate_endgame_uses_score_difference():
    b = Board()
    for r in range(b.size):
        for c in range(b.size):
            b[r, c] = Color.BLACK
    val = evaluate(b, Color.BLACK)
    assert val > 1000


def test_evaluate_works_for_6x6_and_10x10():
    b6 = Board(size=6)
    b10 = Board(size=10)
    assert isinstance(evaluate(b6, Color.BLACK), int)
    assert isinstance(evaluate(b10, Color.BLACK), int)

import pytest
from othello.core.game import GameState
from othello.core.board import Color
from othello.core.rules import flips_for
from othello.ai.base import Strategy
from othello.ai.random_ai import RandomAI
from othello.ai.greedy import GreedyAI
from othello.ai.minimax import MinimaxAI
from othello.ai.alphabeta import AlphaBetaAI


# --- Strategy ABC ---

def test_strategy_is_abstract():
    with pytest.raises(TypeError):
        Strategy()


# --- RandomAI ---

def test_random_ai_returns_legal_move():
    s = GameState()
    ai = RandomAI(seed=0)
    move = ai.select_move(s)
    assert move in s.legal_moves()


def test_random_ai_is_seeded_deterministic():
    s = GameState()
    ai1 = RandomAI(seed=42)
    ai2 = RandomAI(seed=42)
    assert ai1.select_move(s) == ai2.select_move(s)


def test_random_ai_raises_when_no_legal_moves():
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.BLACK
    ai = RandomAI()
    with pytest.raises(ValueError):
        ai.select_move(s)


# --- GreedyAI ---

def test_greedy_picks_max_flips():
    s = GameState()
    ai = GreedyAI()
    move = ai.select_move(s)
    chosen = len(flips_for(s.board, move, s.current))
    for m in s.legal_moves():
        assert chosen >= len(flips_for(s.board, m, s.current))


def test_greedy_returns_legal_move():
    s = GameState()
    ai = GreedyAI()
    assert ai.select_move(s) in s.legal_moves()


# --- MinimaxAI ---

def test_minimax_returns_legal_move():
    s = GameState()
    ai = MinimaxAI(depth=2)
    assert ai.select_move(s) in s.legal_moves()


def test_minimax_depth_1_picks_best_immediate():
    s = GameState()
    ai = MinimaxAI(depth=1)
    move = ai.select_move(s)
    assert move in s.legal_moves()


def test_minimax_raises_with_no_legal_moves():
    s = GameState()
    for r in range(s.board.size):
        for c in range(s.board.size):
            s.board[r, c] = Color.BLACK
    ai = MinimaxAI(depth=2)
    with pytest.raises(ValueError):
        ai.select_move(s)


# --- AlphaBetaAI + Minimax parity ---

def test_alphabeta_returns_legal_move():
    s = GameState()
    ai = AlphaBetaAI(depth=3)
    assert ai.select_move(s) in s.legal_moves()


def test_minimax_and_alphabeta_agree_on_initial_position():
    s = GameState()
    mm = MinimaxAI(depth=3)
    ab = AlphaBetaAI(depth=3)
    assert mm.select_move(s) == ab.select_move(s)


def test_minimax_and_alphabeta_agree_after_few_plays():
    s = GameState()
    s.play(s.legal_moves()[0])
    s.play(s.legal_moves()[0])
    mm = MinimaxAI(depth=3)
    ab = AlphaBetaAI(depth=3)
    assert mm.select_move(s) == ab.select_move(s)

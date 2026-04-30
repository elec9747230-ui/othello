import random

from othello.ai.base import Strategy
from othello.core.board import Move
from othello.core.game import GameState


class RandomAI(Strategy):
    name = "Random"

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("RandomAI: no legal moves available")
        return self._rng.choice(moves)

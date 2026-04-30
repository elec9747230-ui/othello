from othello.ai.base import Strategy
from othello.core.board import Move
from othello.core.game import GameState
from othello.core.rules import flips_for


class GreedyAI(Strategy):
    name = "Greedy"

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("GreedyAI: no legal moves available")
        return max(moves, key=lambda m: len(flips_for(state.board, m, state.current)))

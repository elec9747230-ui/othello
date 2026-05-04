"""
othello/ai/greedy.py — Greedy (maximum-flip) AI strategy for Othello.

Implements the simplest non-random heuristic: always choose the move that
flips the most opponent discs immediately, with no look-ahead.

This strategy is easy to beat with any positional awareness (e.g. it often
sacrifices corner adjacency for a large immediate flip count), but it plays
noticeably better than a fully random agent and serves as a useful baseline
for evaluating stronger algorithms.

Usage:
  ai = GreedyAI()
  move = ai.select_move(game_state)
"""

from othello.ai.base import Strategy
from othello.core.board import Move
from othello.core.game import GameState
from othello.core.rules import flips_for


class GreedyAI(Strategy):
    """AI player that always maximises the number of immediately flipped discs.

    No search depth — decision is made in O(b) time where b is the branching
    factor (number of legal moves), making it the fastest AI in this module.
    """

    name = "Greedy"

    def select_move(self, state: GameState) -> Move:
        """Return the legal move that flips the most opponent discs right now.

        Uses flips_for() to count the number of discs each candidate move
        would flip, then returns the move with the highest count.
        Ties are broken by the natural ordering of state.legal_moves()
        (row-major, so the top-left candidate wins ties).

        Args:
            state: Current game state.

        Returns:
            The Move that flips the greatest number of discs in one turn.

        Raises:
            ValueError: If there are no legal moves available.
        """
        moves = state.legal_moves()
        if not moves:
            raise ValueError("GreedyAI: no legal moves available")

        # max() with a key function selects the move with the largest flip
        # count.  len() on the flip list gives the number of discs captured.
        return max(moves, key=lambda m: len(flips_for(state.board, m, state.current)))

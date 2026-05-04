"""
othello/ai/random_ai.py — Randomly-playing AI strategy for Othello.

Implements the weakest possible AI: selects a uniformly random legal move
each turn.  Useful as a baseline opponent and for automated testing where
determinism is important (pass a fixed seed).

Usage:
  ai = RandomAI()          # non-deterministic
  ai = RandomAI(seed=42)   # deterministic / reproducible
  move = ai.select_move(game_state)
"""

import random

from othello.ai.base import Strategy
from othello.core.board import Move
from othello.core.game import GameState


class RandomAI(Strategy):
    """AI player that picks a uniformly random legal move each turn.

    Uses an isolated random.Random instance so that the RandomAI's choices
    do not affect (and are not affected by) any other random state in the
    program.  This also makes seeding for reproducible tests straightforward.

    Attributes:
        _rng: Private random.Random instance used for all selections.
    """

    name = "Random"

    def __init__(self, seed: int | None = None):
        """Initialise the AI with an optional random seed.

        Args:
            seed: Seed value passed to random.Random.  Pass an integer for
                  reproducible move sequences (useful in tests); omit or pass
                  None for non-deterministic behaviour.
        """
        # Using a private Random instance isolates this AI from global state.
        self._rng = random.Random(seed)

    def select_move(self, state: GameState) -> Move:
        """Return a uniformly random legal move for the current player.

        Args:
            state: Current game state.

        Returns:
            A randomly chosen Move from state.legal_moves().

        Raises:
            ValueError: If there are no legal moves available.
        """
        moves = state.legal_moves()
        if not moves:
            raise ValueError("RandomAI: no legal moves available")

        # random.Random.choice() picks one element with equal probability.
        return self._rng.choice(moves)

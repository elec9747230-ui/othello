"""
othello/ai/base.py — Abstract base class for all AI strategies.

Defines the Strategy interface that every AI player must implement.
Using an ABC enforces the contract at import time and allows the UI to
treat all AI implementations uniformly (duck typing would also work, but
the ABC makes the intention explicit and catches missing implementations
early).
"""

from abc import ABC, abstractmethod

from othello.core.board import Move
from othello.core.game import GameState


class Strategy(ABC):
    """Abstract interface for an Othello move-selection algorithm.

    Every concrete AI class (RandomAI, GreedyAI, MinimaxAI, AlphaBetaAI)
    inherits from Strategy and implements select_move().

    Class Attributes:
        name: Human-readable display name shown in the UI and logs.
              Subclasses should override this with a descriptive string.
    """

    # Subclasses should override this with a short, descriptive label
    # (e.g. "Alpha-Beta", "Random") that the UI can display.
    name: str = ""

    @abstractmethod
    def select_move(self, state: GameState) -> Move:
        """Choose and return a legal move for the current player.

        The returned Move must be present in state.legal_moves(); returning
        an illegal move will cause rules.apply_move() to raise ValueError.

        Args:
            state: The current game state.  state.current is the player
                   this strategy is acting for.

        Returns:
            A legal Move from state.legal_moves().

        Raises:
            ValueError: If no legal move exists (the caller should check
                        state.legal_moves() before calling this method).
        """

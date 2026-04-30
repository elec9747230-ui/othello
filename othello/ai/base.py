from abc import ABC, abstractmethod

from othello.core.board import Move
from othello.core.game import GameState


class Strategy(ABC):
    name: str = ""

    @abstractmethod
    def select_move(self, state: GameState) -> Move:
        """Return a legal move from `state.legal_moves()`.
        Must raise ValueError if no legal move exists."""

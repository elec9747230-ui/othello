from dataclasses import dataclass

from othello.core.board import Board, Color, Move, PASS
from othello.core.rules import (
    apply_move,
    is_terminal,
    legal_moves,
    score,
    winner,
)


@dataclass
class HistoryEntry:
    board_before: Board
    color_to_move: Color
    move: Move


class GameState:
    def __init__(self, size: int = 8):
        self.board: Board = Board(size)
        self.current: Color = Color.BLACK
        self.history: list[HistoryEntry] = []

    def legal_moves(self) -> list[Move]:
        return legal_moves(self.board, self.current)

    def must_pass(self) -> bool:
        return (
            not legal_moves(self.board, self.current)
            and bool(legal_moves(self.board, self.current.opponent()))
        )

    def play(self, move: Move) -> None:
        if move.is_pass:
            if not self.must_pass():
                raise ValueError("PASS is only legal when the current player has no moves")
            self.history.append(HistoryEntry(self.board.copy(), self.current, move))
            self.current = self.current.opponent()
            return
        self.history.append(HistoryEntry(self.board.copy(), self.current, move))
        self.board = apply_move(self.board, move, self.current)
        self.current = self.current.opponent()
        # Auto-pass: opponent has no moves but we still do
        if (
            not legal_moves(self.board, self.current)
            and legal_moves(self.board, self.current.opponent())
        ):
            self.history.append(HistoryEntry(self.board.copy(), self.current, PASS))
            self.current = self.current.opponent()

    def undo(self) -> None:
        if not self.history:
            raise IndexError("No history to undo")
        entry = self.history.pop()
        while entry.move.is_pass and self.history:
            entry = self.history.pop()
        self.board = entry.board_before
        self.current = entry.color_to_move

    def score(self) -> tuple[int, int]:
        return score(self.board)

    def winner(self) -> Color | None:
        return winner(self.board)

    def is_over(self) -> bool:
        return is_terminal(self.board)

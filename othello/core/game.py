"""
othello/core/game.py — High-level game-state management for Othello.

Wraps the stateless rule functions in othello.core.rules with a mutable
GameState class that tracks turn order, move history, and handles the
special-case rules for passing.

Classes:
  HistoryEntry  — one snapshot in the undo stack
  GameState     — the main game controller used by the UI and AI
"""

from dataclasses import dataclass

from othello.core.board import Board, Color, Move, PASS
from othello.core.rules import (
    apply_move,
    is_terminal,
    legal_moves,
    score,
    winner,
)


# ---------------------------------------------------------------------------
# HistoryEntry
# ---------------------------------------------------------------------------

@dataclass
class HistoryEntry:
    """A single undo-stack record captured before each move is applied.

    Storing the full board snapshot (rather than just the move) makes undo
    O(1) — we simply restore the snapshot rather than reversing flips.

    Attributes:
        board_before:   Deep copy of the board taken *before* the move.
        color_to_move:  The player who was about to move.
        move:           The move that was actually played (may be PASS).
    """

    board_before: Board
    color_to_move: Color
    move: Move


# ---------------------------------------------------------------------------
# GameState
# ---------------------------------------------------------------------------

class GameState:
    """Mutable snapshot of an ongoing Othello game.

    Responsibilities:
      - Tracks whose turn it is (current).
      - Delegates legality checking / board mutation to the rules module.
      - Records a full undo history.
      - Automatically handles auto-pass: if after a move the opponent has
        no legal placements, the turn skips back to the original player
        without requiring the opponent to call play(PASS) explicitly.

    Attributes:
        board:   The live Board object.
        current: The Color of the player who must move next.
        history: Stack of HistoryEntry objects (oldest first).
    """

    def __init__(self, size: int = 8):
        """Initialise a new game with an empty history.

        Args:
            size: Board side length passed directly to Board(); must be even
                  and >= 4.
        """
        self.board: Board = Board(size)
        # Black moves first per standard Othello rules.
        self.current: Color = Color.BLACK
        self.history: list[HistoryEntry] = []

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    def legal_moves(self) -> list[Move]:
        """Return all legal placements for the current player.

        Delegates to rules.legal_moves so callers need not import that
        module directly.

        Returns:
            A (possibly empty) list of Move objects.
        """
        return legal_moves(self.board, self.current)

    def must_pass(self) -> bool:
        """Return True when the current player has no moves but the opponent does.

        A pass is only forced when there is no legal placement AND the
        opponent still has at least one.  When BOTH players are out of
        moves the game is over (is_over() returns True).

        Returns:
            True if the current player must pass; False otherwise.
        """
        return (
            not legal_moves(self.board, self.current)
            and bool(legal_moves(self.board, self.current.opponent()))
        )

    # ------------------------------------------------------------------
    # Mutating methods
    # ------------------------------------------------------------------

    def play(self, move: Move) -> None:
        """Apply `move` for the current player and advance the turn.

        Handles two cases:
        1. Normal placement — places the disc, flips opponent discs, and
           switches the active player.
        2. PASS sentinel — only legal when must_pass() is True; simply
           switches the active player without touching the board.

        After a normal placement, checks whether the new current player
        (the opponent) has any moves.  If not, but the original player
        does, an auto-pass entry is injected into history and the turn
        reverts, so the human / AI is never stuck waiting for an auto-pass
        to be explicitly submitted.

        Args:
            move: The Move to apply, or PASS.

        Raises:
            ValueError: If move is PASS but must_pass() is False, or if
                        move is a placement that flips no discs.
        """
        if move.is_pass:
            # A pass is only legal when the current player cannot place.
            if not self.must_pass():
                raise ValueError("PASS is only legal when the current player has no moves")
            # Record the pass so undo can restore state correctly.
            self.history.append(HistoryEntry(self.board.copy(), self.current, move))
            self.current = self.current.opponent()
            return

        # --- Normal placement ---

        # Snapshot *before* modifying the board so undo can restore it.
        self.history.append(HistoryEntry(self.board.copy(), self.current, move))

        # apply_move returns a *new* Board; does not mutate self.board.
        self.board = apply_move(self.board, move, self.current)

        # Switch to the opponent's turn.
        self.current = self.current.opponent()

        # Auto-pass: if the new current player has no moves but the previous
        # player does, skip the current player's turn automatically.
        if (
            not legal_moves(self.board, self.current)
            and legal_moves(self.board, self.current.opponent())
        ):
            # Record the auto-pass so undo restores the correct state.
            self.history.append(HistoryEntry(self.board.copy(), self.current, PASS))
            self.current = self.current.opponent()

    def undo(self) -> None:
        """Revert to the board state before the most recent non-pass move.

        Pops history entries until a non-pass move is found, then restores
        the board and active player from that entry's board_before snapshot.
        If the history contains only pass entries, pops them all and returns
        to the earliest recorded state.

        Raises:
            IndexError: If the history is empty and there is nothing to undo.
        """
        if not self.history:
            raise IndexError("No history to undo")

        # Pop the top entry; if it is a pass, keep popping until we find a
        # real move or exhaust the stack.
        entry = self.history.pop()
        while entry.move.is_pass and self.history:
            entry = self.history.pop()

        # Restore the board and turn to the snapshot captured before that move.
        self.board = entry.board_before
        self.current = entry.color_to_move

    # ------------------------------------------------------------------
    # Outcome query methods
    # ------------------------------------------------------------------

    def score(self) -> tuple[int, int]:
        """Return (black_count, white_count) for the current board.

        Returns:
            Tuple of (black discs, white discs).
        """
        return score(self.board)

    def winner(self) -> Color | None:
        """Return the winning Color, or None for a draw.

        Returns:
            Color.BLACK, Color.WHITE, or None if the disc counts are tied.
        """
        return winner(self.board)

    def is_over(self) -> bool:
        """Return True when neither player can make any further move.

        Returns:
            True if the game is in a terminal state; False otherwise.
        """
        return is_terminal(self.board)

"""
othello/core/board.py — Fundamental data types for the Othello board.

Defines:
  Color   — enum representing a cell's occupant (EMPTY / BLACK / WHITE)
  Move    — immutable value object representing a placement or a pass
  PASS    — singleton sentinel for a forced pass
  Board   — mutable 2-D grid of Color values with the standard opening setup
"""

from dataclasses import dataclass
from enum import Enum
from typing import Iterator


# ---------------------------------------------------------------------------
# Color
# ---------------------------------------------------------------------------

class Color(Enum):
    """The three possible states of a board cell.

    EMPTY = 0  — unoccupied cell
    BLACK = 1  — cell occupied by a black disc (moves first)
    WHITE = 2  — cell occupied by a white disc
    """

    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def opponent(self) -> "Color":
        """Return the opposing player's color.

        BLACK  →  WHITE
        WHITE  →  BLACK
        EMPTY  →  raises ValueError (EMPTY has no opponent)

        Used throughout the rules and AI to switch the active player.
        """
        if self is Color.BLACK:
            return Color.WHITE
        if self is Color.WHITE:
            return Color.BLACK
        raise ValueError("Color.EMPTY has no opponent")


# ---------------------------------------------------------------------------
# Move
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Move:
    """An immutable (row, col) board position, or a pass sentinel.

    Frozen dataclass so Move instances can be used as dict keys / set members.

    Attributes:
        row: Zero-based row index (0 = top row).
        col: Zero-based column index (0 = leftmost column).

    A move with row == -1 and col == -1 represents a forced pass (no legal
    placements available).  Use the PASS constant rather than constructing
    this directly.
    """

    row: int
    col: int

    @property
    def is_pass(self) -> bool:
        """True when this move represents a pass rather than a board placement.

        A pass is encoded as Move(-1, -1) to keep the type uniform.
        """
        return self.row == -1 and self.col == -1


# Singleton constant so callers can write `PASS` instead of `Move(-1, -1)`.
PASS: Move = Move(-1, -1)


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------

class Board:
    """A square grid of Color values representing the Othello game board.

    The board is initialised with the standard 4-disc opening position:
      - White discs at (m-1, m-1) and (m, m)
      - Black discs at (m-1, m) and (m, m-1)
    where m = size // 2 (the centre of the grid).

    Cell access uses __getitem__ / __setitem__ with (row, col) tuples so the
    calling code can write `board[r, c]` without an extra method call.

    Attributes:
        size: Side length of the square board (must be even and >= 4).
    """

    def __init__(self, size: int = 8):
        """Initialise a fresh board with the standard Othello opening.

        Args:
            size: Board side length.  Must be an even integer >= 4.

        Raises:
            ValueError: If size is odd or less than 4.
        """
        if size < 4 or size % 2 != 0:
            raise ValueError(f"Board size must be even and >= 4, got {size}")

        self.size = size

        # Allocate a 2-D list of Color.EMPTY values.
        self._cells: list[list[Color]] = [
            [Color.EMPTY] * size for _ in range(size)
        ]

        # Place the four starting discs at the centre of the board.
        # m is the midpoint index; the four cells around (m-1, m-1) form a
        # 2×2 square at the board's centre.
        m = size // 2
        self._cells[m - 1][m - 1] = Color.WHITE  # top-left of centre block
        self._cells[m][m] = Color.WHITE            # bottom-right of centre block
        self._cells[m - 1][m] = Color.BLACK        # top-right of centre block
        self._cells[m][m - 1] = Color.BLACK        # bottom-left of centre block

    def __getitem__(self, rc: tuple[int, int]) -> Color:
        """Return the Color at cell (row, col).

        Allows the clean syntax:  color = board[r, c]

        Args:
            rc: A (row, col) tuple.

        Returns:
            The Color stored at that position.
        """
        r, c = rc
        return self._cells[r][c]

    def __setitem__(self, rc: tuple[int, int], color: Color) -> None:
        """Set the Color at cell (row, col).

        Allows the clean syntax:  board[r, c] = Color.BLACK

        Args:
            rc:    A (row, col) tuple.
            color: The Color to store.
        """
        r, c = rc
        self._cells[r][c] = color

    def copy(self) -> "Board":
        """Return a deep copy of this board.

        Uses __new__ to bypass __init__ (which would reset cells to the
        opening position) and then manually copies the cell matrix.

        Returns:
            A new Board with identical size and cell values.
        """
        new = Board.__new__(Board)  # allocate without calling __init__
        new.size = self.size
        # Shallow-copy each row list so mutations in the original do not
        # affect the copy and vice-versa.
        new._cells = [row[:] for row in self._cells]
        return new

    def cells(self) -> Iterator[tuple[int, int, Color]]:
        """Yield every (row, col, Color) triple in row-major order.

        Convenient for iterating over all cells without index management.
        Used by the score counter, evaluation function, and board renderer.

        Yields:
            Tuples of (row_index, col_index, Color).
        """
        for r in range(self.size):
            for c in range(self.size):
                yield (r, c, self._cells[r][c])

    def in_bounds(self, r: int, c: int) -> bool:
        """Return True when (r, c) is a valid cell index on this board.

        Used to terminate ray-casting loops in the rules module before
        indexing out of range.

        Args:
            r: Row index to check.
            c: Column index to check.

        Returns:
            True if both indices are within [0, size).
        """
        return 0 <= r < self.size and 0 <= c < self.size

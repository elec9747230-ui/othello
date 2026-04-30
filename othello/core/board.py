from dataclasses import dataclass
from enum import Enum


class Color(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def opponent(self) -> "Color":
        if self is Color.BLACK:
            return Color.WHITE
        if self is Color.WHITE:
            return Color.BLACK
        raise ValueError("Color.EMPTY has no opponent")


@dataclass(frozen=True)
class Move:
    row: int
    col: int

    @property
    def is_pass(self) -> bool:
        return self.row == -1 and self.col == -1


PASS: Move = Move(-1, -1)


from typing import Iterator


class Board:
    def __init__(self, size: int = 8):
        if size < 4 or size % 2 != 0:
            raise ValueError(f"Board size must be even and >= 4, got {size}")
        self.size = size
        self._cells: list[list[Color]] = [
            [Color.EMPTY] * size for _ in range(size)
        ]
        m = size // 2
        self._cells[m - 1][m - 1] = Color.WHITE
        self._cells[m][m] = Color.WHITE
        self._cells[m - 1][m] = Color.BLACK
        self._cells[m][m - 1] = Color.BLACK

    def __getitem__(self, rc: tuple[int, int]) -> Color:
        r, c = rc
        return self._cells[r][c]

    def __setitem__(self, rc: tuple[int, int], color: Color) -> None:
        r, c = rc
        self._cells[r][c] = color

    def copy(self) -> "Board":
        new = Board.__new__(Board)
        new.size = self.size
        new._cells = [row[:] for row in self._cells]
        return new

    def cells(self) -> Iterator[tuple[int, int, Color]]:
        for r in range(self.size):
            for c in range(self.size):
                yield (r, c, self._cells[r][c])

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size

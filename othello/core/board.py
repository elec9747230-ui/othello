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

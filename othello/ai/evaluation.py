from othello.core.board import Board, Color
from othello.core.rules import legal_moves, score

WEIGHTS_8X8: list[list[int]] = [
    [100, -25,  10,   5,   5,  10, -25, 100],
    [-25, -50,   1,   1,   1,   1, -50, -25],
    [ 10,   1,   5,   2,   2,   5,   1,  10],
    [  5,   1,   2,   1,   1,   2,   1,   5],
    [  5,   1,   2,   1,   1,   2,   1,   5],
    [ 10,   1,   5,   2,   2,   5,   1,  10],
    [-25, -50,   1,   1,   1,   1, -50, -25],
    [100, -25,  10,   5,   5,  10, -25, 100],
]


def _generic_value(size: int, r: int, c: int) -> int:
    is_corner = r in (0, size - 1) and c in (0, size - 1)
    is_edge = r in (0, size - 1) or c in (0, size - 1)
    if is_corner:
        return 30
    if is_edge:
        return 5
    return 1


def _terminal_eval(board: Board, color: Color) -> int:
    b, w = score(board)
    diff = b - w
    sign = 1 if color is Color.BLACK else -1
    return sign * diff * 10000


def evaluate(board: Board, color: Color) -> int:
    if not legal_moves(board, Color.BLACK) and not legal_moves(board, Color.WHITE):
        return _terminal_eval(board, color)

    use_weights = (board.size == 8)
    total = 0
    for r, c, cell in board.cells():
        if cell is Color.EMPTY:
            continue
        v = WEIGHTS_8X8[r][c] if use_weights else _generic_value(board.size, r, c)
        if cell is color:
            total += v
        else:
            total -= v
    return total

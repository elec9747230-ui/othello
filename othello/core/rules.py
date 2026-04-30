from othello.core.board import Board, Color, Move

DIRECTIONS: list[tuple[int, int]] = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


def _flips_in_direction(
    board: Board, r: int, c: int, dr: int, dc: int, color: Color
) -> list[tuple[int, int]]:
    opp = color.opponent()
    captured: list[tuple[int, int]] = []
    rr, cc = r + dr, c + dc
    while board.in_bounds(rr, cc) and board[rr, cc] is opp:
        captured.append((rr, cc))
        rr += dr
        cc += dc
    if board.in_bounds(rr, cc) and board[rr, cc] is color and captured:
        return captured
    return []


def flips_for(board: Board, move: Move, color: Color) -> list[tuple[int, int]]:
    if not board.in_bounds(move.row, move.col):
        return []
    if board[move.row, move.col] is not Color.EMPTY:
        return []
    all_flips: list[tuple[int, int]] = []
    for dr, dc in DIRECTIONS:
        all_flips.extend(
            _flips_in_direction(board, move.row, move.col, dr, dc, color)
        )
    return all_flips


def legal_moves(board: Board, color: Color) -> list[Move]:
    moves: list[Move] = []
    for r in range(board.size):
        for c in range(board.size):
            if board[r, c] is Color.EMPTY:
                m = Move(r, c)
                if flips_for(board, m, color):
                    moves.append(m)
    return moves

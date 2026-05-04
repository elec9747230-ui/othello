"""
othello/ai/evaluation.py — Static board evaluation for Othello AI.

Provides the evaluate() function used by MinimaxAI and AlphaBetaAI to
score a non-terminal board position from the perspective of a given player.

Evaluation strategy
-------------------
For an 8×8 board the function uses a hand-crafted positional weight table
(WEIGHTS_8X8) that assigns high value to corners (hard to flip), negative
value to cells adjacent to corners (handing the opponent a corner), and
moderate value to edges and interior cells.

For other board sizes a simpler generic heuristic assigns fixed weights
based on corner / edge / interior classification.

Terminal positions are scored by disc difference (multiplied by 10 000
to ensure they always dominate heuristic evaluations).
"""

from othello.core.board import Board, Color
from othello.core.rules import legal_moves, score


# ---------------------------------------------------------------------------
# 8×8 positional weight table
# ---------------------------------------------------------------------------

# Each entry is the strategic value of owning that cell.
# Negative values (cells adjacent to corners) indicate positions that are
# dangerous to occupy early because they can hand the opponent a corner.
#
#  100  = corner        — permanently stable; highest priority
#  -25  = X-square      — diagonally adjacent to corner; very dangerous
#  -50  = C-square      — edge-adjacent to corner; also dangerous
#   10  = stable edge   — non-corner edge cells; moderate value
#    5  = near-edge     — cells one step inside an edge
#    2  = mid-interior  — relatively neutral interior cells
#    1  = inner cell    — lowest priority
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


# ---------------------------------------------------------------------------
# Generic weight function (non-8×8 boards)
# ---------------------------------------------------------------------------

def _generic_value(size: int, r: int, c: int) -> int:
    """Return a positional weight for boards other than 8×8.

    A simplified three-tier scheme:
      corner  →  30
      edge    →   5
      interior→   1

    Args:
        size: Board side length.
        r, c: Cell coordinates.

    Returns:
        An integer positional weight.
    """
    is_corner = r in (0, size - 1) and c in (0, size - 1)
    is_edge   = r in (0, size - 1) or  c in (0, size - 1)
    if is_corner:
        return 30
    if is_edge:
        return 5
    return 1


# ---------------------------------------------------------------------------
# Terminal evaluation
# ---------------------------------------------------------------------------

def _terminal_eval(board: Board, color: Color) -> int:
    """Score a terminal (game-over) board from `color`'s perspective.

    Uses the final disc difference scaled by 10 000, so any terminal win
    (or loss) dominates all heuristic evaluations during search.

    Args:
        board: The terminal board.
        color: The AI player whose score we maximise.

    Returns:
        A large positive integer if `color` wins, large negative if it
        loses, or 0 for an exact draw.
    """
    b, w = score(board)
    diff = b - w  # positive if BLACK leads, negative if WHITE leads

    # Flip the sign for WHITE so the function always returns a value that
    # is positive for a win by `color` and negative for a loss.
    sign = 1 if color is Color.BLACK else -1
    return sign * diff * 10_000


# ---------------------------------------------------------------------------
# Main evaluation function
# ---------------------------------------------------------------------------

def evaluate(board: Board, color: Color) -> int:
    """Score `board` from the perspective of `color`.

    Returns a large value for positions that are good for `color` and a
    small (negative) value for positions that are bad.  The scale is:
      ±10 000+  → terminal win / loss
      ±hundreds → typical mid-game position

    Algorithm:
      1. If the position is terminal, delegate to _terminal_eval.
      2. Otherwise, sum up positional weights for all occupied cells,
         adding the weight when the disc belongs to `color` and
         subtracting it when the disc belongs to the opponent.

    Args:
        board: The board to evaluate.
        color: The AI player whose interests we maximise.

    Returns:
        An integer score; higher is better for `color`.
    """
    # Check for game-over first — terminal scores always dominate heuristics.
    if not legal_moves(board, Color.BLACK) and not legal_moves(board, Color.WHITE):
        return _terminal_eval(board, color)

    # Choose the appropriate weight table based on board size.
    use_weights = (board.size == 8)

    total = 0
    for r, c, cell in board.cells():
        if cell is Color.EMPTY:
            continue  # empty cells contribute nothing to the score

        # Look up this cell's strategic value.
        v = WEIGHTS_8X8[r][c] if use_weights else _generic_value(board.size, r, c)

        # Add to total if it is our disc; subtract if it belongs to the opponent.
        if cell is color:
            total += v
        else:
            total -= v

    return total

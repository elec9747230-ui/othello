"""
othello/core/rules.py — Pure game-rule functions for Othello.

All functions are stateless: they accept a Board (and optionally a Color or
Move) and return a result without mutating any input.  This makes them safe
to call from AI search trees where the same board position is visited many
times.

Public API:
  DIRECTIONS     — the 8 compass directions used for ray-casting
  flips_for      — list of cells that would be flipped by a given move
  legal_moves    — all valid placements for a given player
  apply_move     — produce a new Board after a player places a disc
  score          — count (black_discs, white_discs) on the board
  is_terminal    — True when neither player has any legal move
  winner         — Color of the winner, or None for a draw
"""

from othello.core.board import Board, Color, Move

# ---------------------------------------------------------------------------
# Direction vectors
# ---------------------------------------------------------------------------

# The 8 cardinal + diagonal directions on the grid, expressed as (dr, dc)
# offsets.  Ray-casting walks from a candidate cell in each direction to
# detect opponent discs bracketed by the player's own disc.
DIRECTIONS: list[tuple[int, int]] = [
    (-1, -1), (-1, 0), (-1, 1),   # NW, N, NE
    (0,  -1),          (0,  1),   # W,     E
    (1,  -1),  (1, 0), (1,  1),   # SW, S, SE
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _flips_in_direction(
    board: Board, r: int, c: int, dr: int, dc: int, color: Color
) -> list[tuple[int, int]]:
    """Return cells that would be flipped along a single ray.

    Starting from the cell immediately adjacent to (r, c) in the direction
    (dr, dc), walks outward as long as it sees the opponent's discs.  If the
    ray terminates on the current player's own disc AND at least one opponent
    disc was crossed, all those opponent cells are returned; otherwise an
    empty list is returned (no capture in this direction).

    Args:
        board:  The current board state.
        r, c:   The cell where the player is considering placing a disc.
        dr, dc: One of the 8 direction vectors.
        color:  The placing player's color.

    Returns:
        A list of (row, col) cells that would be flipped, or [] if no
        capture occurs in this direction.
    """
    opp = color.opponent()
    captured: list[tuple[int, int]] = []

    # Advance one step before the loop starts (we never flip the origin cell).
    rr, cc = r + dr, c + dc

    # Walk while in bounds AND the cell belongs to the opponent.
    while board.in_bounds(rr, cc) and board[rr, cc] is opp:
        captured.append((rr, cc))
        rr += dr
        cc += dc

    # The capture is only valid when the ray ends on our own disc
    # AND we crossed at least one opponent disc.
    if board.in_bounds(rr, cc) and board[rr, cc] is color and captured:
        return captured

    # The ray hit an empty cell, went off the board, or had no opponent
    # discs — no capture.
    return []


# ---------------------------------------------------------------------------
# Public rule functions
# ---------------------------------------------------------------------------

def flips_for(board: Board, move: Move, color: Color) -> list[tuple[int, int]]:
    """Return all opponent cells that would be flipped by placing `color` at `move`.

    A move is legal in Othello if and only if it flips at least one opponent
    disc.  Placing at an occupied cell or outside the board is always illegal.

    Args:
        board: Current board state.
        move:  The proposed placement.
        color: The player making the move.

    Returns:
        A (possibly empty) list of (row, col) cells that would be flipped.
        An empty list means the move is illegal.
    """
    # Reject out-of-bounds positions immediately.
    if not board.in_bounds(move.row, move.col):
        return []

    # A disc can only be placed on an empty cell.
    if board[move.row, move.col] is not Color.EMPTY:
        return []

    # Collect flips from all 8 directions and return the union.
    all_flips: list[tuple[int, int]] = []
    for dr, dc in DIRECTIONS:
        all_flips.extend(
            _flips_in_direction(board, move.row, move.col, dr, dc, color)
        )
    return all_flips


def legal_moves(board: Board, color: Color) -> list[Move]:
    """Return all legal placements available to `color` on `board`.

    Iterates over every empty cell and checks whether placing there would
    flip at least one opponent disc.  The order is row-major (top-to-bottom,
    left-to-right), which produces a consistent move ordering for AI search.

    Args:
        board: Current board state.
        color: The player whose legal moves we want.

    Returns:
        A list of Move objects.  Empty list means the player must pass.
    """
    moves: list[Move] = []
    for r in range(board.size):
        for c in range(board.size):
            # Only consider empty cells — occupied cells can never be placed on.
            if board[r, c] is Color.EMPTY:
                m = Move(r, c)
                # A move is legal iff it flips at least one disc.
                if flips_for(board, m, color):
                    moves.append(m)
    return moves


def apply_move(board: Board, move: Move, color: Color) -> Board:
    """Return a new Board that results from `color` placing at `move`.

    Does NOT modify `board`; creates and returns a copy with the placed disc
    and all flipped discs updated.

    Args:
        board: The board before the move.
        move:  Where to place the disc.
        color: The player making the move.

    Returns:
        A new Board reflecting the placement and all resulting flips.

    Raises:
        ValueError: If the move is illegal (flips no discs).
    """
    flips = flips_for(board, move, color)
    if not flips:
        raise ValueError(f"Illegal move {move} for {color.name}")

    # Work on a copy so the original board is never mutated.
    new_board = board.copy()

    # Place the new disc at the chosen cell.
    new_board[move.row, move.col] = color

    # Flip all captured opponent discs to the current player's color.
    for r, c in flips:
        new_board[r, c] = color

    return new_board


def score(board: Board) -> tuple[int, int]:
    """Count and return (black_disc_count, white_disc_count).

    Iterates over every cell exactly once.  Used for both the in-game score
    display and the terminal evaluation in the AI.

    Args:
        board: The board to score.

    Returns:
        A (black, white) tuple of non-negative integers.
    """
    black = white = 0
    for _, _, c in board.cells():
        if c is Color.BLACK:
            black += 1
        elif c is Color.WHITE:
            white += 1
    return black, white


def is_terminal(board: Board) -> bool:
    """Return True when the game is over (neither player can move).

    The game ends when both BLACK and WHITE have no legal placements.  This
    can happen before the board is full if both players are forced to pass.

    Args:
        board: The board to check.

    Returns:
        True if the position is terminal; False if at least one player can
        still make a move.
    """
    return not legal_moves(board, Color.BLACK) and not legal_moves(board, Color.WHITE)


def winner(board: Board) -> Color | None:
    """Return the winning Color, or None for a draw.

    Only meaningful after is_terminal() returns True.  Does not verify
    that the game is actually over — calling on a mid-game board simply
    returns whichever side currently has more discs.

    Args:
        board: The (ideally terminal) board to evaluate.

    Returns:
        Color.BLACK if black has more discs, Color.WHITE if white has more,
        or None if the disc counts are equal (a draw).
    """
    b, w = score(board)
    if b > w:
        return Color.BLACK
    if w > b:
        return Color.WHITE
    return None  # draw

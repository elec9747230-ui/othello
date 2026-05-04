"""
othello/ai/minimax.py — Minimax AI strategy for Othello.

Implements the classic minimax adversarial search algorithm with no pruning.
MinimaxAI explores the full game tree up to a fixed depth, assuming the
opponent always makes the worst possible move for the current player.

Performance note:
  Minimax with depth 3 examines roughly O(b^3) nodes where b ≈ 10 (average
  branching factor for Othello), so about 1 000 nodes per turn — fast enough
  for interactive play.  For deeper search, prefer AlphaBetaAI which prunes
  large portions of the same tree.

Usage:
  ai = MinimaxAI(depth=3)
  move = ai.select_move(game_state)
"""

from othello.ai.base import Strategy
from othello.ai.evaluation import evaluate
from othello.core.board import Board, Color, Move
from othello.core.game import GameState
from othello.core.rules import apply_move, legal_moves

# Sentinel values for best/worst possible scores during search.
INF = float("inf")


class MinimaxAI(Strategy):
    """AI player using the minimax search algorithm.

    Explores every possible game sequence up to `depth` half-moves (plies)
    and selects the root move that leads to the highest-scoring leaf node
    when both players play optimally.

    Attributes:
        depth: Number of plies (half-moves) to search ahead.
    """

    name = "Minimax"

    def __init__(self, depth: int = 3):
        """Create a MinimaxAI with the given search depth.

        Args:
            depth: How many half-moves to look ahead.  Larger values
                   produce stronger play but increase computation time
                   exponentially.
        """
        self.depth = depth

    def select_move(self, state: GameState) -> Move:
        """Choose the best move for the current player using minimax.

        Iterates over all legal moves, simulates each one, then calls
        _search() to evaluate the resulting position.  Returns the move
        with the highest minimax value.

        Args:
            state: Current game state; state.current is the AI's color.

        Returns:
            The Move with the highest minimax evaluation.

        Raises:
            ValueError: If there are no legal moves available.
        """
        moves = state.legal_moves()
        if not moves:
            raise ValueError("MinimaxAI: no legal moves available")

        root_color = state.current  # the color we are maximising for

        best_move = moves[0]  # fallback in case all moves evaluate equally
        best_val = -INF

        for m in moves:
            # Simulate placing this disc and evaluate the resulting board.
            new_board = apply_move(state.board, m, root_color)

            # It is now the opponent's turn — search one ply deeper.
            val = self._search(new_board, root_color.opponent(), self.depth - 1, root_color)

            if val > best_val:
                best_val = val
                best_move = m

        return best_move

    def _search(self, board: Board, to_move: Color, depth: int, root_color: Color) -> float:
        """Recursively evaluate `board` using minimax.

        At every node:
          - If depth == 0 or the position is terminal: return the heuristic
            evaluation from root_color's perspective.
          - If to_move == root_color (maximising node): return the maximum
            child value.
          - Otherwise (minimising node): return the minimum child value.
          - If to_move has no moves but the opponent does, skip to_move's
            turn by passing (recursing with the opponent and depth - 1).

        Args:
            board:      The board position to evaluate.
            to_move:    The player whose turn it is at this node.
            depth:      Remaining search depth (in plies).
            root_color: The AI's color (the player we ultimately maximise).

        Returns:
            A float evaluation score; higher is better for root_color.
        """
        # Base case: leaf node — return static evaluation.
        if depth == 0:
            return evaluate(board, root_color)

        moves = legal_moves(board, to_move)

        if not moves:
            # No moves for to_move; check if the game is truly over.
            opp_moves = legal_moves(board, to_move.opponent())
            if not opp_moves:
                # Both players have no moves — terminal position.
                return evaluate(board, root_color)

            # Only to_move is stuck; the opponent can still play, so skip
            # this player's turn (pass) and recurse with one less ply.
            return self._search(board, to_move.opponent(), depth - 1, root_color)

        if to_move is root_color:
            # --- Maximising node: pick the child with the highest score ---
            best = -INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move),
                    to_move.opponent(),
                    depth - 1,
                    root_color,
                )
                if v > best:
                    best = v
            return best
        else:
            # --- Minimising node: pick the child with the lowest score ---
            best = INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move),
                    to_move.opponent(),
                    depth - 1,
                    root_color,
                )
                if v < best:
                    best = v
            return best

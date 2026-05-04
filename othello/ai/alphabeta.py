"""
othello/ai/alphabeta.py — Alpha-Beta pruning AI strategy for Othello.

Implements the Alpha-Beta pruning enhancement of the minimax algorithm.
Alpha-Beta achieves the same result as plain minimax but prunes branches
that cannot possibly affect the final decision, reducing the effective
branching factor and allowing much deeper searches in the same time budget.

Key concepts:
  alpha — the best score the maximising player (root_color) has found so far
          along the current path.  Any node that would give a score <= alpha
          can be pruned from the minimiser's perspective.
  beta  — the best score the minimising player (opponent) has found so far.
          Any node that would give a score >= beta can be pruned from the
          maximiser's perspective.

When alpha >= beta at any node (a "cutoff"), the subtree rooted there is
guaranteed to be irrelevant to the final decision and is skipped.

With good move ordering, Alpha-Beta reduces the effective branching factor
from b to approximately sqrt(b), doubling the reachable search depth
compared to plain minimax for the same number of node evaluations.

Usage:
  ai = AlphaBetaAI(depth=5)
  move = ai.select_move(game_state)
"""

from othello.ai.base import Strategy
from othello.ai.evaluation import evaluate
from othello.core.board import Board, Color, Move
from othello.core.game import GameState
from othello.core.rules import apply_move, legal_moves

# Positive and negative infinity used as initial alpha/beta bounds.
INF = float("inf")


class AlphaBetaAI(Strategy):
    """AI player using Alpha-Beta pruning search.

    Explores the game tree up to `depth` plies, pruning subtrees that cannot
    change the root decision.  Stronger and faster than MinimaxAI for the
    same depth, and practically much stronger because it can search deeper.

    Attributes:
        depth: Number of plies (half-moves) to search ahead.
    """

    name = "Alpha-Beta"

    def __init__(self, depth: int = 5):
        """Create an AlphaBetaAI with the given search depth.

        Args:
            depth: How many half-moves to look ahead.  A depth of 5 is
                   generally strong enough for casual play on an 8×8 board.
        """
        self.depth = depth

    def select_move(self, state: GameState) -> Move:
        """Choose the best move for the current player using Alpha-Beta search.

        Iterates over all legal moves, simulates each one, and evaluates
        the resulting position with _search().  Maintains alpha-beta bounds
        across the root's children to prune sibling subtrees early.

        Args:
            state: Current game state; state.current is the AI's color.

        Returns:
            The Move with the highest Alpha-Beta evaluation.

        Raises:
            ValueError: If there are no legal moves available.
        """
        moves = state.legal_moves()
        if not moves:
            raise ValueError("AlphaBetaAI: no legal moves available")

        root_color = state.current  # the color we are maximising for
        best_move = moves[0]        # default to first move as a safe fallback
        best_val = -INF

        # Global alpha/beta bounds that span all root children.
        alpha, beta = -INF, INF

        for m in moves:
            # Apply this move on a copy of the board.
            new_board = apply_move(state.board, m, root_color)

            # Evaluate the resulting position from the opponent's perspective
            # (depth - 1 because we just used one ply placing the disc).
            val = self._search(
                new_board, root_color.opponent(), self.depth - 1, alpha, beta, root_color
            )

            if val > best_val:
                best_val = val
                best_move = m

            # Update the global alpha so subsequent root children can be pruned
            # if they can't beat this value.
            alpha = max(alpha, val)

        return best_move

    def _search(
        self,
        board: Board,
        to_move: Color,
        depth: int,
        alpha: float,
        beta: float,
        root_color: Color,
    ) -> float:
        """Recursively evaluate `board` with Alpha-Beta pruning.

        At maximising nodes (to_move == root_color) we try to raise alpha.
        At minimising nodes we try to lower beta.  When alpha >= beta we
        cut off the remaining children — they cannot affect the parent's
        decision.

        Args:
            board:      The board position to evaluate.
            to_move:    The player whose turn it is at this node.
            depth:      Remaining search depth (in plies).
            alpha:      Best score root_color has guaranteed so far (lower
                        bound on the root's value along this path).
            beta:       Best score the opponent has guaranteed so far (upper
                        bound on the root's value along this path).
            root_color: The AI's color (the player we ultimately maximise).

        Returns:
            A float evaluation score; higher is better for root_color.
        """
        # Base case: reached the search horizon — return static evaluation.
        if depth == 0:
            return evaluate(board, root_color)

        moves = legal_moves(board, to_move)

        if not moves:
            # No legal moves for to_move — check whether the game is over.
            opp_moves = legal_moves(board, to_move.opponent())
            if not opp_moves:
                # Both players are stuck — terminal position; evaluate it.
                return evaluate(board, root_color)

            # Only to_move is stuck; the opponent can play, so pass to_move's
            # turn and continue searching.
            return self._search(board, to_move.opponent(), depth - 1, alpha, beta, root_color)

        if to_move is root_color:
            # ---------------------------------------------------------------
            # Maximising node: find the highest-scoring child.
            # We raise alpha as we find better moves; if value >= beta we
            # can stop (the minimiser above would never allow this path).
            # ---------------------------------------------------------------
            value = -INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move),
                    to_move.opponent(),
                    depth - 1,
                    alpha,
                    beta,
                    root_color,
                )
                if v > value:
                    value = v
                if value > alpha:
                    alpha = value     # tighten the lower bound
                if alpha >= beta:
                    break             # beta cut-off: minimiser won't allow this
            return value
        else:
            # ---------------------------------------------------------------
            # Minimising node: find the lowest-scoring child.
            # We lower beta as we find worse-for-root moves; if value <= alpha
            # we can stop (the maximiser above already has a better choice).
            # ---------------------------------------------------------------
            value = INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move),
                    to_move.opponent(),
                    depth - 1,
                    alpha,
                    beta,
                    root_color,
                )
                if v < value:
                    value = v
                if value < beta:
                    beta = value      # tighten the upper bound
                if alpha >= beta:
                    break             # alpha cut-off: maximiser already has better
            return value

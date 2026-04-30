from othello.ai.base import Strategy
from othello.ai.evaluation import evaluate
from othello.core.board import Board, Color, Move
from othello.core.game import GameState
from othello.core.rules import apply_move, legal_moves

INF = float("inf")


class AlphaBetaAI(Strategy):
    name = "Alpha-Beta"

    def __init__(self, depth: int = 5):
        self.depth = depth

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("AlphaBetaAI: no legal moves available")
        root_color = state.current
        best_move = moves[0]
        best_val = -INF
        alpha, beta = -INF, INF
        for m in moves:
            new_board = apply_move(state.board, m, root_color)
            val = self._search(
                new_board, root_color.opponent(), self.depth - 1, alpha, beta, root_color
            )
            if val > best_val:
                best_val = val
                best_move = m
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
        if depth == 0:
            return evaluate(board, root_color)
        moves = legal_moves(board, to_move)
        if not moves:
            opp_moves = legal_moves(board, to_move.opponent())
            if not opp_moves:
                return evaluate(board, root_color)
            return self._search(board, to_move.opponent(), depth - 1, alpha, beta, root_color)
        if to_move is root_color:
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
                    alpha = value
                if alpha >= beta:
                    break
            return value
        else:
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
                    beta = value
                if alpha >= beta:
                    break
            return value

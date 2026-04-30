from othello.ai.base import Strategy
from othello.ai.evaluation import evaluate
from othello.core.board import Board, Color, Move
from othello.core.game import GameState
from othello.core.rules import apply_move, legal_moves

INF = float("inf")


class MinimaxAI(Strategy):
    name = "Minimax"

    def __init__(self, depth: int = 3):
        self.depth = depth

    def select_move(self, state: GameState) -> Move:
        moves = state.legal_moves()
        if not moves:
            raise ValueError("MinimaxAI: no legal moves available")
        root_color = state.current
        best_move = moves[0]
        best_val = -INF
        for m in moves:
            new_board = apply_move(state.board, m, root_color)
            val = self._search(new_board, root_color.opponent(), self.depth - 1, root_color)
            if val > best_val:
                best_val = val
                best_move = m
        return best_move

    def _search(self, board: Board, to_move: Color, depth: int, root_color: Color) -> float:
        if depth == 0:
            return evaluate(board, root_color)
        moves = legal_moves(board, to_move)
        if not moves:
            opp_moves = legal_moves(board, to_move.opponent())
            if not opp_moves:
                return evaluate(board, root_color)
            return self._search(board, to_move.opponent(), depth - 1, root_color)
        if to_move is root_color:
            best = -INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move), to_move.opponent(), depth - 1, root_color
                )
                if v > best:
                    best = v
            return best
        else:
            best = INF
            for m in moves:
                v = self._search(
                    apply_move(board, m, to_move), to_move.opponent(), depth - 1, root_color
                )
                if v < best:
                    best = v
            return best

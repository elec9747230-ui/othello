import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from othello.core.board import Color, Move
from othello.core.game import GameState
from othello.core.rules import flips_for
from othello.persistence import save_game
from othello.ui import sound
from othello.ui.board_view import BoardView


def _move_label(m: Move) -> str:
    if m.is_pass:
        return "pass"
    return f"{chr(ord('a') + m.col)}{m.row + 1}"


def _build_strategy(name: str):
    if name == "random":
        from othello.ai.random_ai import RandomAI
        return RandomAI()
    if name == "greedy":
        from othello.ai.greedy import GreedyAI
        return GreedyAI()
    if name == "minimax":
        from othello.ai.minimax import MinimaxAI
        return MinimaxAI(depth=3)
    if name == "alphabeta":
        from othello.ai.alphabeta import AlphaBetaAI
        return AlphaBetaAI(depth=5)
    raise ValueError(f"Unknown AI: {name}")


class GameScreen(tk.Frame):
    def __init__(self, root: tk.Tk, app, config: dict[str, Any]):
        super().__init__(root)
        self.app = app
        self.config_data = dict(config)
        loaded = self.config_data.pop("_loaded_state", None)
        size = self.config_data.get("size", 8)
        self.state: GameState = loaded if loaded is not None else GameState(size=size)

        self.ai = None
        self.ai_color: Color | None = None
        if self.config_data.get("mode") == "vs_ai":
            self.ai = _build_strategy(self.config_data["ai_difficulty"])
            human = Color[self.config_data.get("human_color", "BLACK")]
            self.ai_color = human.opponent()

        self.board_view = BoardView(self, self.state.board.size, self._on_click)
        self.board_view.pack(side="left", padx=10, pady=10)

        side = ttk.Frame(self)
        side.pack(side="right", fill="y", padx=10, pady=10)

        self.turn_label = ttk.Label(side, text="", font=("Helvetica", 14, "bold"))
        self.turn_label.pack(anchor="w", pady=5)
        self.score_label = ttk.Label(side, text="", font=("Helvetica", 12))
        self.score_label.pack(anchor="w", pady=5)

        ttk.Button(side, text="Undo", command=self._undo).pack(fill="x", pady=2)
        ttk.Button(side, text="Hint", command=self._hint).pack(fill="x", pady=2)
        ttk.Button(side, text="Save", command=self._save).pack(fill="x", pady=2)
        ttk.Button(side, text="Menu", command=app.show_menu).pack(fill="x", pady=2)

        ttk.Label(side, text="History:").pack(anchor="w", pady=(10, 2))
        self.history_text = tk.Text(side, width=24, height=20, state="disabled")
        self.history_text.pack(fill="y", expand=True)

        self._hint_move: Move | None = None
        self._refresh()
        self._maybe_schedule_ai()

    # --- Event handlers ---

    def _on_click(self, row: int, col: int) -> None:
        if self.board_view.is_animating:
            return
        if self.ai is not None and self.state.current is self.ai_color:
            return  # AI's turn — ignore human clicks
        move = Move(row, col)
        if move not in self.state.legal_moves():
            return
        self._play(move)

    def _play(self, move: Move) -> None:
        flips = flips_for(self.state.board, move, self.state.current)
        try:
            self.state.play(move)
        except ValueError:
            return
        sound.play_place()
        self._hint_move = None

        def after_anim() -> None:
            self._refresh()
            if self.state.is_over():
                self._announce_winner()
                return
            self._maybe_schedule_ai()

        self.board_view.animate_move(self.state.board, move, flips, after_anim)
        self._update_status()
        self._update_history()

    def _undo(self) -> None:
        if self.board_view.is_animating:
            return
        if not self.state.history:
            return
        self.state.undo()
        # If vs AI, undo until it's the human's turn again
        if self.ai is not None and self.ai_color is not None:
            while self.state.history and self.state.current is self.ai_color:
                self.state.undo()
        self._hint_move = None
        self._refresh()

    def _hint(self) -> None:
        if self.board_view.is_animating:
            return
        moves = self.state.legal_moves()
        if not moves:
            return
        from othello.ai.alphabeta import AlphaBetaAI
        self._hint_move = AlphaBetaAI(depth=3).select_move(self.state)
        self._refresh()

    def _save(self) -> None:
        Path("savegames").mkdir(exist_ok=True)
        default_name = f"othello-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        path = filedialog.asksaveasfilename(
            title="Save game",
            defaultextension=".json",
            filetypes=[("JSON saves", "*.json")],
            initialfile=default_name,
            initialdir="savegames",
        )
        if not path:
            return
        try:
            save_game(self.state, self.config_data, path)
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))

    # --- AI ---

    def _maybe_schedule_ai(self) -> None:
        if self.ai is None or self.ai_color is None:
            return
        if self.state.current is not self.ai_color:
            return
        if self.state.is_over():
            return
        self.after(300, self._run_ai_turn)

    def _run_ai_turn(self) -> None:
        if self.board_view.is_animating:
            self.after(100, self._run_ai_turn)
            return
        if self.ai is None or self.state.current is not self.ai_color:
            return
        try:
            move = self.ai.select_move(self.state)
        except ValueError:
            return
        self._play(move)

    # --- Rendering ---

    def _refresh(self) -> None:
        legal = self.state.legal_moves()
        if self._hint_move:
            hints: list[Move] = [self._hint_move]
        else:
            # Only show hints if it's the human's turn (or 2-player mode)
            human_turn = self.ai is None or self.state.current is not self.ai_color
            hints = legal if human_turn else []
        self.board_view.render(self.state.board, hints=hints)
        self._update_status()
        self._update_history()

    def _update_status(self) -> None:
        bullet = "B" if self.state.current is Color.BLACK else "W"
        self.turn_label.config(text=f"Turn: {bullet} {self.state.current.name}")
        b, w = self.state.score()
        self.score_label.config(text=f"Score:  B {b}   W {w}")

    def _update_history(self) -> None:
        items = []
        for n, entry in enumerate(self.state.history, start=1):
            label = _move_label(entry.move)
            color = "B" if entry.color_to_move is Color.BLACK else "W"
            items.append(f"{n}. {color} {label}")
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", "end")
        self.history_text.insert("1.0", "\n".join(items))
        self.history_text.config(state="disabled")

    def _announce_winner(self) -> None:
        sound.play_win()
        w = self.state.winner()
        b, wh = self.state.score()
        if w is None:
            msg = f"Tie!  B {b}   W {wh}"
        else:
            msg = f"{w.name} wins!  B {b}   W {wh}"
        messagebox.showinfo("Game over", msg)

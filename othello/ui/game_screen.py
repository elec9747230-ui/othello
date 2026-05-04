"""
othello/ui/game_screen.py — In-game screen for the Othello GUI.

GameScreen is a tk.Frame that hosts:
  - A BoardView canvas on the left showing the live board state.
  - A side panel on the right with turn/score labels, action buttons
    (Undo, Hint, Save, Menu), and a scrollable move-history log.

It manages all user interactions during a game:
  Human clicks  →  _on_click  →  _play
  AI turns      →  _maybe_schedule_ai  →  _run_ai_turn  →  _play
  Undo button   →  _undo
  Hint button   →  _hint
  Save button   →  _save

The AI runs on Tkinter's after() scheduler (single-threaded), so the UI
stays responsive while the AI is thinking — the AI's select_move() call is
synchronous but short enough (depth ≤ 5) that it completes in well under
a frame.
"""

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
    """Convert a Move to a human-readable algebraic label.

    Standard Othello / chess-like notation:
      col 0 → 'a', col 1 → 'b', …  (letter = column)
      row 0 → 1,   row 1 → 2,   …  (number = 1-based row)

    Example: Move(row=2, col=3) → "d3"

    Args:
        m: The move to format.

    Returns:
        A string such as "d3" or "pass".
    """
    if m.is_pass:
        return "pass"
    # chr(ord('a') + col) maps 0→'a', 1→'b', etc.
    return f"{chr(ord('a') + m.col)}{m.row + 1}"


def _build_strategy(name: str):
    """Instantiate and return an AI Strategy by name.

    Imports are deferred to this function to avoid loading all AI modules at
    startup — only the chosen strategy is imported.

    Args:
        name: One of "random", "greedy", "minimax", "alphabeta".

    Returns:
        A Strategy instance.

    Raises:
        ValueError: If `name` does not match a known strategy.
    """
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
    """The main in-game screen widget.

    Attributes:
        app:          Reference to OthelloApp for navigation (menu button).
        config_data:  Game configuration dict (mode, size, ai settings).
        state:        The live GameState tracking board, turn, and history.
        ai:           The AI Strategy instance, or None in two-player mode.
        ai_color:     The Color the AI is playing as, or None.
        board_view:   The BoardView canvas widget.
        turn_label:   Label showing whose turn it is.
        score_label:  Label showing the current disc counts.
        history_text: Text widget showing the move history log.
        _hint_move:   The last hint move selected by AlphaBeta, or None.
    """

    def __init__(self, root: tk.Tk, app, config: dict[str, Any]):
        """Build the game screen layout and start the first turn.

        Args:
            root:   Tkinter root window.
            app:    OthelloApp controller for screen transitions.
            config: Game configuration dict from MenuScreen or a save file.
        """
        super().__init__(root)
        self.app = app

        # Pop the internal "_loaded_state" key before storing config so it
        # doesn't get serialised into save files.
        self.config_data = dict(config)
        loaded = self.config_data.pop("_loaded_state", None)

        size = self.config_data.get("size", 8)

        # Use a loaded GameState (from a save file) or create a fresh one.
        self.state: GameState = loaded if loaded is not None else GameState(size=size)

        # --- AI setup ---
        self.ai = None
        self.ai_color: Color | None = None
        if self.config_data.get("mode") == "vs_ai":
            self.ai = _build_strategy(self.config_data["ai_difficulty"])
            human = Color[self.config_data.get("human_color", "BLACK")]
            # The AI plays the opposite colour from the human.
            self.ai_color = human.opponent()

        # --- Layout: board canvas (left) ---
        self.board_view = BoardView(self, self.state.board.size, self._on_click)
        self.board_view.pack(side="left", padx=10, pady=10)

        # --- Layout: side panel (right) ---
        side = ttk.Frame(self)
        side.pack(side="right", fill="y", padx=10, pady=10)

        # Status labels.
        self.turn_label  = ttk.Label(side, text="", font=("Helvetica", 14, "bold"))
        self.turn_label.pack(anchor="w", pady=5)
        self.score_label = ttk.Label(side, text="", font=("Helvetica", 12))
        self.score_label.pack(anchor="w", pady=5)

        # Action buttons.
        ttk.Button(side, text="Undo",  command=self._undo).pack(fill="x", pady=2)
        ttk.Button(side, text="Hint",  command=self._hint).pack(fill="x", pady=2)
        ttk.Button(side, text="Save",  command=self._save).pack(fill="x", pady=2)
        ttk.Button(side, text="Menu",  command=app.show_menu).pack(fill="x", pady=2)

        # Move-history log (read-only text widget).
        ttk.Label(side, text="History:").pack(anchor="w", pady=(10, 2))
        self.history_text = tk.Text(side, width=24, height=20, state="disabled")
        self.history_text.pack(fill="y", expand=True)

        # Internal state for the currently displayed hint move.
        self._hint_move: Move | None = None

        # Initial render.
        self._refresh()

        # If it's already the AI's turn (e.g. AI plays Black), schedule it.
        self._maybe_schedule_ai()

    # -----------------------------------------------------------------------
    # Event handlers
    # -----------------------------------------------------------------------

    def _on_click(self, row: int, col: int) -> None:
        """Handle a board cell click from the human player.

        Ignores clicks during animations and when it is the AI's turn.
        Validates the move against the current legal-move list before playing.

        Args:
            row: Zero-based row of the clicked cell.
            col: Zero-based column of the clicked cell.
        """
        # Reject input if an animation is in progress.
        if self.board_view.is_animating:
            return

        # Reject input if it is the AI's turn.
        if self.ai is not None and self.state.current is self.ai_color:
            return

        move = Move(row, col)

        # Only accept legal moves.
        if move not in self.state.legal_moves():
            return

        self._play(move)

    def _play(self, move: Move) -> None:
        """Apply `move` to the game state and trigger the board animation.

        Sequence:
          1. Compute which discs will be flipped (before the state changes).
          2. Apply the move to the game state.
          3. Play the "place" sound.
          4. Kick off the BoardView animation.
          5. After the animation: refresh the board, check for game-over,
             and schedule the AI if needed.

        Args:
            move: The Move to apply (must be legal).
        """
        # Capture the flip list *before* mutating the state so animate_move
        # can highlight the correct cells.
        flips = flips_for(self.state.board, move, self.state.current)

        try:
            self.state.play(move)
        except ValueError:
            return  # should not happen if legality was checked, but be safe

        sound.play_place()
        self._hint_move = None  # discard any displayed hint after each move

        def after_anim() -> None:
            """Callback invoked when the BoardView animation completes."""
            self._refresh()
            if self.state.is_over():
                self._announce_winner()
                return
            # Schedule the AI's response if it is now the AI's turn.
            self._maybe_schedule_ai()

        # Start the animation; status bar and history are updated immediately
        # so the player can read the updated score while the animation plays.
        self.board_view.animate_move(self.state.board, move, flips, after_anim)
        self._update_status()
        self._update_history()

    def _undo(self) -> None:
        """Undo the last move (or the last human move in vs-AI mode).

        In vs-AI mode, keeps undoing until it is the human's turn again so
        the human does not end up watching the AI immediately re-make a move
        after a single undo.

        No-op if the history is empty or an animation is running.
        """
        if self.board_view.is_animating:
            return
        if not self.state.history:
            return

        self.state.undo()

        # In vs-AI mode, skip back past any AI plies so the human can play.
        if self.ai is not None and self.ai_color is not None:
            while self.state.history and self.state.current is self.ai_color:
                self.state.undo()

        self._hint_move = None
        self._refresh()

    def _hint(self) -> None:
        """Show a hint dot on the best move according to AlphaBeta (depth 3).

        Uses a depth-3 AlphaBeta search rather than the game's configured AI
        so that even in two-player mode hints are always available.
        No-op if an animation is running or there are no legal moves.
        """
        if self.board_view.is_animating:
            return
        moves = self.state.legal_moves()
        if not moves:
            return

        # Always use AlphaBeta for hints regardless of the game-mode AI.
        from othello.ai.alphabeta import AlphaBetaAI
        self._hint_move = AlphaBetaAI(depth=3).select_move(self.state)

        # Re-render the board to show the hint dot.
        self._refresh()

    def _save(self) -> None:
        """Open a file-save dialog and write the current game to a JSON file.

        Creates the "savegames/" directory if it does not yet exist.
        Shows an error dialog if the file cannot be written.
        """
        Path("savegames").mkdir(exist_ok=True)

        # Default filename encodes the current date and time for easy sorting.
        default_name = f"othello-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"

        path = filedialog.asksaveasfilename(
            title="Save game",
            defaultextension=".json",
            filetypes=[("JSON saves", "*.json")],
            initialfile=default_name,
            initialdir="savegames",
        )

        # asksaveasfilename returns an empty string if the user cancelled.
        if not path:
            return

        try:
            save_game(self.state, self.config_data, path)
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))

    # -----------------------------------------------------------------------
    # AI scheduling
    # -----------------------------------------------------------------------

    def _maybe_schedule_ai(self) -> None:
        """Schedule an AI turn 300 ms from now if it is the AI's turn.

        The 300 ms delay gives the board animation time to finish and lets
        the human see the current board state before the AI responds.
        No-op in two-player mode or if the game is over.
        """
        if self.ai is None or self.ai_color is None:
            return
        if self.state.current is not self.ai_color:
            return
        if self.state.is_over():
            return

        # after() schedules the callback on Tkinter's event loop — no thread needed.
        self.after(300, self._run_ai_turn)

    def _run_ai_turn(self) -> None:
        """Execute the AI's move selection and play the chosen move.

        If an animation is still running when this callback fires, reschedules
        itself for 100 ms later.  Guards against stale callbacks (e.g. after
        an undo changed the turn back to the human).
        """
        # If an animation is in progress, wait a little longer.
        if self.board_view.is_animating:
            self.after(100, self._run_ai_turn)
            return

        # Stale callback guard: check it is still the AI's turn.
        if self.ai is None or self.state.current is not self.ai_color:
            return

        try:
            move = self.ai.select_move(self.state)
        except ValueError:
            return  # AI has no moves — game might be about to end

        self._play(move)

    # -----------------------------------------------------------------------
    # Rendering helpers
    # -----------------------------------------------------------------------

    def _refresh(self) -> None:
        """Fully re-render the board, status bar, and history log.

        Decides which hint dots to show:
          - If _hint_move is set (user clicked Hint), show only that dot.
          - Otherwise, show all legal moves during the human's turn.
          - During the AI's turn, show no dots.
        """
        legal = self.state.legal_moves()

        if self._hint_move:
            # User explicitly requested a hint — show only the best move.
            hints: list[Move] = [self._hint_move]
        else:
            # Show all legal moves as subtle guide dots, but only when
            # it is the human's turn (or in two-player mode).
            human_turn = self.ai is None or self.state.current is not self.ai_color
            hints = legal if human_turn else []

        self.board_view.render(self.state.board, hints=hints)
        self._update_status()
        self._update_history()

    def _update_status(self) -> None:
        """Refresh the turn and score labels with the current game state."""
        # Single-letter bullet: "B" for black, "W" for white.
        bullet = "B" if self.state.current is Color.BLACK else "W"
        self.turn_label.config(text=f"Turn: {bullet} {self.state.current.name}")

        b, w = self.state.score()
        self.score_label.config(text=f"Score:  B {b}   W {w}")

    def _update_history(self) -> None:
        """Rebuild the move-history text widget from the current history list.

        Each line has the format:  "<n>. <B|W> <label>"
        Example: "5. W d3"
        """
        items = []
        for n, entry in enumerate(self.state.history, start=1):
            label = _move_label(entry.move)
            color = "B" if entry.color_to_move is Color.BLACK else "W"
            items.append(f"{n}. {color} {label}")

        # The Text widget must be set to "normal" state to allow writes,
        # then locked back to "disabled" so the user cannot type in it.
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", "end")
        self.history_text.insert("1.0", "\n".join(items))
        self.history_text.config(state="disabled")

    def _announce_winner(self) -> None:
        """Play the win sound and show a game-over message box.

        Called once is_over() returns True after an animation completes.
        """
        sound.play_win()
        w = self.state.winner()
        b, wh = self.state.score()

        if w is None:
            msg = f"Tie!  B {b}   W {wh}"
        else:
            msg = f"{w.name} wins!  B {b}   W {wh}"

        messagebox.showinfo("Game over", msg)

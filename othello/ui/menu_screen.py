"""
othello/ui/menu_screen.py — Main menu screen for the Othello GUI.

MenuScreen presents all pre-game configuration options:
  - Game mode:      Two-player local vs. single-player vs. AI
  - AI difficulty:  Random / Greedy / Minimax / Alpha-Beta
  - Human colour:   Black (moves first) or White
  - Board size:     6×6, 8×8 (standard), or 10×10

It also provides a "Load Saved Game" button that opens a file picker,
replays the saved move history to reconstruct the GameState, and
transitions directly into a GameScreen with that state pre-loaded.

When "vs AI" mode is not selected, the AI difficulty and human-colour
sections are disabled so the user cannot accidentally set options that
have no effect in two-player mode.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any


class MenuScreen(tk.Frame):
    """The main menu screen widget displayed at application startup.

    Attributes:
        app:         Reference to OthelloApp for triggering screen transitions.
        mode_var:    StringVar tracking the selected game mode.
        ai_var:      StringVar tracking the selected AI difficulty.
        color_var:   StringVar tracking the human player's chosen colour.
        size_var:    IntVar tracking the selected board size.
        ai_frame:    The LabelFrame containing AI difficulty radio buttons.
        color_frame: The LabelFrame containing human-colour radio buttons.
    """

    def __init__(self, root: tk.Tk, app):
        """Build the menu layout and set default option values.

        Args:
            root: Tkinter root window (parent widget).
            app:  OthelloApp controller; used to call show_game() or show_menu().
        """
        super().__init__(root)
        self.app = app

        # Title label.
        ttk.Label(self, text="Othello", font=("Helvetica", 32, "bold")).pack(pady=20)

        # -------------------------------------------------------------------
        # Game mode section
        # -------------------------------------------------------------------
        self.mode_var = tk.StringVar(value="two_player")
        mode_frame = ttk.LabelFrame(self, text="Mode")
        mode_frame.pack(padx=20, pady=10, fill="x")

        ttk.Radiobutton(
            mode_frame, text="2 Player",
            variable=self.mode_var, value="two_player",
            command=self._refresh_enabled,   # enable/disable dependent sections
        ).pack(anchor="w", padx=10)

        ttk.Radiobutton(
            mode_frame, text="vs AI",
            variable=self.mode_var, value="vs_ai",
            command=self._refresh_enabled,
        ).pack(anchor="w", padx=10)

        # -------------------------------------------------------------------
        # AI difficulty section (enabled only in vs-AI mode)
        # -------------------------------------------------------------------
        self.ai_var = tk.StringVar(value="alphabeta")  # default to strongest AI
        ai_frame = ttk.LabelFrame(self, text="AI Difficulty")
        ai_frame.pack(padx=20, pady=10, fill="x")

        for label, val in [
            ("Random",     "random"),    # picks a legal move at random
            ("Greedy",     "greedy"),    # maximises immediate flips
            ("Minimax",    "minimax"),   # depth-3 minimax search
            ("Alpha-Beta", "alphabeta"), # depth-5 alpha-beta search (strongest)
        ]:
            ttk.Radiobutton(ai_frame, text=label, variable=self.ai_var, value=val).pack(
                anchor="w", padx=10
            )
        self.ai_frame = ai_frame  # saved so _refresh_enabled can iterate its children

        # -------------------------------------------------------------------
        # Human colour section (enabled only in vs-AI mode)
        # -------------------------------------------------------------------
        self.color_var = tk.StringVar(value="BLACK")  # default: human plays first
        color_frame = ttk.LabelFrame(self, text="Human Color")
        color_frame.pack(padx=20, pady=10, fill="x")

        ttk.Radiobutton(
            color_frame, text="Black (first)",  variable=self.color_var, value="BLACK"
        ).pack(anchor="w", padx=10)
        ttk.Radiobutton(
            color_frame, text="White (second)", variable=self.color_var, value="WHITE"
        ).pack(anchor="w", padx=10)
        self.color_frame = color_frame

        # -------------------------------------------------------------------
        # Board size section
        # -------------------------------------------------------------------
        self.size_var = tk.IntVar(value=8)  # standard 8×8 board is the default
        size_frame = ttk.LabelFrame(self, text="Board Size")
        size_frame.pack(padx=20, pady=10, fill="x")

        for s in (6, 8, 10):
            ttk.Radiobutton(
                size_frame, text=f"{s}x{s}", variable=self.size_var, value=s
            ).pack(anchor="w", padx=10)

        # -------------------------------------------------------------------
        # Action buttons
        # -------------------------------------------------------------------
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Start",
                   command=self._start).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Load Saved Game",
                   command=self._load).pack(side="left", padx=5)

        # Set the initial enabled/disabled state of AI-related widgets.
        self._refresh_enabled()

    def _refresh_enabled(self) -> None:
        """Enable or disable AI-specific widgets based on the current mode.

        When "two_player" is selected, the AI difficulty and human-colour
        sections are disabled so the user cannot interact with irrelevant
        options.  When "vs_ai" is selected they are re-enabled.
        """
        # "normal" enables widgets; "disabled" greys them out.
        state = "normal" if self.mode_var.get() == "vs_ai" else "disabled"

        for child in self.ai_frame.winfo_children():
            child.configure(state=state)
        for child in self.color_frame.winfo_children():
            child.configure(state=state)

    def _start(self) -> None:
        """Read the current widget values and start a new game.

        Builds a config dict from the selected options and passes it to
        OthelloApp.show_game() which creates a GameScreen with that config.
        """
        config: dict[str, Any] = {
            "mode": self.mode_var.get(),
            "size": self.size_var.get(),
        }

        # Only include AI settings when they are relevant.
        if config["mode"] == "vs_ai":
            config["ai_difficulty"] = self.ai_var.get()
            config["human_color"]   = self.color_var.get()

        self.app.show_game(config)

    def _load(self) -> None:
        """Open a file picker, load a saved game, and transition to GameScreen.

        Shows an error dialog if the file cannot be parsed or is incompatible
        with the current save format version.

        The loaded GameState is injected into the config dict under the
        special key "_loaded_state".  GameScreen pops this key and uses the
        pre-built state instead of creating a fresh one.
        """
        path = filedialog.askopenfilename(
            title="Load saved game",
            filetypes=[("JSON saves", "*.json"), ("All files", "*.*")],
            initialdir="savegames",
        )

        # askopenfilename returns an empty string if the user cancelled.
        if not path:
            return

        try:
            from othello.persistence import load_game
            state, info = load_game(path)
        except (OSError, ValueError, KeyError) as exc:
            messagebox.showerror("Load failed", f"Could not load save:\n{exc}")
            return

        # Build the config dict that GameScreen expects.
        config = dict(info)
        config["size"]          = state.board.size   # board size from the saved state
        config["_loaded_state"] = state              # pre-built GameState to inject

        self.app.show_game(config)

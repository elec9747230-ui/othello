import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any


class MenuScreen(tk.Frame):
    def __init__(self, root: tk.Tk, app):
        super().__init__(root)
        self.app = app

        ttk.Label(self, text="Othello", font=("Helvetica", 32, "bold")).pack(pady=20)

        # Mode
        self.mode_var = tk.StringVar(value="two_player")
        mode_frame = ttk.LabelFrame(self, text="Mode")
        mode_frame.pack(padx=20, pady=10, fill="x")
        ttk.Radiobutton(
            mode_frame, text="2 Player", variable=self.mode_var, value="two_player",
            command=self._refresh_enabled,
        ).pack(anchor="w", padx=10)
        ttk.Radiobutton(
            mode_frame, text="vs AI", variable=self.mode_var, value="vs_ai",
            command=self._refresh_enabled,
        ).pack(anchor="w", padx=10)

        # AI difficulty
        self.ai_var = tk.StringVar(value="alphabeta")
        ai_frame = ttk.LabelFrame(self, text="AI Difficulty")
        ai_frame.pack(padx=20, pady=10, fill="x")
        for label, val in [
            ("Random", "random"), ("Greedy", "greedy"),
            ("Minimax", "minimax"), ("Alpha-Beta", "alphabeta"),
        ]:
            ttk.Radiobutton(ai_frame, text=label, variable=self.ai_var, value=val).pack(
                anchor="w", padx=10
            )
        self.ai_frame = ai_frame

        # Human color
        self.color_var = tk.StringVar(value="BLACK")
        color_frame = ttk.LabelFrame(self, text="Human Color")
        color_frame.pack(padx=20, pady=10, fill="x")
        ttk.Radiobutton(color_frame, text="Black (first)", variable=self.color_var,
                        value="BLACK").pack(anchor="w", padx=10)
        ttk.Radiobutton(color_frame, text="White (second)", variable=self.color_var,
                        value="WHITE").pack(anchor="w", padx=10)
        self.color_frame = color_frame

        # Board size
        self.size_var = tk.IntVar(value=8)
        size_frame = ttk.LabelFrame(self, text="Board Size")
        size_frame.pack(padx=20, pady=10, fill="x")
        for s in (6, 8, 10):
            ttk.Radiobutton(size_frame, text=f"{s}x{s}", variable=self.size_var,
                            value=s).pack(anchor="w", padx=10)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Start", command=self._start).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Load Saved Game",
                   command=self._load).pack(side="left", padx=5)

        self._refresh_enabled()

    def _refresh_enabled(self) -> None:
        state = "normal" if self.mode_var.get() == "vs_ai" else "disabled"
        for child in self.ai_frame.winfo_children():
            child.configure(state=state)
        for child in self.color_frame.winfo_children():
            child.configure(state=state)

    def _start(self) -> None:
        config: dict[str, Any] = {
            "mode": self.mode_var.get(),
            "size": self.size_var.get(),
        }
        if config["mode"] == "vs_ai":
            config["ai_difficulty"] = self.ai_var.get()
            config["human_color"] = self.color_var.get()
        self.app.show_game(config)

    def _load(self) -> None:
        path = filedialog.askopenfilename(
            title="Load saved game",
            filetypes=[("JSON saves", "*.json"), ("All files", "*.*")],
            initialdir="savegames",
        )
        if not path:
            return
        try:
            from othello.persistence import load_game
            state, info = load_game(path)
        except (OSError, ValueError, KeyError) as exc:
            messagebox.showerror("Load failed", f"Could not load save:\n{exc}")
            return
        config = dict(info)
        config["size"] = state.board.size
        config["_loaded_state"] = state
        self.app.show_game(config)

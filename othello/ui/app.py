import tkinter as tk
from typing import Any


class OthelloApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Othello")
        self.root.geometry("900x680")
        self.current_screen: tk.Frame | None = None
        self.show_menu()

    def show_menu(self) -> None:
        from othello.ui.menu_screen import MenuScreen
        self._switch(MenuScreen(self.root, self))

    def show_game(self, config: dict[str, Any]) -> None:
        from othello.ui.game_screen import GameScreen
        self._switch(GameScreen(self.root, self, config))

    def _switch(self, frame: tk.Frame) -> None:
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = frame
        frame.pack(fill="both", expand=True)

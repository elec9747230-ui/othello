"""
othello/ui/app.py — Top-level application controller for the Othello GUI.

OthelloApp owns the Tkinter root window and is responsible for switching
between the different screens (menu, game).  It acts as a thin coordinator:
it knows which screen is currently shown and can swap it out on request,
but all screen-specific logic lives in MenuScreen and GameScreen.

Screen lifecycle:
  1. OthelloApp.__init__ calls show_menu() immediately.
  2. MenuScreen calls app.show_game(config) when the user clicks Start.
  3. GameScreen calls app.show_menu() when the user clicks the Menu button.
  4. Each call to _switch() destroys the old screen before packing the new one,
     ensuring only one screen is visible at a time and preventing widget leaks.
"""

import tkinter as tk
from typing import Any


class OthelloApp:
    """Top-level controller that manages screen transitions for the Othello GUI.

    Keeps a reference to the currently displayed screen (a tk.Frame subclass)
    and replaces it when a transition is requested.

    Attributes:
        root:           The Tkinter root window passed in from main.py.
        current_screen: The tk.Frame currently packed into the window, or None
                        before the first screen is shown.
    """

    def __init__(self, root: tk.Tk):
        """Configure the root window and display the initial menu screen.

        Args:
            root: The Tkinter root window created by main.py.
        """
        self.root = root
        self.root.title("Othello")           # window title bar text
        self.root.geometry("900x680")        # initial window size in pixels
        self.current_screen: tk.Frame | None = None

        # Show the main menu immediately on startup.
        self.show_menu()

    def show_menu(self) -> None:
        """Transition to the main menu screen.

        Imported lazily to avoid a circular import: MenuScreen imports
        OthelloApp indirectly through type hints, so deferring the import
        to call time breaks the cycle.
        """
        from othello.ui.menu_screen import MenuScreen
        self._switch(MenuScreen(self.root, self))

    def show_game(self, config: dict[str, Any]) -> None:
        """Transition to the game screen using the provided configuration.

        Args:
            config: Dictionary produced by MenuScreen._start() or by loading
                    a saved game.  Expected keys include:
                      "mode"           — "two_player" or "vs_ai"
                      "size"           — board side length (int)
                      "ai_difficulty"  — AI name string (vs_ai mode only)
                      "human_color"    — "BLACK" or "WHITE" (vs_ai mode only)
                      "_loaded_state"  — optional pre-built GameState from a save
        """
        from othello.ui.game_screen import GameScreen
        self._switch(GameScreen(self.root, self, config))

    def _switch(self, frame: tk.Frame) -> None:
        """Replace the current screen with `frame`.

        Destroys the old screen widget tree (freeing all child widgets) and
        packs the new frame so it fills the entire window.

        Args:
            frame: The new screen to display (a tk.Frame subclass).
        """
        if self.current_screen is not None:
            # Destroy the old screen and all its descendant widgets to
            # prevent memory leaks and hidden widget interactions.
            self.current_screen.destroy()

        self.current_screen = frame

        # fill="both" + expand=True makes the frame resize with the window.
        frame.pack(fill="both", expand=True)

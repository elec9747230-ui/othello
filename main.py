"""
main.py — Application entry point for the Othello game.

This module creates the Tkinter root window, instantiates the top-level
OthelloApp controller, and starts the Tkinter event loop.  It is the only
file that should be run directly (e.g. `python main.py`).
"""

import tkinter as tk

from othello.ui.app import OthelloApp


def main() -> None:
    """Create the Tkinter root window, attach the app, and run the event loop.

    The function is intentionally thin — all real initialisation happens
    inside OthelloApp so that the UI logic stays testable without needing
    to call mainloop().
    """
    # Create the top-level Tk window that owns all widgets.
    root = tk.Tk()

    # OthelloApp configures the window title/size and renders the first screen.
    OthelloApp(root)

    # Hand control to Tkinter's event loop; this call blocks until the window
    # is closed by the user.
    root.mainloop()


# Guard so that importing this module (e.g. from tests) does not start the GUI.
if __name__ == "__main__":
    main()

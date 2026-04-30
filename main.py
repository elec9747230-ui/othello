import tkinter as tk

from othello.ui.app import OthelloApp


def main() -> None:
    root = tk.Tk()
    OthelloApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

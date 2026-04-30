import tkinter as tk
from typing import Callable, Iterable

from othello.core.board import Board, Color, Move

CELL_PX = 60
PAD = 10
LINE_COLOR = "#2c3e50"
BOARD_COLOR = "#0e7c3a"
HINT_COLOR = "#ffd54f"

PLACE_MS = 150
FLIP_MS = 200
FLIP_STAGGER_MS = 30
ANIM_FPS = 60


class BoardView(tk.Frame):
    def __init__(self, master: tk.Misc, size: int, on_click: Callable[[int, int], None]):
        super().__init__(master)
        self.size = size
        self.on_click = on_click
        self.is_animating = False
        canvas_px = size * CELL_PX + 2 * PAD
        self.canvas = tk.Canvas(
            self, width=canvas_px, height=canvas_px,
            bg=BOARD_COLOR, highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._handle_click)
        self._stones: dict[tuple[int, int], int] = {}
        self._hints: list[int] = []
        self._draw_grid()

    def _draw_grid(self) -> None:
        for i in range(self.size + 1):
            x = PAD + i * CELL_PX
            self.canvas.create_line(x, PAD, x, PAD + self.size * CELL_PX, fill=LINE_COLOR)
            y = PAD + i * CELL_PX
            self.canvas.create_line(PAD, y, PAD + self.size * CELL_PX, y, fill=LINE_COLOR)

    # --- Static rendering ---

    def render(self, board: Board, hints: Iterable[Move] = ()) -> None:
        for cid in self._stones.values():
            self.canvas.delete(cid)
        self._stones.clear()
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()
        for r, c, color in board.cells():
            if color is Color.EMPTY:
                continue
            self._stones[(r, c)] = self._draw_stone(r, c, color)
        for m in hints:
            self._hints.append(self._draw_hint(m.row, m.col))

    # --- Animated render ---

    def animate_move(
        self,
        new_board: Board,
        placed: Move,
        flipped: list[tuple[int, int]],
        on_done: Callable[[], None],
    ) -> None:
        self.is_animating = True
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()
        placed_color = new_board[placed.row, placed.col]
        steps = max(1, int(PLACE_MS * ANIM_FPS / 1000))
        self._scale_in(
            placed.row, placed.col, placed_color, steps,
            on_done=lambda: self._do_flips(new_board, flipped, on_done),
        )

    def _scale_in(self, r: int, c: int, color: Color, steps: int, on_done: Callable[[], None]) -> None:
        if (r, c) in self._stones:
            self.canvas.delete(self._stones.pop((r, c)))
        delay = max(1, PLACE_MS // steps)

        def step(i: int) -> None:
            if (r, c) in self._stones:
                self.canvas.delete(self._stones[(r, c)])
            scale = (i + 1) / steps
            self._stones[(r, c)] = self._draw_stone(r, c, color, scale=scale)
            if i + 1 < steps:
                self.canvas.after(delay, lambda: step(i + 1))
            else:
                on_done()

        step(0)

    def _do_flips(
        self,
        new_board: Board,
        flipped: list[tuple[int, int]],
        on_done: Callable[[], None],
    ) -> None:
        if not flipped:
            self.is_animating = False
            on_done()
            return
        remaining = {"count": len(flipped)}

        def finish_one() -> None:
            remaining["count"] -= 1
            if remaining["count"] == 0:
                self.is_animating = False
                on_done()

        for i, (r, c) in enumerate(flipped):
            new_color = new_board[r, c]
            self.canvas.after(
                i * FLIP_STAGGER_MS,
                lambda r=r, c=c, nc=new_color: self._flip_one(r, c, nc, finish_one),
            )

    def _flip_one(self, r: int, c: int, new_color: Color, on_done: Callable[[], None]) -> None:
        steps = max(2, int(FLIP_MS * ANIM_FPS / 1000))
        delay = max(1, FLIP_MS // steps)
        old_color = new_color.opponent()

        def step(i: int) -> None:
            if (r, c) in self._stones:
                self.canvas.delete(self._stones[(r, c)])
            half = steps // 2
            if i < half:
                width_scale = 1 - (i / half)
                self._stones[(r, c)] = self._draw_oval_scaled(
                    r, c, old_color, x_scale=max(0.05, width_scale)
                )
            else:
                width_scale = (i - half + 1) / max(1, steps - half)
                self._stones[(r, c)] = self._draw_oval_scaled(
                    r, c, new_color, x_scale=max(0.05, width_scale)
                )
            if i + 1 < steps:
                self.canvas.after(delay, lambda: step(i + 1))
            else:
                self.canvas.delete(self._stones[(r, c)])
                self._stones[(r, c)] = self._draw_stone(r, c, new_color)
                on_done()

        step(0)

    # --- Drawing helpers ---

    def _draw_stone(self, r: int, c: int, color: Color, scale: float = 1.0) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = (CELL_PX / 2 - 4) * scale
        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_oval_scaled(self, r: int, c: int, color: Color, x_scale: float) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        rx = (CELL_PX / 2 - 4) * x_scale
        ry = CELL_PX / 2 - 4
        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - rx, y - ry, x + rx, y + ry,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_hint(self, r: int, c: int) -> int:
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = 6
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=HINT_COLOR, outline="",
        )

    def _handle_click(self, event: tk.Event) -> None:
        if self.is_animating:
            return
        col = (event.x - PAD) // CELL_PX
        row = (event.y - PAD) // CELL_PX
        if 0 <= row < self.size and 0 <= col < self.size:
            self.on_click(int(row), int(col))

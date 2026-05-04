"""
othello/ui/board_view.py — Tkinter canvas widget for rendering the Othello board.

BoardView owns a single tk.Canvas and provides:
  - Static rendering (render): draw all stones and optional hint dots in one
    synchronous call.
  - Animated rendering (animate_move): play a placement-then-flip animation
    driven by Tkinter's after() scheduler (no threads required).

Animation design
----------------
Two animations run in sequence:
  1. "Scale-in" — the newly placed disc grows from nothing to full size over
     PLACE_MS milliseconds.
  2. "Flip" — each captured disc shrinks along the x-axis (simulating a coin
     flip) and then re-expands in the new colour, with a small stagger delay
     (FLIP_STAGGER_MS) between each disc so they cascade rather than all
     flipping simultaneously.

While any animation is in progress, is_animating is set to True.  The game
screen checks this flag before accepting new clicks or scheduling the AI,
preventing input races.
"""

import tkinter as tk
from typing import Callable, Iterable

from othello.core.board import Board, Color, Move

# --- Layout constants (pixels) ---
CELL_PX = 60          # width and height of each board cell
PAD = 10              # padding around the grid on all four sides

# --- Colour constants ---
LINE_COLOR  = "#2c3e50"   # grid line and stone outline colour (dark navy)
BOARD_COLOR = "#0e7c3a"   # board background (green felt)
HINT_COLOR  = "#ffd54f"   # legal-move hint dot (amber)

# --- Animation timing ---
PLACE_MS        = 150     # total duration for the "place disc" scale-in (ms)
FLIP_MS         = 200     # total duration for one disc flip animation (ms)
FLIP_STAGGER_MS = 30      # delay between successive flip animations (ms)
ANIM_FPS        = 60      # target frame rate used to compute step counts


class BoardView(tk.Frame):
    """A tk.Frame containing a Canvas that renders an Othello board.

    Attributes:
        size:         Board side length (number of cells per row/column).
        on_click:     Callback invoked with (row, col) when the user clicks
                      a board cell (ignored during animation).
        is_animating: True while a place-or-flip animation is running.
        canvas:       The underlying tk.Canvas widget.
        _stones:      Maps (row, col) → canvas item ID for each placed disc.
        _hints:       List of canvas item IDs for the current hint dots.
    """

    def __init__(self, master: tk.Misc, size: int, on_click: Callable[[int, int], None]):
        """Create the board canvas and draw the empty grid.

        Args:
            master:   Parent widget.
            size:     Board side length (must match the GameState board size).
            on_click: Callback receiving (row, col) when the user clicks a cell.
        """
        super().__init__(master)
        self.size = size
        self.on_click = on_click
        self.is_animating = False  # guards against input during animations

        # Compute canvas pixel size: cells + padding on both sides.
        canvas_px = size * CELL_PX + 2 * PAD
        self.canvas = tk.Canvas(
            self,
            width=canvas_px,
            height=canvas_px,
            bg=BOARD_COLOR,
            highlightthickness=0,  # remove the default focus ring
        )
        self.canvas.pack()

        # Bind left mouse button click to our internal handler.
        self.canvas.bind("<Button-1>", self._handle_click)

        # Track canvas item IDs so we can delete/replace individual stones.
        self._stones: dict[tuple[int, int], int] = {}
        self._hints:  list[int] = []

        # Draw the static grid lines (only needs to happen once).
        self._draw_grid()

    def _draw_grid(self) -> None:
        """Draw the board grid lines on the canvas.

        Draws (size + 1) vertical and (size + 1) horizontal lines to form
        the square grid.  Grid lines are drawn once at construction time and
        never redrawn, since stones and hints are layered on top.
        """
        for i in range(self.size + 1):
            # Vertical line at column i.
            x = PAD + i * CELL_PX
            self.canvas.create_line(x, PAD, x, PAD + self.size * CELL_PX, fill=LINE_COLOR)

            # Horizontal line at row i.
            y = PAD + i * CELL_PX
            self.canvas.create_line(PAD, y, PAD + self.size * CELL_PX, y, fill=LINE_COLOR)

    # -----------------------------------------------------------------------
    # Static rendering
    # -----------------------------------------------------------------------

    def render(self, board: Board, hints: Iterable[Move] = ()) -> None:
        """Redraw all stones and hint dots to match `board`.

        Clears every existing stone and hint from the canvas, then redraws
        all occupied cells and the provided hint positions.  Called after
        undo, at game start, and whenever a refresh is needed outside of an
        animation.

        Args:
            board:  The current board state.
            hints:  Legal moves to mark with hint dots (amber circles).
        """
        # Remove all existing stone canvas items.
        for cid in self._stones.values():
            self.canvas.delete(cid)
        self._stones.clear()

        # Remove all existing hint canvas items.
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()

        # Draw stones for all occupied cells.
        for r, c, color in board.cells():
            if color is Color.EMPTY:
                continue
            self._stones[(r, c)] = self._draw_stone(r, c, color)

        # Draw hint dots on all provided legal move positions.
        for m in hints:
            self._hints.append(self._draw_hint(m.row, m.col))

    # -----------------------------------------------------------------------
    # Animated rendering
    # -----------------------------------------------------------------------

    def animate_move(
        self,
        new_board: Board,
        placed: Move,
        flipped: list[tuple[int, int]],
        on_done: Callable[[], None],
    ) -> None:
        """Animate a disc placement followed by disc flips.

        Runs two animations in sequence:
          1. Scale-in the newly placed disc at `placed`.
          2. Flip each disc in `flipped` (staggered).

        Sets is_animating = True for the duration.  Calls on_done() when the
        full animation sequence finishes.

        Args:
            new_board: The board state *after* the move (used to read the
                       colour of placed and flipped discs).
            placed:    The cell where the new disc was placed.
            flipped:   Cells whose discs were captured and must be flipped.
            on_done:   Callback invoked once all animations complete.
        """
        self.is_animating = True

        # Clear hint dots immediately — they are no longer relevant.
        for cid in self._hints:
            self.canvas.delete(cid)
        self._hints.clear()

        placed_color = new_board[placed.row, placed.col]

        # Number of animation frames for the scale-in step.
        steps = max(1, int(PLACE_MS * ANIM_FPS / 1000))

        # After the scale-in finishes, start the flip animations.
        self._scale_in(
            placed.row, placed.col, placed_color, steps,
            on_done=lambda: self._do_flips(new_board, flipped, on_done),
        )

    def _scale_in(self, r: int, c: int, color: Color, steps: int, on_done: Callable[[], None]) -> None:
        """Animate a disc growing from zero to full size at (r, c).

        Uses Tkinter's after() to schedule each frame.  The disc is drawn at
        increasing scale factors (1/steps, 2/steps, … 1.0).

        Args:
            r, c:    Cell to place the disc at.
            color:   Color of the new disc.
            steps:   Total number of animation frames.
            on_done: Callback invoked when the animation finishes.
        """
        # Remove any existing stone at this cell before animating.
        if (r, c) in self._stones:
            self.canvas.delete(self._stones.pop((r, c)))

        # Compute per-frame delay in milliseconds, clamped to >= 1 ms.
        delay = max(1, PLACE_MS // steps)

        def step(i: int) -> None:
            """Draw one frame of the scale-in animation."""
            # Delete the previous frame's drawing for this cell.
            if (r, c) in self._stones:
                self.canvas.delete(self._stones[(r, c)])

            # Scale ranges from nearly-zero (i=0) to 1.0 (i=steps-1).
            scale = (i + 1) / steps
            self._stones[(r, c)] = self._draw_stone(r, c, color, scale=scale)

            if i + 1 < steps:
                # Schedule the next frame.
                self.canvas.after(delay, lambda: step(i + 1))
            else:
                # Last frame — signal completion and start the flip phase.
                on_done()

        step(0)  # kick off the first frame immediately

    def _do_flips(
        self,
        new_board: Board,
        flipped: list[tuple[int, int]],
        on_done: Callable[[], None],
    ) -> None:
        """Start staggered flip animations for all captured discs.

        Each disc in `flipped` starts its flip animation FLIP_STAGGER_MS
        milliseconds after the previous one, so they cascade left-to-right /
        top-to-bottom rather than all flipping at once.

        Uses a shared mutable counter (dict) to detect when the last flip
        animation has finished and call on_done().

        Args:
            new_board: Board state after the move; used to read the new colour.
            flipped:   List of (row, col) cells to flip.
            on_done:   Callback invoked when all flip animations finish.
        """
        if not flipped:
            # No captures (can happen with a pass); finish immediately.
            self.is_animating = False
            on_done()
            return

        # Shared counter tracking how many flip animations are still running.
        # Using a dict so the nested closure can mutate it (Python 3 closure
        # cells don't allow rebinding a plain integer variable).
        remaining = {"count": len(flipped)}

        def finish_one() -> None:
            """Called by each flip animation when it completes."""
            remaining["count"] -= 1
            if remaining["count"] == 0:
                # All flips done — release the animation lock and notify caller.
                self.is_animating = False
                on_done()

        for i, (r, c) in enumerate(flipped):
            new_color = new_board[r, c]
            # Schedule each flip with an increasing stagger offset.
            self.canvas.after(
                i * FLIP_STAGGER_MS,
                # Use default-argument capture (r=r, c=c, nc=new_color) to
                # avoid the classic loop-closure variable capture bug.
                lambda r=r, c=c, nc=new_color: self._flip_one(r, c, nc, finish_one),
            )

    def _flip_one(self, r: int, c: int, new_color: Color, on_done: Callable[[], None]) -> None:
        """Animate a single disc flipping from its old colour to `new_color`.

        The animation has two phases:
          Phase 1 (shrink): The x-radius shrinks from full to near-zero while
                            keeping the old colour.  Simulates the first half
                            of a coin flip.
          Phase 2 (grow):   The x-radius grows from near-zero to full while
                            showing the new colour.  Simulates the second half.

        Args:
            r, c:      Cell containing the disc to flip.
            new_color: The colour to flip to.
            on_done:   Callback invoked when this single flip finishes.
        """
        steps = max(2, int(FLIP_MS * ANIM_FPS / 1000))
        delay = max(1, FLIP_MS // steps)
        old_color = new_color.opponent()  # the colour the disc is changing from

        def step(i: int) -> None:
            """Draw one frame of the flip animation."""
            if (r, c) in self._stones:
                self.canvas.delete(self._stones[(r, c)])

            half = steps // 2  # frame index where the colour switches

            if i < half:
                # --- Phase 1: shrink (old colour) ---
                # width_scale goes 1.0 → 0 over the first half of the animation.
                width_scale = 1 - (i / half)
                self._stones[(r, c)] = self._draw_oval_scaled(
                    r, c, old_color, x_scale=max(0.05, width_scale)
                )
            else:
                # --- Phase 2: grow (new colour) ---
                # width_scale goes 0 → 1.0 over the second half.
                width_scale = (i - half + 1) / max(1, steps - half)
                self._stones[(r, c)] = self._draw_oval_scaled(
                    r, c, new_color, x_scale=max(0.05, width_scale)
                )

            if i + 1 < steps:
                self.canvas.after(delay, lambda: step(i + 1))
            else:
                # Last frame: draw the final fully-expanded disc and signal done.
                self.canvas.delete(self._stones[(r, c)])
                self._stones[(r, c)] = self._draw_stone(r, c, new_color)
                on_done()

        step(0)

    # -----------------------------------------------------------------------
    # Drawing helpers
    # -----------------------------------------------------------------------

    def _draw_stone(self, r: int, c: int, color: Color, scale: float = 1.0) -> int:
        """Draw a circular disc at cell (r, c) and return its canvas item ID.

        Args:
            r, c:  Cell coordinates.
            color: Color.BLACK (black fill) or Color.WHITE (white fill).
            scale: Fraction of full size to draw (0.0–1.0); default full size.

        Returns:
            The canvas item ID of the created oval, for later deletion.
        """
        # Compute the pixel centre of this cell.
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2

        # Leave a 4-pixel margin so the stone does not touch the grid lines.
        radius = (CELL_PX / 2 - 4) * scale

        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_oval_scaled(self, r: int, c: int, color: Color, x_scale: float) -> int:
        """Draw a horizontally-scaled oval to simulate a coin-flip mid-frame.

        Only the x-radius is scaled; the y-radius stays at full size.  This
        creates the visual illusion of a disc rotating around its vertical axis.

        Args:
            r, c:    Cell coordinates.
            color:   Disc colour for this frame.
            x_scale: Fraction (0–1) of the full x-radius to use.

        Returns:
            The canvas item ID of the created oval.
        """
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2

        rx = (CELL_PX / 2 - 4) * x_scale   # scaled horizontal radius
        ry = CELL_PX / 2 - 4                # full vertical radius (unchanged)

        fill = "#000000" if color is Color.BLACK else "#ffffff"
        return self.canvas.create_oval(
            x - rx, y - ry, x + rx, y + ry,
            fill=fill, outline=LINE_COLOR,
        )

    def _draw_hint(self, r: int, c: int) -> int:
        """Draw a small amber dot at cell (r, c) to indicate a legal move.

        Args:
            r, c: Cell coordinates.

        Returns:
            The canvas item ID of the hint circle.
        """
        x = PAD + c * CELL_PX + CELL_PX / 2
        y = PAD + r * CELL_PX + CELL_PX / 2
        radius = 6  # small fixed radius so the hint does not obscure existing stones
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=HINT_COLOR,
            outline="",  # no border on the hint dot
        )

    def _handle_click(self, event: tk.Event) -> None:
        """Convert a canvas pixel click into a (row, col) cell click.

        Ignores clicks while an animation is in progress to prevent input
        races.  Ignores clicks outside the grid area.

        Args:
            event: Tkinter mouse-button event with .x and .y pixel coordinates.
        """
        # Reject clicks during animation — the board is mid-transition.
        if self.is_animating:
            return

        # Convert pixel coordinates to cell indices.
        col = (event.x - PAD) // CELL_PX
        row = (event.y - PAD) // CELL_PX

        # Only forward clicks that land inside the grid.
        if 0 <= row < self.size and 0 <= col < self.size:
            self.on_click(int(row), int(col))

"""
othello/ui/sound.py — Audio playback for the Othello GUI.

Provides three public functions:
  play_place() — plays when a disc is placed on the board
  play_flip()  — plays when discs are flipped (currently unused by default)
  play_win()   — plays when the game ends

Audio backend selection
-----------------------
The module tries to find an available audio backend at import time (via
_make_player()) and stores it as _PLAYER.  Two backends are supported:

  1. winsound (Windows only, stdlib) — fastest and dependency-free.
     Uses SND_ASYNC so playback does not block the Tkinter event loop.

  2. playsound (cross-platform, third-party) — used on macOS/Linux or as a
     Windows fallback if winsound is somehow unavailable.

If neither backend is importable, _PLAYER is set to None and all sound
calls become no-ops (the game plays silently without errors).

Sound files are expected at:
  <repo-root>/assets/sounds/{place,flip,win}.wav
"""

import logging
import sys
from pathlib import Path
from typing import Callable

# Module-level logger; messages appear in the console/log at DEBUG level.
logger = logging.getLogger(__name__)

# Resolve the absolute path to the sounds directory relative to this file.
# __file__ is othello/ui/sound.py, so we go up three levels to the repo root.
ASSETS = Path(__file__).resolve().parent.parent.parent / "assets" / "sounds"


def _make_player() -> Callable[[Path], None] | None:
    """Detect the best available audio backend and return a play function.

    Called once at module import time.  The returned callable accepts a
    Path to a .wav file and plays it asynchronously (non-blocking).

    Returns:
        A callable(Path) → None that plays a WAV file, or None if no
        audio backend is available.
    """
    # --- Backend 1: winsound (Windows stdlib) ---
    # Preferred on Windows because it requires no extra dependencies and
    # SND_ASYNC plays the sound in a background thread without blocking.
    if sys.platform == "win32":
        try:
            import winsound

            def play_winsound(path: Path) -> None:
                winsound.PlaySound(
                    str(path),
                    # SND_FILENAME: path is a file path (not a system alias)
                    # SND_ASYNC:    play in background without blocking
                    # SND_NODEFAULT: do not fall back to the system beep if
                    #               the file is missing
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
                )

            return play_winsound
        except ImportError:
            pass  # winsound should always be present on Win32, but be safe

    # --- Backend 2: playsound (cross-platform, optional dependency) ---
    try:
        from playsound import playsound  # type: ignore[import-not-found]

        def play_playsound(path: Path) -> None:
            # block=False makes playback asynchronous (non-blocking).
            playsound(str(path), block=False)

        return play_playsound
    except ImportError:
        # playsound is not installed — disable sound gracefully.
        logger.info("no audio backend available; sound disabled")
        return None


# Resolved once at import time.  None means sound is silently disabled.
_PLAYER = _make_player()


def _play(name: str) -> None:
    """Play the WAV file named `name` from the assets/sounds directory.

    Silently no-ops if:
      - _PLAYER is None (no audio backend available).
      - The file does not exist (logs a DEBUG message instead of raising).
      - Playback fails for any reason (logs a DEBUG message).

    Args:
        name: Filename including extension, e.g. "place.wav".
    """
    if _PLAYER is None:
        return  # audio disabled — do nothing

    path = ASSETS / name

    # Avoid crashing if an asset file is missing (e.g. clean checkout).
    if not path.exists():
        logger.debug("sound file missing: %s", path)
        return

    try:
        _PLAYER(path)
    except Exception as exc:  # noqa: BLE001 — catch-all so audio never crashes the game
        logger.debug("sound playback failed: %s", exc)


# ---------------------------------------------------------------------------
# Public playback functions
# ---------------------------------------------------------------------------

def play_place() -> None:
    """Play the disc-placement sound effect."""
    _play("place.wav")


def play_flip() -> None:
    """Play the disc-flip sound effect.

    Not currently called by default in the animation sequence, but available
    for future use or custom integrations.
    """
    _play("flip.wav")


def play_win() -> None:
    """Play the game-over / winner sound effect."""
    _play("win.wav")

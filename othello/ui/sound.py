import logging
import sys
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets" / "sounds"


def _make_player() -> Callable[[Path], None] | None:
    """Pick the first available audio backend, or None to disable sound."""
    # Windows stdlib — fastest and dependency-free.
    if sys.platform == "win32":
        try:
            import winsound

            def play_winsound(path: Path) -> None:
                winsound.PlaySound(
                    str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
                )

            return play_winsound
        except ImportError:
            pass

    # Cross-platform fallback.
    try:
        from playsound import playsound  # type: ignore[import-not-found]

        def play_playsound(path: Path) -> None:
            playsound(str(path), block=False)

        return play_playsound
    except ImportError:
        logger.info("no audio backend available; sound disabled")
        return None


_PLAYER = _make_player()


def _play(name: str) -> None:
    if _PLAYER is None:
        return
    path = ASSETS / name
    if not path.exists():
        logger.debug("sound file missing: %s", path)
        return
    try:
        _PLAYER(path)
    except Exception as exc:  # noqa: BLE001
        logger.debug("sound playback failed: %s", exc)


def play_place() -> None:
    _play("place.wav")


def play_flip() -> None:
    _play("flip.wav")


def play_win() -> None:
    _play("win.wav")

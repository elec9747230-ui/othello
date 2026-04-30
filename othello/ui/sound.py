import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets" / "sounds"

try:
    from playsound import playsound  # type: ignore[import-not-found]
    _PLAYSOUND_OK = True
except ImportError:
    _PLAYSOUND_OK = False
    logger.info("playsound not installed; sound disabled")


def _play(name: str) -> None:
    if not _PLAYSOUND_OK:
        return
    path = ASSETS / name
    if not path.exists():
        logger.debug("sound file missing: %s", path)
        return
    try:
        playsound(str(path), block=False)
    except Exception as exc:  # noqa: BLE001
        logger.debug("sound playback failed: %s", exc)


def play_place() -> None:
    _play("place.wav")


def play_flip() -> None:
    _play("flip.wav")


def play_win() -> None:
    _play("win.wav")

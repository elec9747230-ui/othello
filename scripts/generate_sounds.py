"""Generate the three game WAV files using only Python stdlib.

Run from project root: `python scripts/generate_sounds.py`
Outputs to assets/sounds/{place,flip,win}.wav.
"""
import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44100
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "sounds"


def _write_wav(path: Path, samples: list[float]) -> None:
    """Write a list of floats in [-1, 1] as a 16-bit mono WAV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # 16-bit
        w.setframerate(SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", max(-32767, min(32767, int(s * 32767))))
            for s in samples
        )
        w.writeframes(frames)


def _envelope(n: int, attack: float = 0.01, release: float = 0.7) -> list[float]:
    """Linear attack + exponential release envelope."""
    env = []
    attack_n = max(1, int(n * attack))
    for i in range(n):
        if i < attack_n:
            env.append(i / attack_n)
        else:
            t = (i - attack_n) / max(1, n - attack_n)
            env.append(math.exp(-t / release))
    return env


def _tone(freq: float, duration_s: float, amp: float = 0.6, harmonic_mix=(1.0, 0.3, 0.1)) -> list[float]:
    """Simple additive tone with harmonics + decay envelope."""
    n = int(SAMPLE_RATE * duration_s)
    env = _envelope(n)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        v = 0.0
        for k, weight in enumerate(harmonic_mix, start=1):
            v += weight * math.sin(2 * math.pi * freq * k * t)
        samples.append(amp * env[i] * v / sum(harmonic_mix))
    return samples


def _concat(*tracks: list[float]) -> list[float]:
    out: list[float] = []
    for t in tracks:
        out.extend(t)
    return out


def gen_place() -> None:
    # Short percussive "tock" — low-mid tone, very fast decay
    samples = _tone(440, 0.08, amp=0.7, harmonic_mix=(1.0, 0.5, 0.2))
    _write_wav(ASSETS / "place.wav", samples)


def gen_flip() -> None:
    # Higher, lighter "tick" with faster attack
    samples = _tone(880, 0.06, amp=0.5, harmonic_mix=(1.0, 0.3))
    _write_wav(ASSETS / "flip.wav", samples)


def gen_win() -> None:
    # Triumphant ascending arpeggio: C5 - E5 - G5 - C6
    notes = [523.25, 659.25, 783.99, 1046.50]
    pieces = [_tone(f, 0.18, amp=0.55, harmonic_mix=(1.0, 0.4, 0.15)) for f in notes]
    samples = _concat(*pieces)
    _write_wav(ASSETS / "win.wav", samples)


if __name__ == "__main__":
    gen_place()
    gen_flip()
    gen_win()
    for name in ("place.wav", "flip.wav", "win.wav"):
        p = ASSETS / name
        print(f"  {p.name}: {p.stat().st_size:,} bytes")
    print("done")

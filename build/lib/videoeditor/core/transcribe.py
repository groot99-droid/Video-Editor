"""Local Whisper transcription that emits ElevenLabs-Scribe-shaped JSON.

pack.py and render.py read `{"words": [{"type": "word"|"spacing", "text", "start", "end"}]}`.
Producing that shape here means they work unchanged on Whisper output.

Whisper tends to drop fillers ("um", "uh"); the initial prompt below nudges it to keep them,
but it is not a guarantee. Cuts around fillers are therefore less reliable than with Scribe.

CLI: `ve transcribe <video> [--edit-dir DIR] [--model base.en] [--language en]`.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

FILLER_PROMPT = "Um, uh, so, like, you know, I mean, hmm. Uh, well, okay."


def extract_audio(video: Path, wav: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)],
        check=True,
    )


def load_wav(path: Path) -> np.ndarray:
    """Read our own 16 kHz mono PCM16 WAV as float32. Handing Whisper an array also avoids PyAV decoding."""
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


def to_scribe_shape(segments, language: str, duration: float) -> dict:
    """Convert faster-whisper segments (with word timestamps) to the Scribe-like schema."""
    words: list[dict] = []
    prev_end: float | None = None
    for seg in segments:
        for w in seg.words or []:
            text = (w.word or "").strip()
            if not text:
                continue
            if prev_end is not None and w.start > prev_end:
                words.append({"type": "spacing", "text": " ", "start": round(prev_end, 3), "end": round(w.start, 3)})
            words.append({"type": "word", "text": text, "start": round(w.start, 3), "end": round(w.end, 3)})
            prev_end = w.end
    return {
        "language_code": language,
        "duration": duration,
        "text": " ".join(w["text"] for w in words if w["type"] == "word"),
        "words": words,
    }


def transcribe(
    video: Path,
    edit_dir: Path,
    model: str = "base.en",
    language: str | None = "en",
    vad_filter: bool = False,
    force: bool = False,
) -> Path:
    """Transcribe `video` into <edit_dir>/transcripts/<stem>.json. Cached per source file."""
    out = edit_dir / "transcripts" / f"{video.stem}.json"
    if out.exists() and not force:
        if out.stat().st_mtime >= video.stat().st_mtime:
            print(f"cached: {out}")
            return out
    from faster_whisper import WhisperModel  # imported lazily: heavy, optional for non-speech recipes

    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "audio.wav"
        extract_audio(video, wav)
        wm = WhisperModel(model, device="cpu", compute_type="int8")
        segments, info = wm.transcribe(
            load_wav(wav),
            language=language,
            word_timestamps=True,
            initial_prompt=FILLER_PROMPT,
            vad_filter=vad_filter,
            condition_on_previous_text=False,
        )
        data = to_scribe_shape(list(segments), info.language, info.duration)  # list(): decoding is lazy
    out.write_text(json.dumps(data, indent=2))
    print(f"transcript -> {out} ({sum(1 for w in data['words'] if w['type'] == 'word')} words)")
    return out

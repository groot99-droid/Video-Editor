"""Zero-setup PIL overlay: an animated text card rendered to MP4 (ease_out_cubic slide + fade in)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from videoeditor.core.platform import find_font


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def render_text_card(text: str, out: Path, duration: float = 4.0, size: tuple[int, int] = (1920, 1080),
                     fps: int = 30, reveal: float = 0.6, font_size: int = 76,
                     bg: tuple[int, int, int] = (10, 10, 10), fg: tuple[int, int, int] = (255, 90, 0),
                     font_path: str | None = None) -> Path:
    """Render a centered text card. Explicit font path is used; a missing font is an error, not a silent fallback."""
    font_path = font_path or find_font("DejaVu Sans Mono", bold=True)
    if not font_path:
        raise SystemExit("no usable font found; pass --font /path/to/font.ttf")
    font = ImageFont.truetype(font_path, font_size)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = int(round(duration * fps))
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
           "-r", str(fps), "-i", "-", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
           "-t", f"{duration}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac",
           "-shortest", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    probe_draw = ImageDraw.Draw(Image.new("RGB", size))
    # anchor on the FULL string width so text does not drift as it animates
    tw = probe_draw.textlength(text, font=font)
    x0, y0 = (size[0] - tw) / 2, (size[1] - font_size) / 2
    for i in range(n):
        t = i / fps
        p = ease_out_cubic(min(1.0, t / reveal)) if reveal > 0 else 1.0
        img = Image.new("RGB", size, bg)
        layer = Image.new("RGB", size, bg)
        ImageDraw.Draw(layer).text((x0, y0 + (1 - p) * 40), text, font=font, fill=fg)
        img = Image.blend(img, layer, p)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed while encoding the overlay")
    return out

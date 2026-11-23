"""
ASCII art animator buat terminal.

  python ascii.py                      -> demo plasma (gak butuh file apa-apa)
  python ascii.py foto.jpg             -> render gambar, sekali
  python ascii.py anim.gif             -> animasi loop
  python ascii.py video.mp4            -> animasi loop (butuh ffmpeg)
  python ascii.py anim.gif --width 120 --fps 20
  python ascii.py --once               -> cetak 1 frame demo, buat tes

Stop: Ctrl+C. Terminal: pakai Windows Terminal, teksnya kecilin (Ctrl+-).
"""
import os
import sys
import math
import time
import shutil
import colorsys
import tempfile
import subprocess

from PIL import Image, ImageSequence

if os.name == "nt":
    os.system("")  # nyalain ANSI escape di terminal Windows

RAMP = " .:-=+*#%@"
ASPECT = 0.5  # sel karakter ~2x tinggi -> tinggi grid dibagi 2 biar gak ketarik
HIDE, SHOW, HOME, CLEAR = "\x1b[?25l", "\x1b[?25h", "\x1b[H", "\x1b[2J"
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".flv"}

# 64 warna buat demo, dihitung sekali
PALETTE = [
    tuple(int(c * 255) for c in colorsys.hsv_to_rgb(i / 64, 0.75, 1.0))
    for i in range(64)
]


def grid_size(fallback_w=100):
    sz = shutil.get_terminal_size((fallback_w, 30))
    return max(20, sz.columns - 2), max(6, sz.lines - 2)


def demo_frame(w, h, t):
    """Plasma: gak butuh input, cuma sinus. Bagus buat tes + bikin konten."""
    rows = []
    cx, cy = w / 2, h / 2
    for y in range(h):
        out = []
        for x in range(w):
            n = (
                math.sin(x * 0.12 + t)
                + math.sin(y * 0.16 - t * 0.8)
                + math.sin((x + y) * 0.08 + t * 0.5)
                + math.sin(math.hypot(x - cx, y - cy) * 0.18 - t * 1.2)
            )
            v = (n + 4) / 8
            r, g, b = PALETTE[int((x * 3 + y * 2 + t * 40) % 64)]
            out.append(f"\x1b[38;2;{r};{g};{b}m{RAMP[min(9, int(v * 10))]}")
        rows.append("".join(out) + "\x1b[0m")
    return "\n".join(rows)


def image_to_ascii(img, w, boost=1.0):
    h = max(1, int(img.height / img.width * w * ASPECT))
    img = img.convert("RGB").resize((w, h), Image.LANCZOS)
    px = img.load()
    rows = []
    for y in range(h):
        out = []
        for x in range(w):
            r, g, b = px[x, y]
            lum = min(1.0, (r * 0.299 + g * 0.587 + b * 0.114) / 256 * boost)
            out.append(f"\x1b[38;2;{r};{g};{b}m{RAMP[min(9, int(lum * 10))]}")
        rows.append("".join(out) + "\x1b[0m")
    return "\n".join(rows)


def load_frames(path, w, fps):
    """GIF/PNG/JPG lewat Pillow, video lewat ffmpeg (di-dump ke frame PNG)."""
    if os.path.splitext(path)[1].lower() not in VIDEO_EXT:
        img = Image.open(path)
        return [f.convert("RGB").copy() for f in ImageSequence.Iterator(img)]

    tmp = tempfile.mkdtemp(prefix="ascii-")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", path,
         "-vf", f"fps={fps},scale=480:-2", os.path.join(tmp, "%05d.png")],
        check=True,
    )
    names = sorted(os.listdir(tmp))
    return [Image.open(os.path.join(tmp, n)).convert("RGB") for n in names]


def play(frames, w, fps, once=False, boost=1.0):
    sys.stdout.write(CLEAR + HIDE)
    try:
        while True:
            for f in frames:
                if callable(f):
                    t = time.perf_counter()
                    size = grid_size()
                    frame = f(size[0], size[1], t)
                else:
                    frame = image_to_ascii(f, w, boost)
                sys.stdout.write(HOME + frame)
                sys.stdout.flush()
                if once:
                    return
                time.sleep(1 / fps)
            if not callable(frames[0]) and len(frames) == 1:
                return
    finally:
        sys.stdout.write(SHOW + "\n")


def main():
    args = sys.argv[1:]
    once = "--once" in args
    if once:
        args.remove("--once")

    def flag(name, default):
        if name in args:
            out = args[args.index(name) + 1]
            del args[args.index(name):args.index(name) + 2]
            return int(out)
        return default

    def fflag(name, default):
        if name in args:
            out = float(args[args.index(name) + 1])
            del args[args.index(name):args.index(name) + 2]
            return out
        return default

    fps = flag("--fps", 15)
    boost = fflag("--boost", 1.0)
    width = flag("--width", grid_size()[0])

    if once and not args:
        sys.stdout.write(CLEAR + HIDE)
        sys.stdout.write(demo_frame(*grid_size(), 1.5) + SHOW + "\n")
        return

    if not args:
        play([demo_frame], width, fps, once)
        return

    path = args[0]
    if not os.path.exists(path):
        sys.exit(f"file gak ada: {path}")

    frames = load_frames(path, width, fps)
    play(frames, width, fps, once)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()

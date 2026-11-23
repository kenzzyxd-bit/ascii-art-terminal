"""
ASCII art animator buat terminal.

  python ascii.py                          -> demo plasma
  python ascii.py --demo matrix            -> demo hujan karakter
  python ascii.py foto.jpg                 -> render gambar, sekali
  python ascii.py anim.gif                 -> animasi loop
  python ascii.py video.mp4                -> animasi loop (butuh ffmpeg)
  python ascii.py anim.gif --width 120 --fps 20
  python ascii.py --once --demo matrix     -> cetak 1 frame (buat tes/screenshot)

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

try:
    sys.stdout.reconfigure(encoding="utf-8")  # katakana + escape aman walau output di-pipe
except (AttributeError, ValueError):
    pass

RAMP = " .:-=+*#%@"
ASPECT = 0.5  # sel karakter ~2x tinggi -> tinggi grid dibagi 2 biar gak ketarik
HIDE, SHOW, HOME, CLEAR = "\x1b[?25l", "\x1b[?25h", "\x1b[H", "\x1b[2J"
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".flv"}


def grid_size(fallback_w=100):
    sz = shutil.get_terminal_size((fallback_w, 30))
    return max(20, sz.columns - 2), max(6, sz.lines - 2)


# Palet: 24 hue x 32 tingkat terang. Di-precompute biar lookup-nya murah.
def _build_pal(hue0, hue1, sat=0.8):
    out = []
    for i in range(24):
        h = hue0 + (hue1 - hue0) * i / 23
        out.append(
            [
                tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h % 1.0, sat, 0.10 + 0.90 * v / 31))
                for v in range(32)
            ]
        )
    return out


PAL_RAINBOW = _build_pal(0.0, 1.0)


def _cell(rgb, ch):
    return f"\x1b[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{ch}"


def demo_frame(w, h, t):
    """Plasma halus: gelombang besar, warna ikut terang-gelap (bukan confetti)."""
    rows = []
    cx, cy = w / 2, h / 2
    for y in range(h):
        out = []
        for x in range(w):
            n = (
                math.sin(x * 0.07 + t * 0.9)
                + math.sin(y * 0.11 - t * 0.7)
                + math.sin((x + y) * 0.05 + t * 0.45)
                + math.sin(math.hypot(x - cx, y - cy) * 0.11 - t)
            )
            v = (n + 4) / 8
            hi = int((x * 0.5 + y * 0.35 + v * 14 + t * 6) % 24)
            out.append(_cell(PAL_RAINBOW[hi][min(31, int(v * 31))], RAMP[min(9, int(v * 9.99))]))
        rows.append("".join(out) + "\x1b[0m")
    return "\n".join(rows)


MATRIX_GLYPH = "01ｱｲｳｴｵｶｷｸ<>[]{}=+*#%&@"


def demo_matrix(w, h, t):
    """Hujan karakter hijau, tiap kolom beda kecepatan + ekor yang memudar."""
    rows = []
    n_glyph = len(MATRIX_GLYPH)
    for y in range(h):
        out = []
        for x in range(w):
            speed = 7 + (x * 37 % 9)
            head = (t * speed + (x * 101 % 61)) % (h + 14)
            d = head - y
            if 0 <= d < 13:
                fade = 1 - d / 13
                if d < 1:
                    rgb = (215, 255, 220)
                else:
                    rgb = (0, int(35 + 205 * fade * fade), int(25 + 105 * fade))
                ch = MATRIX_GLYPH[(x * 7 + y * 13 + int(t * speed)) % n_glyph]
            else:
                rgb, ch = (0, 26, 12), " "
            out.append(_cell(rgb, ch))
        rows.append("".join(out) + "\x1b[0m")
    return "\n".join(rows)


DEMOS = {"plasma": demo_frame, "matrix": demo_matrix}



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

    demo = "plasma"
    if "--demo" in args:
        demo = args[args.index("--demo") + 1]
        del args[args.index("--demo"):args.index("--demo") + 2]
    if demo not in DEMOS:
        sys.exit(f"demo gak ada: {demo} (pilihan: {', '.join(DEMOS)})")
    scene = DEMOS[demo]

    if once and not args:
        sys.stdout.write(CLEAR + HIDE)
        sys.stdout.write(scene(*grid_size(), 1.5) + SHOW + "\n")
        return

    if not args:
        play([scene], width, fps, once)
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

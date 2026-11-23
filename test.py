"""Cek cepat: py -3 test.py"""
from PIL import Image
import ascii as A

f = A.demo_frame(40, 12, 0.5).split("\n")
assert len(f) == 12, "demo harus 12 baris"
assert all("\x1b[38;2;" in row for row in f), "tiap baris harus ada warna truecolor"

white = A.image_to_ascii(Image.new("RGB", (64, 64), (255, 255, 255)), 40)
assert len(white.split("\n")) == 20, "tinggi grid = 40 * 0.5"
assert "@" in white, "putih penuh harus jadi karakter paling padat"

black = A.image_to_ascii(Image.new("RGB", (64, 64), (0, 0, 0)), 40)
plain = black.replace("\x1b[38;2;0;0;0m", "").replace("\x1b[0m", "")
assert set(plain) == {" ", "\n"}, "hitam = spasi"

print("ok")

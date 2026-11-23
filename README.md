# ASCII Art Terminal

[![tests](https://github.com/reyzdev/ascii-art-terminal/actions/workflows/tests.yml/badge.svg)](https://github.com/reyzdev/ascii-art-terminal/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

Convert gambar, GIF, atau video jadi **ASCII art berwarna** yang jalan animasi langsung di terminal.

Ditulis dengan Python + Pillow, output pakai **ANSI truecolor 24-bit**.

![demo: plasma, matrix, planet](docs/demo.png)

Empat demo bawaan. Statis (atas ke bawah): **plasma**, **matrix**, **planet**. Animasi:

![demo tunnel](docs/demo.gif)

**tunnel** — lorong 3D berwarna yang bergerak ke dalam.

## Fitur

- **Empat mode demo** tanpa file: plasma (gelombang halus), matrix (hujan karakter), planet (bola 3D + cincin), tunnel (lorong 3D) — semua murni matematika
- **Gambar / GIF / PNG / JPG** — dibaca lewat Pillow
- **Video (MP4/MKV/WebM/MOV)** — frame diambil lewat `ffmpeg`
- **Truecolor ANSI** `\x1b[38;2;R;G;Bm`, bukan 256 warna
- **Rasio karakter dikoreksi** (sel terminal ~2× tinggi) biar gambar gak ketarik
- `--boost` buat gambar gelap, `--width` & `--fps` buat atur ukuran dan kecepatan

## Instalasi

```bash
pip install pillow          # wajib
ffmpeg                      # opsional, cuma buat video
```

## Pemakaian

```bash
python ascii.py                          # demo plasma
python ascii.py --demo matrix            # demo hujan karakter
python ascii.py --demo planet            # demo planet 3D
python ascii.py --demo tunnel            # demo lorong 3D
python ascii.py foto.jpg                 # render sekali
python ascii.py anim.gif                 # animasi loop
python ascii.py video.mp4                # video, lewat ffmpeg
python ascii.py foto.jpg --boost 2       # gambar gelap biar lebih kebaca
python ascii.py anim.gif --width 120 --fps 20
python ascii.py --once --demo planet     # cetak 1 frame (buat tes/screenshot)
```

Stop: `Ctrl+C`.

Windows: jalankan di **Windows Terminal** (truecolor gak jalan di `cmd.exe` lama), atau double-click `run.bat`.

## Contoh: gambar → ASCII

Input `docs/sample.png`, hasilnya (warna asli dari gambar):

| Gambar asli | Hasil ASCII |
|---|---|
| <img src="docs/sample.png" width="330" alt="sample" /> | <img src="docs/sample-ascii.png" width="470" alt="hasil ascii" /> |

```bash
python ascii.py docs/sample.png
```

Tips: gambar dengan latar gelap perlu `--boost 2` biar bagian gelapnya tetap kebaca.

## Cara kerja

1. Frame diperkecil jadi grid ± lebar terminal × 0.5 (koreksi aspek karakter)
2. Terang tiap piksel (0.299R + 0.587G + 0.114B) dipetakan ke ramp `" .:-=+*#%@"`
3. Tiap karakter diwarnai sesuai piksel aslinya, satu string per baris
4. Frame ditulis setelah `\x1b[H` (kursor balik ke atas) → jadi animasi

Demo dibuat murni dari matematika (sinus + vektor), bukan file gambar, jadi tetap ringan. Performa di laptop uji: plasma ~5.6 ms/frame, matrix ~3.4 ms, planet ~6.3 ms, tunnel ~6.0 ms (118×28 kolom, >150 fps di Python murni).

## Struktur

```
ascii.py            script utama
test.py             cek cepat (assert): py -3 test.py -> ok
run.bat             launcher Windows (auto-install Pillow)
docs/               gambar demo untuk README
```

## Lisensi

MIT — lihat [LICENSE](LICENSE).

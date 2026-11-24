"""Draws the part-filter icons: a lander on its legs. usage: make_icon.py <out dir>"""
import os, sys
from PIL import Image, ImageDraw
S = 1024; out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for n, rgb in (('STMS_N', (255, 255, 255)), ('STMS_S', (25, 25, 25))):
    a = Image.new('L', (S, S), 0); d = ImageDraw.Draw(a); c = S / 2; w = 150
    pts = [(c - w, 800), (c - w, 360)] + [(c - w * (1 - t / 20) ** .62, 360 - 300 * t / 20) for t in range(21)]
    d.polygon(pts + [(2 * c - x, y) for x, y in pts[::-1]], fill=255)
    d.rectangle((c - w, 430, c + w, 500), fill=0)                       # thruster band
    for k in range(4): d.rounded_rectangle((c - 108 + k * 58, 330, c - 66 + k * 58, 388), 12, fill=0)
    for s in (-1, 1):                                                   # legs and pads
        d.line([(c + s * w, 640), (c + s * 330, 930)], fill=255, width=52); d.line([(c + s * w, 790), (c + s * 265, 840)], fill=255, width=40)
        d.rounded_rectangle((c + s * 330 - 100, 915, c + s * 330 + 100, 968), 20, fill=255)
    a = a.resize((64, 64), Image.LANCZOS); im = Image.new('RGBA', (64, 64), rgb + (0,)); im.putalpha(a); im.save(os.path.join(out, n + '.png'))

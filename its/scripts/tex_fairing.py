"""Fairing sheet, in the manner of BDB's Atlas V fairings: warm satin white, thin seams with bolted clips where they cross, vents, access doors."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl, fairing_layout as F
from texcommon import line
W = 2048; c = tl.Canvas(W, albedo=(.80, .795, .78), gloss=.30); X, Y = c.x, c.y
cl = np.kron(tl._fbm(1024, 1024, 3, base=4, octaves=5), np.ones((2, 2))); fn = np.kron(tl._fbm(1024, 1024, 8, base=70, octaves=2), np.ones((2, 2)))
c.albedo *= (1 + .010 * cl + .003 * fn)[..., None]; c.gloss += .020 * cl + .012 * fn
h = np.zeros((W, W), np.float32)
def seam(d, w=1.6, dark=.16, dep=.9):
    k = line(d, w, .8); c.albedo[:] *= (1 - dark * k)[..., None]; h[:] -= dep * k
    c.albedo[:] *= (1 - .035 * np.exp(-(d / 14) ** 2))[..., None]
def dots(pts, r=3.2):
    for x, y in pts:
        s = (slice(max(0, int(y) - 10), int(y) + 11), slice(max(0, int(x) - 10), int(x) + 11)); d = np.hypot(X[s] - x, Y[s] - y); k = np.clip(r + .5 - d, 0, 1); c.albedo[s] *= (1 - .30 * k)[..., None]; h[s] += .9 * k
def door(x, y, w, hh, r):
    d = tl.sd_rrect(X, Y, x, y, w, hh, r); k = np.exp(-(d / 2.0) ** 2); c.albedo[:] *= (1 - .22 * k)[..., None]; h[:] += 1.6 * np.clip(-d / 6, 0, 1) - 1.0 * k; c.albedo[:] *= (1 - .05 * np.exp(-(np.clip(d, 0, 99) / 10) ** 2) * (d > 0))[..., None]
    n = max(6, int((w + hh) / 22))
    for t in np.linspace(0, 2 * np.pi, n, endpoint=False): pass
for y0, y1 in [v for k, v in F.ROWS.items() if k != 'cap']: seam(Y - y0 - 2, 1.6); seam(Y - y1 + 2, 1.6)
for x in (3, W - 3): seam(X - x, 2.2, .22)                        # the split between halves
seam((X - W / 2) * ((Y < F.ROWS['base'][0])), 1.2, .10) if False else None
for x in (W * .25, W * .75):
    m = (Y > F.ROWS['cone'][0]) & (Y < F.ROWS['wall'][1]); d = np.where(m, X - x, 99); seam(d, 1.2, .09, .5)
for k in ('cone', 'wall', 'base'):                                # bolted clips where seams cross
    for y in (F.ROWS[k][0] + 10, F.ROWS[k][1] - 10):
        for x in (14, W * .25, W * .5, W * .75, W - 14): dots([(x + dx, y + dy) for dx in (-9, 9) for dy in (-5, 5)])
        dots([(x, y + (3 if y < F.ROWS[k][0] + 20 else -3)) for x in np.arange(24, W, 32)], 1.5)
cy = (F.ROWS['cone'][0] + F.ROWS['cone'][1]) // 2; seam(np.where((Y > 0) & (Y < 1120), Y - 470, 99), 1.4, .14); dots([(x + dx, 470 + dy) for x in (14, W * .25, W * .5, W * .75, W - 14) for dx in (-9, 9) for dy in (-14, 14)])
b0, b1 = F.ROWS['base']; bm = (b0 + b1) / 2
for x, y, w, hh, r in ((330, bm + 70, 62, 34, 30), (1130, bm + 60, 80, 42, 38), (1690, bm + 70, 62, 34, 30), (760, bm - 60, 34, 34, 34), (1440, bm - 70, 34, 34, 34)): door(x, y, w, hh, r); dots([(x + (w + 9) * np.cos(t) if r >= hh - 5 and w == hh else x + np.sign(np.cos(t)) * min(abs((w + 9) * np.cos(t) * 1.3), w + 9), y + np.sign(np.sin(t)) * min(abs((hh + 9) * np.sin(t) * 1.3), hh + 9)) for t in np.linspace(0, 2 * np.pi, 12, endpoint=False)], 1.8)
w0, w1 = F.ROWS['wall']
door(560, (w0 + w1) / 2, 34, 34, 34); door(1300, (w0 + w1) / 2 + 40, 30, 30, 30)
for x in np.arange(200, 1900, 180):                                # vent ports low on the base
    s = np.abs(X - x) < 24; d = tl.sd_rrect(X, Y, x, b1 - 40, 22, 10, 8); k = tl.fill(d); c.albedo[:] = c.albedo * (1 - .45 * k[..., None]); h[:] -= 1.0 * k
c.height[:] = h; c.save('stms_fairing', nstrength=.5)

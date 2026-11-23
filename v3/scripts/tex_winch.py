"""Paints the winch sheet in SEP's palette: bright stainless with weld lines, dark fittings, grey wire rope."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from tl import *
import layout as L

c = Canvas(L.ATLAS, albedo=(.6, .6, .62), gloss=.3)


def zone(n, rgb, gloss):
    x, y, w, h = L.Z[n]
    c.albedo[y:y + h, x:x + w] = rgb; c.gloss[y:y + h, x:x + w] = gloss
    return x, y, w, h


def line(x0, y0, x1, y1, depth=1.4, dark=.72):
    c.height[y0:y1 + 1, x0:x1 + 1] -= depth; c.albedo[y0:y1 + 1, x0:x1 + 1] *= dark


x, y, w, h = zone('FRAME', (.68, .69, .71), .55)
for k in range(1, 4):
    line(x + k * 128, y, x + k * 128, y + h - 1); line(x, y + k * 128, x + w - 1, y + k * 128)
x, y, w, h = zone('DARK', (.07, .072, .08), .4)
for k in range(1, 8):
    line(x + k * 64, y, x + k * 64, y + h - 1, 1.0, .6)
x, y, w, h = zone('BRIGHT', (.80, .81, .83), .72)
for k in range(1, 4):
    line(x, y + k * 48, x + w - 1, y + k * 48, .8, .85)
x, y, w, h = zone('CABLE', (.30, .30, .31), .35)
c.height[y:y + h, x:x + w] += np.sin((c.x[y:y + h, x:x + w] + c.y[y:y + h, x:x + w]) * 1.6) * .8
# deck: dark tread with a light tie-down grid
x, y, w, h = zone('DECK', (.22, .225, .235), .28)
for j in range(y, y + h, 24):
    for i in range(x + ((j - y) // 24 % 2) * 12, x + w - 8, 24):
        c.height[j + 4:j + 8, i:i + 12] += 1.1
for k in range(0, 9):
    line(min(x + k * 128, x + w - 2), y, min(x + k * 128 + 1, x + w - 1), y + h - 1, 1.6, 1.8)
    line(x, min(y + k * 64, y + h - 2), x + w - 1, min(y + k * 64 + 1, y + h - 1), 1.6, 1.8)
c.ao[:] = 1
c.save('sep_cw', nstrength=1.0, cavity=.6)

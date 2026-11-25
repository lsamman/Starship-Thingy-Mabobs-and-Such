"""Depot steel: one texture repeat is eight welded rings by half the way round; each sheet a shade apart, with its vertical weld."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl
from texcommon import line, hash2
H, W = 2048, 2048; c = tl.Canvas(W, H, albedo=(.80, .80, .80), gloss=.80); v = (1 - c.y / H) * 8; row = np.floor(v); u = c.x / W * 3 + .5 * (row % 2) + .17 * (row % 3); col = np.floor(u) % 3
cl = np.kron(tl._fbm(W // 2, W // 2, 71, base=6, octaves=5), np.ones((2, 2), np.float32)); t = hash2(row, col, 91) - .5
c.albedo *= (1 + .030 * t + .012 * cl)[..., None]; c.gloss += .05 * t + .025 * cl
fu = u - np.floor(u); d = np.minimum(fu, 1 - fu) * 2.945; k = line(d, .008, .003); c.albedo *= (1 - .28 * k)[..., None]; c.gloss -= .12 * k
fv = v - row; d = np.minimum(fv, 1 - fv) * 1.1427; k2 = line(d, .012, .002); c.albedo *= (1 - .38 * k2)[..., None]; c.gloss -= .10 * k2
c.height[:] = -.15 * k; c.save('stms_depot', nstrength=.4)

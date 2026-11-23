"""Textures for the Block 3 nose window kit: dark satin frames, and glass with eight lit rooms behind it
(the ITS crew section's scheme: each pane picks one room, so lit and dark cabins differ)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from tl import *

c = Canvas(256, albedo=(.17, .175, .185), gloss=.42)
c.albedo *= (1 + .02 * fbm(256, 256, 11, base=6, octaves=4))[..., None]
c.save('stms_b3_kit', nstrength=.3)

S = 512
c = Canvas(S, S, albedo=(.018, .022, .028), gloss=.86); em = np.zeros((S, S, 3), np.float32)
X, Y = c.x / S, 1 - c.y / S
for i in range(8):
    x0, y0 = (i % 4) / 4, (i // 4) / 2; m = (X >= x0) & (X < x0 + .25) & (Y >= y0) & (Y < y0 + .5)
    a, b = (X - x0) / .25, (Y - y0) / .5
    lv = (.95, .25, .80, .55, .08, .90, .40, .70)[i]; tint = ((1, .84, .58), (.75, .86, 1), (1, .80, .50), (1, .9, .7), (.6, .7, .9), (1, .86, .62), (.8, .9, 1), (1, .78, .5))[i]
    l_ = lv * (.55 + .45 * np.exp(-((b - .9) / .35) ** 2)) * (1 - .5 * (b < .28) * ((a * 5 + i) % 1 < .6)) * (1 - .7 * ((np.abs(a - (.3 + .05 * i)) < .05) & (b < .62)))
    em += (m * l_)[..., None] * np.array(tint)
c.albedo += em * .05
c.save('stms_b3_glass')
write_emissive((np.clip(em, 0, 1) * 255).astype(np.uint8), 'stms_b3_glass_emit')

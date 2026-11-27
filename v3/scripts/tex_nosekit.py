"""Textures for the Block 3 nose window kit: dark satin frames, and the ITS crew section's glass: a lit observation
deck behind the big window, and eight rooms for the small panes (each picks one, so cabins differ)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from tl import *

c = Canvas(256, albedo=(.17, .175, .185), gloss=.42)
c.albedo *= (1 + .02 * fbm(256, 256, 11, base=6, octaves=4))[..., None]
c.save('stms_b3_kit', nstrength=.3)

# ablative coat for the camera housing on the step of SEP's extended ablative: SEP's ablative is a flat dark grey (27, 28, 27)
c = Canvas(64, albedo=(.106, .11, .106), gloss=.25)
c.albedo *= (1 + .04 * fbm(64, 64, 5, base=4, octaves=3))[..., None]
c.save('stms_cam_abl', nstrength=.4)

# the ITS glass sheet (its/scripts/tex_details.py): the big window's lit deck top left, eight rooms top right
S = 1024
c = Canvas(S, S, albedo=(.018, .022, .028), gloss=.86); em = np.zeros((S, S, 3), np.float32)
X, Y = c.x / S, 1 - c.y / S
nose = (X < .5) & (Y > .5); gx = (X - .02) / .46; gy = (Y - .52) / .46                   # the observation deck
lit = np.exp(-((gy - .02) / .22) ** 2) * .55 + np.exp(-((gx - .5) / .35) ** 2 - ((gy - .62) / .16) ** 2) * .25 + .10
ribs = (np.abs(((gx - .5) * 9) % 1 - .5) < .05) | (np.abs((gy * 6) % 1 - .5) < .05)
em += (nose * np.clip(lit * (1 - .45 * ribs), 0, 1))[..., None] * np.array((1.0, .86, .62))
for i in range(8):
    x0, y0 = .5 + (i % 4) / 8, .5 + (i // 4) / 4; m = (X >= x0) & (X < x0 + .125) & (Y >= y0) & (Y < y0 + .25)
    a, b = (X - x0) / .125, (Y - y0) / .25
    lv = (.95, .82, .80, .88, .78, .90, .85, .76)[i]; tint = ((1, .84, .58), (1, .86, .62), (1, .80, .50), (1, .88, .66), (1, .82, .54), (1, .86, .62), (1, .84, .60), (1, .78, .5))[i]
    l_ = lv * (.55 + .45 * np.exp(-((b - .9) / .35) ** 2)) * (1 - .5 * (b < .28) * ((a * 5 + i) % 1 < .6))
    em += (m * l_)[..., None] * np.array(tint)
c.albedo += em * .05
c.save('stms_b3_glass')
write_emissive((np.clip(em, 0, 1) * 255).astype(np.uint8), 'stms_b3_glass_emit')

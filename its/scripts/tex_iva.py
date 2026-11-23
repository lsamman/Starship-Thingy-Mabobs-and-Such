"""Interior sheet for the HLS and Block 3 crew cabins: white panels, padded hexagons, dark floor, upholstery, screens."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl
from texcommon import line, cells, hash2
from iva_layout import ZONES, ATLAS
W = ATLAS; c = tl.Canvas(W); em = np.zeros((W, W, 3), np.float32)


def z(k): x, y, w, h = ZONES[k]; yy, xx = np.mgrid[0:h, 0:w] + .5; return (slice(y, y + h), slice(x, x + w)), w, h, xx, yy
def fill(k, rgb, gl, seed=0, al=.006, gv=.015):
    s, w, h, xx, yy = z(k); n = np.kron(tl._fbm(512, 512, seed + 7, base=5, octaves=4), np.ones((2, 2)))[:h, :w]; c.albedo[s] = np.array(rgb, np.float32) * (1 + al * n)[..., None]; c.gloss[s] = gl + gv * n; return s, w, h, xx, yy
def seam(s, e, w=1.6, dark=.30, d=1.0): k = line(e, w, .8); c.albedo[s] *= (1 - dark * k)[..., None]; c.height[s] -= d * k


s, w, h, xx, yy = fill('panel', (.74, .74, .73), .22, 1)        # wall panels, four to the zone, split low and high
_, ex = cells(xx, w / 4, 0); _, ey = cells(yy, h / 2, 0); seam(s, np.minimum(ex, ey), 2.2, .34); ao = np.clip(np.minimum(ex, ey) / 26, 0, 1); c.albedo[s] *= (.95 + .05 * ao)[..., None]
dot = np.clip(3 - np.hypot(ex - 18, ey - 18), 0, 1); c.albedo[s] *= (1 - .30 * dot)[..., None]
k = line(np.abs(yy - h * .06), 5, 1) * (ex > 60); c.albedo[s] = c.albedo[s] * (1 - k[..., None]) + .12 * k[..., None]
s, w, h, xx, yy = fill('hex', (.70, .70, .69), .12, 2)           # quilted airlock padding
a = w / 4; r = a / np.sqrt(3); best = np.full(xx.shape, 1e9); second = np.full(xx.shape, 1e9)
for j in range(-1, int(h / (1.5 * r)) + 3):
    for i in range(-1, 6):
        d = np.hypot(xx - (i + .5 * (j % 2)) * a, yy - j * 1.5 * r); m = d < best; second = np.where(m, best, np.minimum(second, d)); best = np.where(m, d, best)
e = second - best; seam(s, e, 3, .34, 1.4); c.height[s] += 2.2 * np.clip(e / 40, 0, 1) ** .5; c.albedo[s] *= (.90 + .10 * np.clip(e / 34, 0, 1))[..., None]
s, w, h, xx, yy = fill('floor', (.085, .088, .092), .20, 3, .02)
_, ex = cells(xx, w / 4, 0); _, ey = cells(yy, h / 4, 0); seam(s, np.minimum(ex, ey), 1.8, .5); _, gx = cells(xx, 12, 0); _, gy = cells(yy, 12, 0); d = np.clip(2 - np.hypot(6 - gx, 6 - gy), 0, 1); c.height[s] += .5 * d; c.albedo[s] *= (1 + .15 * d)[..., None]
s, w, h, xx, yy = fill('ceil', (.70, .70, .70), .16, 4)           # tapered ceiling gores
_, ex = cells(xx, w / 4, 0); _, ey = cells(yy, h / 3, .5); seam(s, np.minimum(ex, ey), 2, .26)
s, w, h, xx, yy = fill('bench', (.20, .20, .215), .10, 5, .03)    # upholstery with channels
_, ex = cells(xx, w / 8, 0); seam(s, ex, 2.5, .45, 1.6); _, ey = cells(yy, h, 0); seam(s, ey - 10, 1.2, .2)
s, w, h, xx, yy = fill('wood', (.34, .255, .175), .22, 6, .05); g = np.sin(yy * .22 + 2.2 * np.sin(xx * .011) + tl._fbm(512, 512, 5, base=3)[:h, :w] * 2); c.albedo[s] *= (1 + .10 * g)[..., None]
s, w, h, xx, yy = fill('console', (.055, .057, .062), .34, 7); _, ex = cells(xx, w / 3, 0); seam(s, ex, 1.6, .5)
for q in range(3):                                               # blanks round the instruments
    for r_ in range(6): m = (np.abs(xx - (q + .5) * w / 3 - (r_ - 2.5) * 22) < 7) & (np.abs(yy - h * .86) < 7); c.albedo[s] = np.where(m[..., None], .14, c.albedo[s]); c.height[s] += m * .8
s, w, h, xx, yy = fill('door', (.62, .62, .61), .24, 8); d = tl.sd_rrect(xx, yy, w / 2, h / 2, w * .44, h * .46, w * .12); seam(s, np.abs(d), 4, .5, 1.5); d2 = tl.sd_rrect(xx, yy, w / 2, h / 2, w * .34, h * .36, w * .10); c.albedo[s] = np.where((d2 < 0)[..., None], np.array((.05, .05, .052)), c.albedo[s]); rr = np.hypot(xx - w / 2, yy - h / 2); th = np.arctan2(yy - h / 2, xx - w / 2); c.height[s] += (d2 < 0) * .8 * np.sin(th * 14); seam(s, np.abs(rr - w * .1), 3, .4)
s, w, h, xx, yy = fill('locker', (.64, .64, .635), .20, 9); _, ex = cells(xx, w / 3, 0); _, ey = cells(yy, h / 4, 0); e = np.minimum(ex, ey); seam(s, e, 2.2, .45, 1.2); c.albedo[s] = np.where(((np.abs(ey - h / 8) < 5) & (np.abs(ex - 26) < 16))[..., None], .13, c.albedo[s])
s, w, h, xx, yy = fill('curtain', (.23, .27, .33), .08, 10); g = np.sin(xx * 2 * np.pi / 22); c.albedo[s] *= (1 + .16 * g)[..., None]; c.height[s] += 1.2 * g
s, w, h, xx, yy = fill('suit', (.72, .72, .71), .12, 11); seam(s, np.abs((yy % 40) - 20), 1.5, .16)
for i, (k, rgb, gl) in enumerate((('white', (.76, .76, .75), .28), ('grey', (.40, .41, .42), .30), ('dark', (.10, .10, .105), .28), ('black', (.035, .035, .037), .25), ('metal', (.56, .57, .58), .50), ('led', (.95, .95, .92), .3),
                                   ('orange', (.62, .25, .06), .2), ('blue', (.10, .17, .30), .2), ('green', (.16, .28, .10), .1), ('pillow', (.66, .66, .64), .08), ('yellow', (.62, .47, .06), .3), ('red', (.48, .07, .06), .25))): fill(k, rgb, gl, 20 + i)
s, w, h, xx, yy = z('led'); em[s] = (1, .97, .90)
s, w, h, xx, yy = z('screen'); c.albedo[s] = .02; c.gloss[s] = .6                # four displays: attitude, orbit, plots, schematic
hw = w / 4
for i in range(4):
    x = (xx - i * hw) / hw; y = yy / h; m = (x >= .04) & (x < .96) & (y > .05) & (y < .95); col = np.zeros((*x.shape, 3), np.float32); col[...] = (.010, .016, .026)
    if i == 0: r_ = np.hypot(x - .5, (y - .5)); sky = (y < .5 + .12 * (x - .5)); col = np.where((r_ < .33)[..., None], np.where(sky[..., None], (.10, .30, .55), (.34, .20, .09)), col); col = np.where((np.abs(r_ - .33) < .012)[..., None], .8, col); col = np.where(((np.abs(y - .5) < .008) & (np.abs(x - .5) < .16))[..., None], (1, .8, .2), col)
    if i == 1: r_ = np.hypot(x - .5, y - .52); col = np.where((r_ < .15)[..., None], (.32, .32, .34), col); e = np.hypot((x - .56) / .36, (y - .5) / .27); col = np.where((np.abs(e - 1) < .035)[..., None], (.2, .8, 1), col)
    if i == 2:
        for q, cc in enumerate(((.2, .9, .5), (1, .7, .2), (.4, .6, 1))): f = .25 + .25 * q + .06 * np.sin(x * (9 + 5 * q) + q) + .02 * np.sin(x * 47); col = np.where((np.abs(y - f) < .008)[..., None], cc, col)
        col = np.where((((x * 8) % 1 < .03) | ((y * 8) % 1 < .03))[..., None], col + .03, col)
    if i == 3:
        b = (np.abs(x - .5) < .10 * np.clip(1.0 - np.clip(.36 - y, 0, 1) * 4.2, 0, 1)) & (y > .1) & (y < .86); col = np.where(b[..., None], (.55, .58, .62), col); col = np.where((b & (np.abs(y - .42) < .02))[..., None], (.1, .9, 1), col); t = (x > .7) & (x < .92) & (((y * 14) % 1) < .4) & (hash2(np.floor(y * 14), x * 0, 1) > .25) & (x < .7 + .22 * hash2(np.floor(y * 14), x * 0, 5)); col = np.where(t[..., None], (.3, .8, .9), col)
    em[s] = np.where(m[..., None], col, em[s])
c.albedo += em * .06 * (c.albedo < .2)
c.save('stms_iva', nstrength=.5); tl.write_emissive((np.clip(em, 0, 1) * 255).astype(np.uint8), 'stms_iva_emit')
g = np.zeros((64, 64, 4), np.uint8); g[...] = (150, 170, 180, 14); tl.write_dds(g, 'stms_ivaglass_diff', transparent=True)

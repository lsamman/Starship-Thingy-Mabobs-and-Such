"""Detail atlas, solar cells and lit glass."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl, layout as L
from PIL import Image, ImageDraw, ImageFont
from texcommon import line, cells, hash2
W = 2048
c = tl.Canvas(W); metal = np.zeros((W, W), np.float32)
X, Y = c.x, c.y


def zone(k):
    x, y, w, h = L.DET[k]; return (slice(y, y + h), slice(x, x + w)), w, h


def fill(k, rgb, gl, me=0.0, al=.008, gv=.014, seed=0, streak=None):
    s, w, h = zone(k); n = tl._fbm(512, 512, seed + 50, base=5, octaves=5)[:h, :w] if max(w, h) <= 512 else np.kron(tl._fbm(512, 512, seed + 50, base=4, octaves=5), np.ones((2, 2)))[:h, :w]
    f = tl._fbm(512, 512, seed + 90, base=90, octaves=2)
    f = np.tile(f, (2, 2))[:h, :w]
    if streak == 'y': f = tl.blur(f, 0) * 0 + np.repeat(tl.rng(seed).standard_normal((1, w)), h, 0)
    if streak == 'x': f = np.repeat(tl.rng(seed).standard_normal((h, 1)), w, 1)
    c.albedo[s] = np.array(rgb, np.float32) * (1 + al * n + al * .5 * f)[..., None]; c.gloss[s] = gl + gv * n + gv * .7 * f; metal[s] = me
    return s, w, h


fill('white', (.78, .78, .77), .44, seed=1)
fill('grey', (.42, .43, .44), .38, seed=2)
s, w, h = fill('carbon', (.075, .076, .080), .46, seed=3)
yy, xx = np.mgrid[0:h, 0:w]; tw = ((xx // 5 + yy // 5) % 4 < 2).astype(np.float32); c.albedo[s] *= (1 + .16 * (tw - .5))[..., None]; c.gloss[s] += .05 * (tw - .5)
fill('steel', (.56, .56, .55), .62, 1, al=.02, gv=.03, seed=4, streak='x')
fill('dark', (.105, .107, .112), .36, seed=5)
fill('alu', (.62, .63, .64), .50, 1, al=.015, gv=.03, seed=6, streak='x')
fill('black', (.048, .048, .05), .30, seed=7)
fill('invar', (.50, .49, .46), .55, 1, al=.02, gv=.03, seed=8)
s, w, h = fill('wall', (.40, .405, .41), .30, seed=9)      # inside of the composite shell: bonded panels, doublers, fasteners
yy, xx = np.mgrid[0:h, 0:w] + .5; _, ex = cells(xx, 256, 0); _, ey = cells(yy, 170.67, 0); e = np.minimum(ex, ey)
k = line(e, 1.4, .8); c.albedo[s] *= (1 - .35 * k)[..., None]; c.height[s] -= 1.2 * k
k2 = line(e - 12, .8, .8); c.albedo[s] *= (1 - .08 * k2)[..., None]; c.height[s] -= .3 * k2
_, fx = cells(xx, 21.333, 0); _, fy = cells(yy, 21.333, 0); dot = np.clip(2.1 - np.hypot(10.667 - fx, np.abs(ey - 6)), 0, 1) + np.clip(2.1 - np.hypot(10.667 - fy, np.abs(ex - 6)), 0, 1)
dot = np.clip(dot, 0, 1); c.albedo[s] *= (1 - .18 * dot)[..., None]; c.height[s] += .5 * dot
v = hash2(np.floor(xx / 256), np.floor(yy / 170.67), 3); c.albedo[s] *= (1 + .05 * (v - .5))[..., None]
s, w, h = fill('deck', (.23, .235, .24), .26, seed=10)     # floor: panels with grip dots
yy, xx = np.mgrid[0:h, 0:w] + .5; _, ex = cells(xx, 64, 0); _, ey = cells(yy, 64, 0); k = line(np.minimum(ex, ey), 1.2, .7); c.albedo[s] *= (1 - .45 * k)[..., None]; c.height[s] -= k
_, gx = cells(xx, 9.143, 0); _, gy = cells(yy, 9.143, 0); dot = np.clip(2.4 - np.hypot(4.57 - gx, 4.57 - gy), 0, 1) * (np.minimum(ex, ey) > 5); c.albedo[s] *= (1 + .18 * dot)[..., None]; c.height[s] += .6 * dot
s, w, h = zone('stripe'); yy, xx = np.mgrid[0:h, 0:w]; m = (((xx + yy) // 48) % 2).astype(np.float32)[..., None]; c.albedo[s] = m * np.array((.70, .50, .07)) + (1 - m) * .05; c.gloss[s] = .34
fill('hatch', (.74, .74, .73), .42, seed=11)
s, w, h = fill('pica', (.050, .049, .0475), .26, al=.05, gv=.03, seed=12)    # leg shells: blocks in true proportion
yy, xx = np.mgrid[0:h, 0:w] + .5; row = np.floor(yy / 64); col = np.floor(xx / 128 + .5 * (row % 2))
_, ey = cells(yy, 64, 0); fx = xx / 128 + .5 * (row % 2); fx = fx - np.floor(fx); ex = np.minimum(fx, 1 - fx) * 128; e = np.minimum(ex, ey)
g = line(e, 1.4, .8); vv = hash2(row, col, 4); c.albedo[s] *= (1 + .22 * (vv - .5))[..., None]; c.albedo[s] *= (1 - .55 * g)[..., None]; c.gloss[s] += .04 * (hash2(col, row, 6) - .5) - .1 * g; c.height[s] -= 1.4 * g
s, w, h = fill('dome', (.36, .365, .37), .34, seed=13)     # tank domes and bulkheads: gores and doublers
yy, xx = np.mgrid[0:h, 0:w] + .5; _, ex = cells(xx, 64, 0); _, ey = cells(yy, 128, .5); k = line(np.minimum(ex, ey), 1.1, .7); c.albedo[s] *= (1 - .32 * k)[..., None]; c.height[s] -= k
fill('copper', (.52, .30, .17), .52, 1, al=.03, seed=14); fill('rubber', (.045, .045, .045), .14, seed=15)
s, w, h = fill('cable', (.30, .31, .32), .45, 1, seed=16); yy, xx = np.mgrid[0:h, 0:w]; q = np.sin((xx * 1.0 + yy * 2.2) / 4.0); c.albedo[s] *= (1 + .25 * q)[..., None]; c.height[s] += .6 * q
s, w, h = zone('lamp'); c.albedo[s] = (.95, .95, .90); c.gloss[s] = .6
s, w, h = fill('label', (.78, .78, .77), .44, seed=17)
# flag, drawn at twice the size
fx, fy, fw, fh = L.FLAG; im = Image.new('RGB', (fw * 2, fh * 2), (255, 255, 255)); d = ImageDraw.Draw(im); FW, FH = fw * 2, fh * 2
for i in range(0, 13, 2): d.rectangle((0, round(i * FH / 13), FW, round((i + 1) * FH / 13) - 1), fill=(150, 26, 38))
d.rectangle((0, 0, FW * .4, round(7 * FH / 13) - 1), fill=(28, 38, 84))
for r in range(9):
    for q in range(6 if r % 2 == 0 else 5):
        sx = FW * .4 * ((q * 2 + 1 + (r % 2)) / 12); sy = 7 * FH / 13 * (r + 1) / 10; R = FH * .0155
        d.polygon([(sx + R * (1 if k % 2 == 0 else .40) * np.sin(np.pi * k / 5), sy - R * (1 if k % 2 == 0 else .40) * np.cos(np.pi * k / 5)) for k in range(10)], fill=(255, 255, 255))
f = np.asarray(im.resize((fw, fh), Image.LANCZOS)).astype(np.float32) / 255 * .80; c.albedo[fy:fy + fh, fx:fx + fw] = f; c.gloss[fy:fy + fh, fx:fx + fw] = .42
c.save('its_det', nstrength=.55)
tl.write_dds((np.dstack([metal, metal, metal, np.ones_like(metal)]) * 255).astype(np.uint8), 'its_det_metal')

# ---------------- solar petals: four panels, u across, v out along the petal
S, T_ = 512, 2048
c = tl.Canvas(S, T_, albedo=(.030, .036, .075), gloss=.62)
u = c.x / S; v = 1 - c.y / T_; k, ev = cells((v - .02) / .96 * 4, 1, 0)
fz = ((v - .02) / .96 * 4) % 1
_, ex = cells(c.x, 32, 0); _, ey = cells(c.y, 32, 0); cx, cy = np.floor(c.x / 32), np.floor(c.y / 32)
c.albedo *= (1 + .20 * (hash2(cx, cy, 1) - .5))[..., None]; c.gloss += .03 * (hash2(cy, cx, 2) - .5)
g = line(np.minimum(ex, ey), .9, .6); c.albedo[:] = c.albedo * (1 - g[..., None]) + np.array((.14, .15, .18)) * g[..., None]
bus = line(ex - 10, .5, .5); c.albedo[:] = c.albedo * (1 - .35 * bus[..., None]) + .25 * .35 * bus[..., None]
edge = np.clip(1 - ev / .012, 0, 1) ; c.albedo[:] = c.albedo * (1 - edge[..., None]) + np.array((.30, .22, .10)) * edge[..., None]
c.height[:] = -.6 * g
for m, rgb, gl in (((u < .25) & (v < .10), (.10, .10, .105), .35), ((u > .75) & (v < .10), (.40, .24, .12), .45)):      # frames; film on the back
    c.albedo[m] = rgb; c.gloss[m] = gl; c.height[m] = 0
c.save('its_solar', nstrength=.4)

# ---------------- glass: nose window on the left of the top half, eight rooms on its right
S = 1024
c = tl.Canvas(S, S, albedo=(.018, .022, .028), gloss=.86); em = np.zeros((S, S, 3), np.float32); X, Y = c.x / S, 1 - c.y / S
r = tl.rng(4)
nose = (X < .5) & (Y > .5); gx = (X - .02) / .46; gy = (Y - .52) / .46                   # the observation deck
lit = np.exp(-((gy - .02) / .22) ** 2) * .55 + np.exp(-((gx - .5) / .35) ** 2 - ((gy - .62) / .16) ** 2) * .25 + .10
ribs = (np.abs(((gx - .5) * 9) % 1 - .5) < .05) | (np.abs((gy * 6) % 1 - .5) < .05)
for i in range(9):                                                                       # people and planters along the rail
    px, ph = .08 + i * .105 + r.uniform(-.02, .02), r.uniform(.10, .16); m = (np.abs(gx - px) < .018) & (gy < ph) | (np.hypot(gx - px, (gy - ph - .02) * 1.0) < .02)
    lit = np.where(m, lit * .25, lit)
em += (nose * np.clip(lit * (1 - .45 * ribs), 0, 1))[..., None] * np.array((1.0, .86, .62))
for i in range(8):
    x0, y0 = .5 + (i % 4) / 8, .5 + (i // 4) / 4; m = (X >= x0) & (X < x0 + .125) & (Y >= y0) & (Y < y0 + .25)
    a, b = (X - x0) / .125, (Y - y0) / .25
    lv = (.95, .25, .80, .55, .08, .90, .40, .70)[i]; tint = ((1, .84, .58), (.75, .86, 1), (1, .80, .50), (1, .9, .7), (.6, .7, .9), (1, .86, .62), (.8, .9, 1), (1, .78, .5))[i]
    l_ = lv * (.55 + .45 * np.exp(-((b - .9) / .35) ** 2)) * (1 - .5 * (b < .28) * ((a * 5 + i) % 1 < .6)) * (1 - .7 * ((np.abs(a - (.3 + .05 * i)) < .05) & (b < .62)))
    em += (m * l_)[..., None] * np.array(tint)
c.albedo += em * .05
c.save('its_glass')
tl.write_emissive((np.clip(em, 0, 1) * 255).astype(np.uint8), 'its_glass_emit')

"""HLS engine bay: the aft bulkhead seen from below, planar (6.6 m a side): puck, cone and flat ring of heat-tinted steel, with welds.
The corners outside the disk are plain swatches: dark steel, straw-tinted steel, black, bright steel."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl
from texcommon import line
N = 2048; c = tl.Canvas(N, N, albedo=(.5, .5, .5), gloss=.62); X = (c.x / N - .5) * 6.6; Y = (.5 - c.y / N) * 6.6; r = np.hypot(X, Y); a = np.arctan2(X, -Y)
f = lambda s, b, o=5: np.kron(tl._fbm(N // 2, N // 2, s, base=b, octaves=o), np.ones((2, 2), np.float32))
n1, n2, n3 = f(301, 5), f(302, 14), f(303, 40, 4)
gold, grey, dark = (np.array(q, np.float32) for q in ((.56, .475, .31), (.44, .425, .39), (.27, .265, .26)))
mix = lambda p, q, t: p * (1 - t[..., None]) + q * t[..., None]
straw = mix(gold, grey, np.clip(.38 + .30 * n1 + .16 * n2 + .10 * n3, 0, .85)); drk = mix(dark, dark * 1.5, np.clip(.4 + .6 * n1 + .3 * n2, 0, 1)); drk = mix(drk, gold * .7, np.clip(n1 * .9 - .25, 0, .35))
ins = r < 1.09; cone = (r >= 1.09) & (r < 1.98)
c.albedo[:] = np.where(cone[..., None], drk, straw) * (1 + .03 * n3)[..., None]; c.gloss += .05 * n2 + .03 * n3 - .04 * cone
soot = np.clip(1 - np.abs(r - 1.5) / 1.6, 0, 1) * .12; c.albedo *= (1 - soot * (1 + n1))[..., None]
w = np.zeros((N, N), np.float32)
for k in range(12):                                  # radial welds: twelve in the ring, six in the cone
    d = np.abs(np.sin(a - np.radians(15 + 30 * k))) * r; w = np.maximum(w, line(d, .009, .004) * (np.cos(a - np.radians(15 + 30 * k)) > 0) * ((r > 2.0) | (cone & (k % 2 == 0))))
for q in (1.09, 1.98): w = np.maximum(w, line(np.abs(r - q), .014, .005))
c.albedo *= (1 - .35 * w)[..., None]; c.gloss -= .12 * w
c.height[:] = .5 * w + np.where(cone, 1.6 * n2 + .5 * n3, np.where(ins, .15 * n2, .7 * n2 + .2 * n3)) * 1.2        # thin sheet, a little wavy
s = int(N * .115)
for (ys, xs), col, g in (((slice(0, s), slice(0, s)), dark * 1.15, .66), ((slice(0, s), slice(N - s, N)), gold * .92, .60), ((slice(N - s, N), slice(0, s)), dark * .25, .35), ((slice(N - s, N), slice(N - s, N)), grey * 1.15, .70)):
    c.albedo[ys, xs] = col * (1 + .05 * n3[ys, xs] + .04 * n2[ys, xs])[..., None]; c.gloss[ys, xs] = g + .04 * n3[ys, xs]; c.height[ys, xs] = 0
c.save('hls_aft', nstrength=.5)

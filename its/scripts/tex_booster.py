"""Booster sheet: 120 degrees repeated three times, in two strips (layout.b_uv). Painted twice: white, then the
bare-carbon livery (its_booster_carbon_diff, sharing the white sheet's normal map)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl, layout as L, carbon as CF
W = int(os.environ.get('ITS_HULL', 4096))
from texcommon import line, cells, hash2


def paint(carbon=False):
    c = tl.Canvas(W, W, albedo=CF.RGB if carbon else (.80, .80, .79), gloss=.46)
    u = c.x / W; v = 1 - c.y / W
    strip = (u >= .5).astype(np.int32)
    az = (u - strip * .5 - L.B_PAD) / (.5 - 2 * L.B_PAD) * 120
    t = (v - L.B_PAD) / (1 - 2 * L.B_PAD)
    z0 = np.where(strip == 0, L.B_STRIP[0][0], L.B_STRIP[1][0]); z1 = np.where(strip == 0, L.B_STRIP[0][1], L.B_STRIP[1][1])
    z = (z0 + (z1 - z0) * t).astype(np.float32); a = ((az + 60) % 120 - 60).astype(np.float32)          # 0 = fairing and fin, +-60 = raceway
    x = np.radians(az).astype(np.float32) * 6.0; xs = np.radians(a) * 6.0
    mpp = 38.45 / W; aa = mpp * .7
    def noise(seed, base, o=4, g=.5):
        return np.kron(tl._fbm(W // 2, W // 2, seed, base=base, octaves=o, gain=g), np.ones((2, 2), np.float32))
    cloud, fine = noise(3, 5, 5, .6), noise(4, 40)
    if carbon:
        CF.base(c, x, z, cloud, fine, period=np.radians(120) * 6.0)
    else:
        c.albedo *= (1 + .010 * cloud + .004 * fine)[..., None]
        course = np.floor(z / .44)
        c.gloss += .012 * cloud + .010 * fine + .012 * (hash2(course, course * 0 + strip, 7) - .5)
    h = np.zeros((W, W), np.float32)
    def ringseam(zz, strap=.2, dots=True, dark=.42):
        nonlocal h
        d = z - zz; k = line(d, .013, aa)
        if carbon:
            CF.seam(c, k)
        else:
            c.albedo[:] *= (1 - dark * k)[..., None]
        h -= 1.3 * k
        st = (np.abs(d) < strap).astype(np.float32)
        if carbon:
            CF.strap(c, st)
        else:
            c.gloss[:] -= .05 * st; c.albedo[:] *= (1 - .022 * st)[..., None]
        e = line(np.abs(d) - strap, .005, aa)
        if carbon:
            CF.seam(c, e * .3)
        else:
            c.albedo[:] *= (1 - .10 * e)[..., None]
        h -= .25 * e
        if dots:
            _, ex = cells(x, 2 * np.pi * 2 / 60, .5); fx = np.pi * 2 / 60 - ex
            for o in (-strap * .55, strap * .55):
                dot = np.clip(.5 + (.018 - np.hypot(fx, d - o)) / (2 * aa), 0, 1)
                if carbon:
                    CF.fastener(c, dot)
                else:
                    c.albedo[:] *= (1 - .16 * dot)[..., None]; c.gloss[:] -= .08 * dot
                h -= .35 * dot
    for zz in (3.2, 11.6, 19.6, 28.4, 38.9, 47.6, 56.2, 63.6, 72.0):
        ringseam(zz, .30 if zz in (3.2, 72.0) else .16)
    for aa_, za, zb in ((-30, 3.2, 19.6), (30, 19.6, 38.9), (-30, 38.9, 56.2), (30, 56.2, 72.0)):
        k = line(np.radians(a - aa_) * 6, .011, aa) * ((z > za) & (z < zb))
        if carbon:
            CF.seam(c, k * .85)
        else:
            c.albedo *= (1 - .34 * k)[..., None]
        h -= k
    # base: black heat-soaked ring and a grey closeout; scuff plate under the stowed grid fin; dark rim at the interstage lip
    def band(m, rgb, gl):
        m = m.astype(np.float32); c.albedo[:] = c.albedo * (1 - m[..., None]) + np.array(rgb, np.float32) * m[..., None]; c.gloss[:] = c.gloss * (1 - m) + gl * m
    blk = np.clip(.5 + (1.9 - z) / (2 * aa), 0, 1); band(blk, (.06, .06, .062), .34)
    k = line(z - 1.9, .014, aa); h -= k; c.albedo *= (1 - .5 * k)[..., None]
    _, ex = cells(x, 2 * np.pi * 2 / 24, 0); g = line(ex, .012, aa) * blk; c.albedo *= (1 - .4 * g)[..., None]; h -= g
    sd = np.maximum(np.abs(xs) - 1.75, np.abs(z - 62.6) - 3.7); sd2 = np.hypot(np.maximum(np.abs(xs) - 1.45, 0), np.maximum(np.abs(z - 62.6) - 3.4, 0)) - .3
    m = np.clip(.5 - sd2 / (2 * aa), 0, 1); band(m * .85, (.50, .505, .51), .40); k = line(sd2, .012, aa); h -= .9 * k; c.albedo *= (1 - .35 * k)[..., None]
    # soft contact shading around the base fairings, raceways and hinge fairing
    sh = np.exp(-np.maximum(np.abs(xs) - .9, 0) / .7) * np.clip((11.2 - z) / 3, 0, 1) * .10 + np.exp(-np.maximum(np.abs(np.abs(xs) - 2 * np.pi) - .36, 0) / .22) * ((z > 3.4) & (z < 59.1)) * .12
    sh = sh + np.exp(-np.maximum(np.abs(xs) - 1.7, 0) / .5) * np.clip((z - 65.8) / .4, 0, 1) * np.clip((71.4 - z) / 2, 0, 1) * .07
    c.albedo *= (1 - sh)[..., None].astype(np.float32)
    c.height[:] = h
    if carbon:
        c.save('its_booster_carbon', nstrength=.55, nrm=False)
    else:
        c.save('its_booster', nstrength=.55)


paint(False)
paint(True)

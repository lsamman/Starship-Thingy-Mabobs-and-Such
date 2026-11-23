"""Ship hull sheets: white-painted carbon composite to leeward, PICA blocks to windward. Half a hull, mirrored, so no text."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl, hull as H
W = int(os.environ.get('ITS_HULL', 4096))
sm = tl.smooth


def line(d, w, aa):
    return np.clip(.5 + (w - np.abs(d)) / (2 * aa), 0, 1).astype(np.float32)


def noise(seed, base, oct_=4, gain=.5):
    n = tl._fbm(W // 2, W // 2, seed, base=base, octaves=oct_, gain=gain)
    return np.kron(n, np.ones((2, 2), np.float32))


def cells(s, pitch, off):
    """Cell index, and distance to the nearest edge, for a 1D pitch."""
    k = np.floor(s / pitch + off); f = s / pitch + off - k
    return k, np.minimum(f, 1 - f) * pitch


def hash2(a, b, seed):
    v = np.sin(a * 127.1 + b * 311.7 + seed * 74.7) * 43758.5453
    return (v - np.floor(v)).astype(np.float32)


def build(sheet, seams, long_seams, seed):
    az, z = H.grid(W, W, sheet)
    z = np.clip(z, H.Z_WIND - .2, H.Z_TIP - .004)
    r = np.where(z > H.Z_TAN, H.body_r(z), H.RB).astype(np.float32)
    z0, z1 = H.SHEET[sheet]
    mpp = (H.arc(z1) - H.arc(z0)) / (W * (1 - 2 * H.PAD))          # real metres per pixel, along the meridian
    aa = mpp * .7
    s = H.arc(z).astype(np.float32); x = np.radians(az).astype(np.float32) * r
    d = H.paint_d(az, z).astype(np.float32)
    white = np.clip(.5 + d / (2 * aa), 0, 1).astype(np.float32); pica = 1 - white
    c = tl.Canvas(W, W, albedo=(.80, .80, .79), gloss=.47)
    cloud = noise(seed, 5, 5, .6); fine = noise(seed + 1, 40, 4)
    # ---------------- white composite: long barrels, few joints; tape-laid courses and buffing only in the gloss
    c.albedo *= (1 + .010 * cloud + .004 * fine)[..., None]
    tape = np.floor((x + s * .36) / .42); tape2 = np.floor((x - s * .36) / .42)
    c.gloss += .012 * cloud + .010 * fine + .010 * (hash2(tape, tape * 0, 1) - .5) + .008 * (hash2(tape2, tape2 * 0, 2) - .5)
    h = np.zeros((W, W), np.float32)
    for zz in seams:
        dd = s - H.arc(zz); k = line(dd, .012, aa)
        c.albedo *= (1 - .42 * k * white)[..., None]; h -= 1.3 * k * white
        band = np.clip(1 - np.abs(dd) / .16, 0, 1)                  # joint strap, a touch glossier, ringed by flush fasteners
        strap = (np.abs(dd) < .16).astype(np.float32) * white
        c.gloss -= .05 * strap; c.albedo *= (1 - .022 * strap)[..., None]
        edge = line(np.abs(dd) - .16, .005, aa) * white
        c.albedo *= (1 - .10 * edge)[..., None]; h -= .25 * edge
        _, ex = cells(x, .22, .5); fx = .11 - ex
        for o in (-.09, .09):
            dot = np.clip(.5 + (.016 - np.hypot(fx, dd - o)) / (2 * aa), 0, 1) * white
            c.albedo *= (1 - .16 * dot)[..., None]; h -= .35 * dot; c.gloss -= .08 * dot
    for a_, za, zb in long_seams:
        dd = np.radians(az - a_) * r; k = line(dd, .010, aa) * ((z > za) & (z < zb)) * white
        c.albedo *= (1 - .34 * k)[..., None]; h -= 1.0 * k
    # soft shading where the fairing flanks meet the barrel
    if sheet == 'aft' or True:
        pc, pt = H.angles(z); th = np.abs((az + 60) % 120 - 60); rr, _ = H.ridge(z)
        amp = np.clip((rr - H.RB) / 2.2, 0, 1)
        c.albedo *= (1 - .045 * amp * np.exp(-((th - pt) / 5.0) ** 2) * white + .02 * amp * np.exp(-((th - pc) / 1.6) ** 2) * white)[..., None].astype(np.float32)
    # ---------------- PICA blocks: large staggered tiles, pitch halving as the nose narrows
    n = np.where(r > 3.6, 24, np.where(r > 1.7, 12, np.where(r > .75, 6, 3))).astype(np.float32)
    row, er = cells(s, .86, .13)
    col, ec = cells(az, 180.0 / n, .5 * (row % 2)); ec = np.radians(ec) * r
    e = np.minimum(er, ec)
    gap = np.clip(.5 + (.011 - e) / (2 * aa), 0, 1).astype(np.float32)
    v = hash2(row, col + n * 3, seed); v2 = hash2(col, row + n, seed + 5)
    pal = np.empty((W, W, 3), np.float32); base = .050 + .012 * (v - .5) + .004 * cloud + .003 * fine
    pal[..., 0] = base * 1.02; pal[..., 1] = base; pal[..., 2] = base * .97
    pal *= (1 - .55 * gap)[..., None]
    pal += (.006 * np.clip(1 - (e - .011) / .03, 0, 1) * (1 - gap))[..., None]           # edges catch light
    pg = .26 + .045 * (v2 - .5) + .030 * cloud + .018 * fine - .13 * gap
    ph = -1.6 * gap + .5 * np.clip((e - .011) / .022, 0, 1) + .10 * (v - .5)
    plug = np.clip(.5 + (.034 - np.hypot(er - .20, ec - .20)) / (2 * aa), 0, 1) * (r > 1.7)   # bonded-in plugs over the mount points
    pal *= (1 + .35 * plug)[..., None]; ph += .18 * line(np.hypot(er - .20, ec - .20) - .034, .006, aa)
    c.albedo[:] = c.albedo * white[..., None] + pal * pica[..., None]
    c.gloss[:] = c.gloss * white + pg * pica
    h = h + ph.astype(np.float32) * pica
    # closeout between paint and tiles: a dark-grey strip with a groove each side
    strip = line(d + .05, .05, aa)
    c.albedo[:] = c.albedo * (1 - strip[..., None]) + np.array((.13, .13, .135), np.float32) * strip[..., None]
    c.gloss[:] = c.gloss * (1 - strip) + .34 * strip
    for o in (0, -.10):
        g = line(d - o, .008, aa); h -= 1.0 * g; c.albedo *= (1 - .4 * g)[..., None]
    if sheet == 'aft':                                                # carbon lip around the skirt's edge
        lip = np.clip(.5 + (.16 - (z - H.skirt_z(az))) / (2 * aa), 0, 1).astype(np.float32)
        c.albedo[:] = c.albedo * (1 - lip[..., None]) + .075 * lip[..., None]; c.gloss[:] = c.gloss * (1 - lip) + .42 * lip
    # joint lines at the sheet's own ends
    c.height[:] = h
    c.save('its_' + sheet, nstrength=.55)


build('fwd', (28.15, 30.9, 34.0, 38.0, 40.6, 43.3, 45.4), ((0, 27, 45.4), (60, 30.9, 38), (30, 38, 43.3), (74, 27, 34)), 11)
build('aft', (8.6, 12.0, 15.0, 19.0, 23.0, 26.6), ((0, 14.2, 27), (60, 8.6, 15), (60, 19, 27), (88, 12, 23), (31, 15, 23)), 23)

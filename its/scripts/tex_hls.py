"""HLS hull sheets: white insulating tiles, black leg panels, base and landing-thruster band. Half a hull, mirrored."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl, hls_layout as HL
from texcommon import line, cells, hash2
W = int(os.environ.get('ITS_HULL', 4096))


def noise(seed, base, o=4):
    return np.kron(tl._fbm(W // 2, W // 2, seed, base=base, octaves=o), np.ones((2, 2), np.float32))


def radius(z):
    zz = [0, HL.Z_OGIVE] + [HL.Z_OGIVE + a for a, _ in HL.OGIVE[1:]]; return np.interp(z, zz, [HL.R, HL.R] + [r for _, r in HL.OGIVE[1:]]).astype(np.float32)


def build(sheet, seams, seed):
    c = tl.Canvas(W, W, albedo=(.80, .80, .79), gloss=.40); z0, z1 = HL.SHEET[sheet]
    az = np.clip((c.x / W - HL.PAD) / (1 - 2 * HL.PAD), 0, 1) * 180; z = z0 + (z1 - z0) * np.clip((1 - c.y / W - HL.PAD) / (1 - 2 * HL.PAD), 0, 1)
    r = radius(z); x = np.radians(az) * r; aa = (z1 - z0) / W * .7
    cloud, fine = noise(seed, 5, 5), noise(seed + 1, 60)
    c.albedo *= (1 + .009 * cloud + .004 * fine)[..., None]; c.gloss += .014 * cloud + .012 * fine
    h = np.zeros((W, W), np.float32)
    # insulating tiles: brick-laid, a hair of tone each, thin joints; they halve where the nose narrows
    n = np.where(r > 1.9, 24, 12); row, er = cells(z, .50, .0); col, ec = cells(az, 180.0 / n, .5 * (row % 2)); e = np.minimum(er, np.radians(ec) * r)
    v = hash2(row, col, seed); c.albedo *= (1 + .020 * (v - .5))[..., None]; c.gloss += .035 * (hash2(col, row, seed + 3) - .5)
    g = line(e, .0035, aa); c.albedo *= (1 - .13 * g)[..., None]; h -= .55 * g; c.gloss -= .05 * g
    for s in seams:                                            # barrel joints
        dd = z - s; k = line(dd, .008, aa); c.albedo *= (1 - .30 * k)[..., None]; h -= 1.0 * k
        _, ex = cells(x, .14, .5)
        for o in (-.055, .055):
            dot = np.clip(.5 + (.010 - np.hypot(.07 - ex, dd - o)) / (2 * aa), 0, 1); c.albedo *= (1 - .14 * dot)[..., None]; h -= .3 * dot
    black = np.zeros((W, W), np.float32)
    if sheet == 'core':
        da = np.minimum(np.abs(az - 45), np.abs(az - 135)); s_ = np.radians(da) * HL.R
        t = np.clip((z - HL.Z_BLACK) / (HL.PANEL_TOP - HL.Z_BLACK), 0, 1); half = HL.PANEL_W[0] + (HL.PANEL_W[1] - HL.PANEL_W[0]) * t
        # signed distance, rounded at the top and flared into the base with a fillet
        sd = np.maximum(s_ - half, z - HL.PANEL_TOP); R_ = .16
        qx, qy = s_ - (half - R_), z - (HL.PANEL_TOP - R_); corner = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - R_
        sd = np.where(z > HL.PANEL_TOP - 1, corner, sd); base = z - HL.Z_BLACK; F = .22                       # smooth union
        hh = np.clip(.5 + .5 * (base - sd) / F, 0, 1); u = base + (sd - base) * hh - F * hh * (1 - hh) * 1.0
        black = np.maximum(black, np.clip(.5 - u / (2 * aa), 0, 1))
        bm = (HL.BAND[0] + HL.BAND[1]) / 2; bh = (HL.BAND[1] - HL.BAND[0]) / 2; R_ = .13
        xe = np.radians(np.maximum(0, 12.0 - az)) * HL.R; qx = R_ - np.radians(az - 11.2) * HL.R; qy = np.abs(z - bm) - (bh - .02 - R_)
        u2 = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - R_
        black = np.maximum(black, np.clip(.5 - u2 / (2 * aa), 0, 1)); ub = np.minimum(u, u2)
        edge = line(ub, .010, aa); h -= .9 * edge
        pal = .043 + .006 * cloud + .002 * fine
        c.albedo[:] = c.albedo * (1 - black[..., None]) + np.dstack([pal, pal, pal * 1.03]) * black[..., None]
        c.gloss[:] = c.gloss * (1 - black) + (.30 + .03 * cloud + .02 * fine) * black
        for b in HL.GROUPS:                                     # frames round each group of ports, and a ring round each port
            for k in (-1, 0, 1):
                d_ = np.abs(az - (b + k * HL.PITCH)); ee = np.hypot(np.radians(d_) * HL.R / HL.BORE[0], (z - bm) / HL.BORE[1]); rg = line((ee - 1.06) * .3, .016, aa)
                c.albedo[:] = c.albedo * (1 - rg[..., None]) + .13 * rg[..., None]; c.gloss += .2 * rg; h += .6 * rg
        _, ea = cells(az, 60, .0); k = line(np.radians(ea) * HL.R, .004, aa) * (np.abs(z - bm) < bh); h -= .7 * k
    else:
        for a0, hw, zz in ((48.75, HL.SOL_HW, HL.SOL_Z),):      # hatch outline, and a second service hatch aft
            pass
        for a0, hw, zc, hh_ in ((48.75, 18.9, sum(HL.SOL_Z) / 2, .44), (135, 15, 23.2, .42), (180, 9, 26.2, .5)):
            q = np.maximum(np.abs(np.radians(az - a0)) * r - np.radians(hw) * HL.R, np.abs(z - zc) - hh_); k = line(q, .009, aa); c.albedo *= (1 - .45 * k)[..., None]; h -= 1.0 * k
        s_ = line(z - HL.Z_OGIVE - 7.39, .012, aa); c.albedo *= (1 - .4 * s_)[..., None]; h -= s_
    c.height[:] = h; c.save('hls_' + sheet, nstrength=.5)


build('core', (2.2, 4.85, 7.4, 10.1, 12.8, 15.5, 18.2), 51)
build('crew', (21.3, 24.0, 27.3, 29.6), 57)
import its_lamp

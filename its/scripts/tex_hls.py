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
    c = tl.Canvas(W, W, albedo=(.885, .885, .88), gloss=.52); z0, z1 = HL.SHEET[sheet]
    az = np.clip((c.x / W - HL.PAD) / (1 - 2 * HL.PAD), 0, 1) * 180; z = z0 + (z1 - z0) * np.clip((1 - c.y / W - HL.PAD) / (1 - 2 * HL.PAD), 0, 1)
    r = radius(z); x = np.radians(az) * r; aa = (z1 - z0) / W * .7
    cloud, fine = noise(seed, 5, 5), noise(seed + 1, 60)
    c.albedo *= (1 + .004 * cloud + .002 * fine)[..., None]; c.gloss += .012 * cloud + .006 * fine
    h = np.zeros((W, W), np.float32)
    # insulating tiles: brick-laid, a hair of tone each, thin joints; they halve where the nose narrows
    n = np.where(r > 1.9, 24, 12); row, er = cells(z, .50, .0); col, ec = cells(az, 180.0 / n, .5 * (row % 2)); e = np.minimum(er, np.radians(ec) * r)
    v = hash2(row, col, seed); c.albedo *= (1 + .004 * (v - .5))[..., None]; c.gloss += .010 * (hash2(col, row, seed + 3) - .5)
    g = line(e, .0035, aa); c.albedo *= (1 - (.022 if sheet.endswith('_o') else .010) * g)[..., None]; c.gloss -= (.01 if sheet.endswith('_o') else .006) * g
    for s in seams:                                            # barrel joints
        dd = z - s; k = line(dd, .008, aa); c.albedo *= (1 - (.10 if sheet.endswith('_o') else .05) * k)[..., None]; h -= (.4 if sheet.endswith('_o') else .3) * k
        _, ex = cells(x, .14, .5)
        for o in (-.055, .055):
            dot = np.clip(.5 + (.010 - np.hypot(.07 - ex, dd - o)) / (2 * aa), 0, 1); c.albedo *= (1 - .02 * dot)[..., None]
    black = np.zeros((W, W), np.float32)
    if sheet == 'core':
        da = np.minimum(np.abs(az - 45), np.abs(az - 135)); s_ = np.radians(da) * HL.R
        t = np.clip((z - HL.Z_BLACK) / (HL.PANEL_TOP - HL.Z_BLACK), 0, 1); half = HL.PANEL_W[0] + (HL.PANEL_W[1] - HL.PANEL_W[0]) * t
        # signed distance, rounded at the top and flared into the base with a fillet
        sd = np.maximum(s_ - half, z - HL.PANEL_TOP); R_ = .16
        qx, qy = s_ - (half - R_), z - (HL.PANEL_TOP - R_); corner = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - R_
        sd = np.where(z > HL.PANEL_TOP - 1, corner, sd); sd = sd
        u = sd; black = np.maximum(black, np.clip(.5 - u / (2 * aa), 0, 1))
        bm = (HL.BAND[0] + HL.BAND[1]) / 2; bh = (HL.BAND[1] - HL.BAND[0]) / 2; R_ = .13
        u2 = np.abs(z - bm) - (bh - .02)
        black = np.maximum(black, np.clip(.5 - u2 / (2 * aa), 0, 1)); ub = np.minimum(u, u2)
        edge = line(ub, .010, aa); h -= .9 * edge
        pal = .050 + .004 * cloud + .002 * fine
        c.albedo[:] = c.albedo * (1 - black[..., None]) + np.dstack([pal, pal, pal * 1.03]) * black[..., None]
        c.gloss[:] = c.gloss * (1 - black) + (.16 + .012 * cloud + .008 * fine) * black
        for b in HL.GROUPS:                                     # frames round each group of ports, and a ring round each port
            for k in (-1, 0, 1):
                d_ = np.abs(az - (b + k * HL.PITCH)); ee = np.hypot(np.radians(d_) * HL.R / HL.BORE[0], (z - bm) / HL.BORE[1]); rg = line((ee - 1.06) * .3, .016, aa)
                c.albedo[:] = c.albedo * (1 - rg[..., None]) + .085 * rg[..., None]; h += .5 * rg
        _, ea = cells(az, 60, .0); k = line(np.radians(ea) * HL.R, .004, aa) * (np.abs(z - bm) < bh); h -= .7 * k
    elif sheet in ('core_o', 'core_d_o'):                     # the depot's core is the original's without the band
        da = np.minimum(np.abs(az - 45), np.abs(az - 135)); s_ = np.radians(da) * HL.R
        t = np.clip((z - HL.Z_BLACK) / (HL.O_PANEL_TOP - HL.Z_BLACK), 0, 1); half = HL.O_PANEL_W[0] + (HL.O_PANEL_W[1] - HL.O_PANEL_W[0]) * t
        # signed distance, rounded at the top and flared into the base with a fillet
        sd = np.maximum(s_ - half, z - HL.O_PANEL_TOP); R_ = .16
        qx, qy = s_ - (half - R_), z - (HL.O_PANEL_TOP - R_); corner = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - R_
        sd = np.where(z > HL.O_PANEL_TOP - 1, corner, sd); base = z - HL.Z_BLACK; F = .22                       # smooth union
        hh = np.clip(.5 + .5 * (base - sd) / F, 0, 1); u = base + (sd - base) * hh - F * hh * (1 - hh) * 1.0
        black = np.maximum(black, np.clip(.5 - u / (2 * aa), 0, 1))
        bm = (HL.O_BAND[0] + HL.O_BAND[1]) / 2; bh = (HL.O_BAND[1] - HL.O_BAND[0]) / 2; R_ = .13
        xe = np.radians(np.maximum(0, 12.0 - az)) * HL.R; qx = R_ - np.radians(az - 11.2) * HL.R; qy = np.abs(z - bm) - (bh - .02 - R_)
        u2 = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - R_
        if sheet == 'core_d_o': u2 = np.full_like(u2, 9)
        black = np.maximum(black, np.clip(.5 - u2 / (2 * aa), 0, 1)); ub = np.minimum(u, u2)
        edge = line(ub, .010, aa); h -= .9 * edge
        pal = .050 + .004 * cloud + .002 * fine
        c.albedo[:] = c.albedo * (1 - black[..., None]) + np.dstack([pal, pal, pal * 1.03]) * black[..., None]
        c.gloss[:] = c.gloss * (1 - black) + (.16 + .012 * cloud + .008 * fine) * black
        for b in HL.GROUPS if sheet == 'core_o' else ():        # frames round each group of ports, and a ring round each port
            for k in (-1, 0, 1):
                d_ = np.abs(az - (b + k * HL.PITCH)); ee = np.hypot(np.radians(d_) * HL.R / HL.O_BORE[0], (z - bm) / HL.O_BORE[1]); rg = line((ee - 1.06) * .3, .016, aa)
                c.albedo[:] = c.albedo * (1 - rg[..., None]) + .085 * rg[..., None]; h += .5 * rg
        _, ea = cells(az, 60, .0); k = line(np.radians(ea) * HL.R, .004, aa) * (np.abs(z - bm) < bh); h -= .7 * k * (sheet == 'core_o')
    elif sheet in ('crew', 'crew_o'):
        for a0, hw, zc, hh_ in ((56.25, 18.9, sum(HL.SOL_Z) / 2, (HL.SOL_Z[1] - HL.SOL_Z[0]) / 2 + .015), (101.25, 18.9, sum(HL.SOL_Z) / 2, (HL.SOL_Z[1] - HL.SOL_Z[0]) / 2 + .015), (180, 18.9, sum(HL.SOL_Z) / 2, (HL.SOL_Z[1] - HL.SOL_Z[0]) / 2 + .015), (180, 9, 26.2, .5)):
            q = np.maximum(np.abs(np.radians(az - a0)) * r - np.radians(hw) * HL.R, np.abs(z - zc) - hh_); k = line(q, .009, aa); c.albedo *= (1 - .45 * k)[..., None]; h -= 1.0 * k
        s_ = line(z - HL.Z_OGIVE - 7.39, .012, aa); c.albedo *= (1 - .3 * s_)[..., None]; h -= s_
    c.height[:] = h; c.save('hls_' + sheet, nstrength=.5)


build('core', (2.2, 4.85, 7.4, 10.1, 12.8, 15.5, 18.2), 51)
build('crew', (21.3, 24.0, 27.3, 29.6), 57)
W = W // 2
build('cargo', (24.0, 27.3, 29.6), 61)
build('core_o', (2.2, 4.85, 7.4, 10.1, 12.8, 15.5, 18.2), 51)
build('crew_o', (21.3, 24.0, 27.3, 29.6), 57)
build('cargo_o', (24.0, 27.3, 29.6), 61)
import its_lamp

g = np.zeros((64, 64, 4), np.uint8); g[...] = (212, 212, 210, 175); tl.write_dds(g, 'stms_plainwhite_diff')          # white finish for SEP's docking hardware
g[...] = (225, 226, 225, 133); tl.write_dds(g, 'stms_corewhite_diff')     # the expendable core's White hull: the white depot's own paint (median of hls_crew_o_diff: colour, smoothness in the alpha), on the same shader
g[...] = (0, 255, 0, 255); tl.write_dds(g, 'stms_plainmask_diff')                                                    # no metal, full AO

g = np.zeros((4, 4, 4), np.uint8); g[...] = (128, 128, 128, 255)      # stand-ins for SEP's textures on the cut nose pieces (B9 swaps the real ones in)
for n in ('Ship_Core_7_BASE', 'Ship_Core_7_NRM', 'Ship_Core_7_MASK', 'Ship_Core_11_BASE', 'Ship_Core_11_NRM', 'Ship_Core_11_MASK', 'Ship_Core_1_BASE', 'Ship_Core_1_NRM', 'Ship_Core_1_MASK', 'TILES_BASE', 'TILES_NRM'): tl.write_dds(g, 'SEP_B3_' + n)

g = np.zeros((512, 512, 4), np.uint8); g[..., :3] = 203; g[..., 3] = np.clip(190 + 10 * tl._fbm(512, 512, 5, base=6, octaves=4), 0, 255); tl.write_dds(g, 'stms_steel_diff')      # the ship's steel: SEP's average colour and smoothness
g[...] = (255, 255, 0, 255); tl.write_dds(g[:64, :64].copy(), 'stms_steelmask_diff'); g[...] = (255, 128, 128, 128); tl.write_dds(g[:64, :64].copy(), 'stms_steel_nrm')

"""Booster: tanks, thrust section for the three engine rings, base fairings, raceways and interstage."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
P = start('ITS_Booster'); O = L.B_ORIGIN; R = L.BR * K
M = P.material('its_booster', spec=(.55, .55, .56), shininess=.45)
zk = lambda z: (z - O) * K
ZM = L.B_ENG                       # engine mounting plane (KSP m)
ZMR = ZM / K + O

# ------------------------------------------------ outer skin
g = Geo(); SEG = 96
zs = [L.B_BASE, L.B_BASE + .14, 3.0, 10.5, 20, 30, 39.0, 39.0, 50, 60, 66, 71.0]
AZ = np.linspace(0, 360, SEG + 1)
def skin_row(z, dr=0.0):
    i0 = len(g.v)
    zz = np.broadcast_to(z, AZ.shape)
    for a, z_ in zip(AZ, zz):
        x = math.radians(a); r = R + dr
        g.v.append((r * math.sin(x), -r * math.cos(x), zk(z_)))
    return i0, zz
rows = [skin_row(z, -.03 if z == L.B_BASE else 0) for z in zs] + [skin_row(72.6)] + [skin_row(72.6 + (L.b_top(AZ) - 72.6) * t) for t in (.5, 1)]
def outer_quads(ra, rb):
    (ia, za), (ib, zb) = ra, rb
    if zb[0] - za[0] < 1e-6 and abs(zb[SEG // 2] - za[SEG // 2]) < 1e-6:
        return
    s = 0 if max(zb) <= 39.001 else 1
    for k in range(SEG):
        a0 = AZ[k] % 120; a1 = a0 + 360 / SEG
        g.face([ia + k, ia + k + 1, ib + k + 1, ib + k], [L.b_uv(a0, za[k], s), L.b_uv(a1, za[k + 1], s), L.b_uv(a1, zb[k + 1], s), L.b_uv(a0, zb[k], s)])
for ra, rb in zip(rows, rows[1:]):
    outer_quads(ra, rb)
P.mesh('hull', g, M, smooth_angle=30)

det, bay, inter = Geo(), Geo(), Geo()
# ------------------------------------------------ interstage, inside
W = .10
ri = R - W
n = SEG; top = L.b_top(AZ)
g2 = Geo(); levels = (0, .35, .7, 1)
for t in levels:
    for a, zt in zip(AZ, top):
        x = math.radians(a); z = L.B_INTER + (zt - L.B_INTER) * t
        g2.v.append((ri * math.sin(x), -ri * math.cos(x), zk(z)))
for j in range(len(levels) - 1):
    for k in range(n):
        a, b, c, d = j * (n + 1) + k, j * (n + 1) + k + 1, (j + 1) * (n + 1) + k + 1, (j + 1) * (n + 1) + k
        s = (k % 12) / 12
        g2.face([b, a, d, c], [Z.wall.uv(s + 1 / 12, levels[j]), Z.wall.uv(s, levels[j]), Z.wall.uv(s, levels[j + 1]), Z.wall.uv(s + 1 / 12, levels[j + 1])])
base = len(g2.v)
for rr in (R, ri):
    for a, zt in zip(AZ, top):
        x = math.radians(a); g2.v.append((rr * math.sin(x), -rr * math.cos(x), zk(zt)))
for k in range(n):
    q = [base + k, base + k + 1, base + n + 1 + k + 1, base + n + 1 + k]
    g2.face(q, [Z.carbon.uv(.1 * (k % 8), .1), Z.carbon.uv(.1 * (k % 8) + .1, .1), Z.carbon.uv(.1 * (k % 8) + .1, .16), Z.carbon.uv(.1 * (k % 8), .16)])
inter.add(g2)
inter.add(lathe([(ri, zk(L.B_INTER)), (ri - .25, zk(L.B_INTER) + .0), (2.5, zk(L.B_INTER) - .02), (1.6, zk(L.B_INTER) + .04), (.8, zk(L.B_INTER) + .07), (0, zk(L.B_INTER) + .08)], 72, zone=Z.invar))
for a in range(0, 360, 10):
    zt = float(L.b_top(a)) - .35
    if zt > L.B_INTER + .6:
        inter.add(box(.05, .07, (zt - L.B_INTER) * K, zone=Z.carbon, bevel=.008), on_cyl(a, zk((zt + L.B_INTER) / 2), ri - .03) @ Rx(-90) @ Rz(0))
inter.add(ring(ri - .10, ri + .01, zk(72.75), zk(72.75) + .05, Z.carbon, 72))
for a in range(-80, 81, 8):                      # leeward hoop only: the windward wall is cut away
    pass
for z in (74.2, 76.0):
    inter.add(ring(ri - .07, ri + .01, zk(z), zk(z) + .04, Z.carbon, 48, -80, 80))
for a in range(20, 360, 40):                     # floor: ribs, vents and sensors on the dome
    f = on_cyl(a, zk(L.B_INTER) + .03, 2.9)
    inter.add(box(.10, .10, 1.5, zone=Z.dark, bevel=.012), f @ T(0, 0, -.4))
for a, rr in ((10, 1.2), (130, 1.2), (250, 1.2), (70, 2.3), (190, 2.3), (310, 2.3)):
    c = on_cyl(a, zk(L.B_INTER), rr).translation
    inter.add(cyl(.20, .16, 20, zone=Z.steel, bevel=.02, center_z=False), T(c.x, c.y, c.z))
    inter.add(bolts(10, .16), T(c.x, c.y, c.z + .16))
# separation pushers around the leeward rim, latches all round
for a in range(0, 360, 30):
    zt = float(L.b_top(a))
    f = on_cyl(a, zk(zt) - .30, ri - .10)
    inter.add(box(.26, .46, .16, zone=Z.grey, bevel=.02), f)
    inter.add(cyl(.055, .26, 14, zone=Z.steel), f @ T(0, .16, .05) @ Rx(90))
P.mesh('interstage', inter, P.det, smooth_angle=36)

# ------------------------------------------------ engine section
rb = R - .09
bay.add(lathe([(rb, ZM + .42), (rb, zk(L.B_BASE) + .04), (R - .03, zk(L.B_BASE))], 96, zone=Z.wall, flip=False))
plate = [(0, ZM + .03), (rb - .02, ZM + .03)]
bay.add(lathe(plate, 72, zone=Z.dome))
bay.add(ring(rb - .16, rb, ZM - .06, ZM + .10, Z.carbon, 96))
def engine_spots():
    for nm, (cnt, r, a0) in L.RINGS.items():
        for i in range(cnt):
            yield nm, r, a0 + 360 * i / cnt
        if nm == 'ITS_Ring7':
            yield nm, 0, 0
for nm, r, a in engine_spots():
    c = on_cyl(a, ZM, r).translation
    bay.add(cyl(.30, .10, 14, zone=Z.steel, bevel=.02, center_z=False), T(c.x, c.y, ZM - .0))
    bay.add(cyl(.38, .035, 14, zone=Z.alu, bevel=.01, center_z=False), T(c.x, c.y, ZM + .035))
    if r > 0:
        for s in (-1, 1):                        # LOX and CH4 stubs to the manifolds
            q = on_cyl(a + s * math.degrees(.22 / r), ZM, r + .30).translation
            bay.add(cyl(.075, .22, 8, zone=Z.alu if s > 0 else Z.steel), T(q.x, q.y, ZM + .0))
for rr, t, zn in ((1.62, .07, Z.steel), (1.78, .05, Z.alu), (2.74, .09, Z.steel), (2.94, .06, Z.alu), (3.50, .05, Z.alu)):
    bay.add(tube([tuple(on_cyl(a, ZM - .02, rr).translation) for a in np.arange(0, 360, 7.5)], t, 6, zone=zn, closed=True))
for k in range(21):
    f = on_cyl(360 / 21 * (k + .5), ZM - .09, 3.08)
    bay.add(box(.07, .26, 1.0, zone=Z.carbon, bevel=.01), f @ T(0, -.02, -.02))
for k in range(14):
    f = on_cyl(360 / 28 + 360 / 14 * (k + .5), ZM - .06, 2.24)
    bay.add(box(.06, .20, .62, zone=Z.carbon, bevel=.01), f)
for k in range(6):
    f = on_cyl(30 + 60 * k, ZM - .06, 1.20)
    bay.add(box(.06, .20, .80, zone=Z.carbon, bevel=.01), f)
for a in range(0, 360, 10):
    bay.add(box(.04, zk(0) * 0 + (ZM - zk(L.B_BASE) - .1), .06, zone=Z.carbon, bevel=.006), on_cyl(a + 5, (ZM + zk(L.B_BASE)) / 2, rb - .02))
bay.add(ring(rb - .07, rb, zk(1.55), zk(1.55) + .04, Z.carbon, 96))
P.mesh('engine_section', bay, P.det, smooth_angle=36)

# ------------------------------------------------ base fairings: blade with a filleted root (slide 34)
FZ = np.array([.75, 1.2, 1.9, 2.6, 3.1, 3.6, 4.6, 5.0, 5.5, 6.2, 7.0, 7.8, 8.6, 9.4, 10.1, 10.7])
FR = np.array([6.0, 6.55, 7.32, 7.95, 8.2, 8.27, 8.27, 8.22, 8.05, 7.62, 7.13, 6.72, 6.42, 6.2, 6.06, 6.0])
def fin_loop(z, Rz_):
    h = Rz_ - 6.0; w = .12 + .20 * min(1, h / 1.6); f = min(.95, h * .62) + 1e-3
    out = [(0, Rz_)]
    c = min(.10, h * .25)
    for t in (0, 30, 60, 90):
        out.append((w - c + c * math.sin(math.radians(t)), Rz_ - c + c * math.cos(math.radians(t))))
    # fillet: circle of radius f tangent to the flank x = w and (nearly) to the body
    yb = lambda x: math.sqrt(36 - x * x)
    cx = w + f; cy = math.sqrt(max((6 + f) ** 2 - cx * cx, 0))
    cy = max(cy, 6.0)
    a_end = math.atan2(6 - cy * 1, 0 - 0) if False else None
    th0 = math.pi; th1 = math.atan2(-cy, -cx)      # toward the axis: contact with the body circle
    if th1 < 0: th1 += TAU
    for t in np.linspace(0, 1, 7):
        th = th0 + (th1 - th0) * t
        x, y = cx + f * math.cos(th), cy + f * math.sin(th)
        out.append((x, min(y, Rz_ - c)))
    x, y = out[-1]; rr = math.hypot(x, y)
    out[-1] = (x / rr * 5.985, y / rr * 5.985)
    return [(-x, y) for x, y in out[:0:-1]] + out
fair = Geo()
loops = [fin_loop(z, r) for z, r in zip(FZ, FR)]; m = len(loops[0])
for z, lp in zip(FZ, loops):
    fair.v += [(x * K, -y * K, zk(z)) for x, y in lp]
for j in range(len(FZ) - 1):
    for k in range(m - 1):
        t0, t1 = (FZ[j] - .75) / 10, (FZ[j + 1] - .75) / 10
        fair.face([j * m + k, j * m + k + 1, (j + 1) * m + k + 1, (j + 1) * m + k],
                  [Z.white.uv(k / (m - 1), t0), Z.white.uv((k + 1) / (m - 1), t0), Z.white.uv((k + 1) / (m - 1), t1), Z.white.uv(k / (m - 1), t1)])
fs = Geo()
for a in L.GF_AZ:
    fs.add(fair, Rz(a))
    for s in (-1, 1):                              # leg/footing plates under the blades, access covers
        det.add(box(.24, .34, .03, zone=Z.grey, bevel=.01), Rz(a) @ T(0, -8.28 * K, zk(4.1)) @ Rx(90)) if s > 0 else None
    det.add(cyl(.12, .06, 18, zone=Z.steel, bevel=.012), Rz(a) @ T(0, -7.35 * K, zk(1.92)) @ Rx(48))
P.mesh('fairings', fs, P.det, smooth_angle=40)

# ------------------------------------------------ outside details
def strip(az, z0, z1, w, h, zone):
    """Raceway: a low box along the hull with sloped ends."""
    y0, y1 = zk(z0), zk(z1); g = Geo(); e = .35
    prof = ((y0, 0), (y0 + e, h), (y1 - e, h), (y1, 0))
    for (y, hh) in prof:
        for x, k in ((-w / 2, 0), (-w / 2 + .03, 1), (w / 2 - .03, 1), (w / 2, 0)):
            g.v.append((x, y, hh * k - .01))
    for j in range(3):
        l0, l1 = prof[j][0], prof[j + 1][0]
        reps = max(1, int((l1 - l0) / 2.5))
        for k in range(3):
            q = [j * 4 + k, j * 4 + k + 1, (j + 1) * 4 + k + 1, (j + 1) * 4 + k]
            g.face(q, [zone.uv(k / 3, 0), zone.uv((k + 1) / 3, 0), zone.uv((k + 1) / 3, 1), zone.uv(k / 3, 1)])
    return g
for a in L.RW_AZ:
    f = on_cyl(a, 0, R)
    det.add(strip(a, 3.5, 59.0, .42, .13, Z.white), f)
    for z in np.arange(5.5, 58.5, 2.65):           # clamps
        det.add(box(.50, .10, .15, zone=Z.grey, bevel=.012), f @ T(0, zk(z), .065))
    # autogenous pressurant lines alongside
    for dx, t in ((.36, .035), (.45, .022)):
        det.add(tube([(dx, zk(4.2), .0), (dx, zk(4.5), .05), (dx, zk(58), .05), (dx, zk(58.3), -.02)], t, 8, zone=Z.steel), f)
        for z in np.arange(6.8, 57, 5.3):
            det.add(box(.10, .05, .09, zone=Z.alu, bevel=.008), f @ T(dx, zk(z), .04))
# grid fin hardpoints: a fairing above each hinge and the actuator box behind it
for a in L.GF_AZ:
    f = on_cyl(a, zk(L.GF_Z), R)
    # sail-shaped fairing over the hinge: flat ridge, concave flanks, flaring out at its open lower end
    g = Geo(); nz, secs = 12, []
    for j in range(nz + 1):
        u = j / nz; h = .62 * (1 - u) ** 1.15; w = .30; bw = w + .06 + 1.02 * (1 - u) ** 1.2
        row = []
        for s in (-1, 1):
            side = [(w * k / 2, h) for k in range(3)] + [(w + (bw - w) * t, h * (1 - t) ** 2.1) for t in (.05, .13, .24, .38, .55, .75, 1)]
            row += [(s * x, y) for x, y in (side[::-1] if s < 0 else side[1:])]
        secs.append(row); z_ = -.02 + 2.9 * u
        for x, hh in row:
            a_ = x / R; rr = R + hh - .012
            g.v.append((rr * math.sin(a_), z_, rr * math.cos(a_) - R))
    m_ = len(secs[0])
    for j in range(nz):
        for k in range(m_ - 1):
            q = [j * m_ + k, j * m_ + k + 1, (j + 1) * m_ + k + 1, (j + 1) * m_ + k]
            g.face(q, [Z.white.uv(k / m_, j / nz), Z.white.uv((k + 1) / m_, j / nz), Z.white.uv((k + 1) / m_, (j + 1) / nz), Z.white.uv(k / m_, (j + 1) / nz)])
    # closing wall under the lower end, set back as a lip
    for k in range(m_ - 1):
        n0 = len(g.v)
        for kk in (k, k + 1):
            x, hh = secs[0][kk]
            for rr in (R + hh - .012, R - .02):
                g.v.append((rr * math.sin(x / R), -.02, rr * math.cos(x / R) - R))
        g.face([n0 + 1, n0 + 3, n0 + 2, n0], [Z.dark.uv(.1, .1), Z.dark.uv(.2, .1), Z.dark.uv(.2, .2), Z.dark.uv(.1, .2)])
    det.add(g, f)
    for x in (-.62, .62):                              # stowage latches for the fin
        det.add(stick_cyl(box(.16, .24, .16, zone=Z.grey, bevel=.02, center=(x, 0, 0)), a, zk(L.GF_Z) - 3.2, R))
    P.node('fin%d' % (L.GF_AZ.index(a) + 1), f @ Vector((0, 0, .0)), f.to_3x3() @ Vector((0, 0, 1)), 1)
# attitude thrusters: four pods under the interstage, three by the base
rcs = []
for a in (30, 90, 150, 210, 270, 330):
    f = on_cyl(a, zk(70.6), R)
    det.add(stick_cyl(box(.9, .60, .14, zone=Z.grey, bevel=.03), a, zk(70.6), R))
    for x in (-.27, 0, .27):
        rcs.append(on_cyl(a + math.degrees(x / R), zk(70.6), R + .066))
for a in (30, 90, 150, 210, 270, 330):
    f = on_cyl(a, zk(12.0), R)
    for x in (-.2, .2):
        rcs.append(on_cyl(a + math.degrees(x / R), zk(12.0), R))
for fr in rcs:
    det.add(rcs_port(.19), fr)
for a in range(30, 360, 60):
    for z, off in ((70.6, .066), (12.0, 0)):
        P.empty('RCSthruster', on_cyl(a, zk(z), R + off), P.model)
# umbilicals, hold-downs, panels round the base
for a in (60, 180, 300):
    for da, y in ((-14, 2.2), (14, 2.2)):
        h = Geo(); h.add(box(.8, .55, .06, zone=Z.grey, bevel=.02))
        for x in (-.2, .2):
            h.add(cyl(.13, .08, 20, zone=Z.steel, bevel=.012, center_z=False), T(x, 0, .02))
            h.add(cyl(.08, .10, 16, zone=Z.dark, center_z=False), T(x, 0, .02))
        det.add(stick_cyl(h, a + da, zk(y), R))
for a in range(15, 360, 30):
    f = on_cyl(a, zk(1.15), R)
    det.add(box(.34, .42, .10, zone=Z.alu, bevel=.02), f)
    det.add(cyl(.10, .05, 16, zone=Z.dark, center_z=False), f @ T(0, -.05, .04))
for a, z, w, h in ((24, 18, 1.0, .8), (95, 36.4, .8, .8), (215, 36.4, .8, .8), (335, 18, 1.0, .8), (24, 62, .8, .6), (144, 62, .8, .6), (264, 62, .8, .6)):
    det.add(stick_cyl(rounded_rect_ring(w, h, .10, .04, .014, 4, zone=Z.white), a, zk(z), R))
P.mesh('detail', det, P.det)

# ------------------------------------------------ lettering and flag (own meshes, so a switch can hide them)
def decal(poly, az, z, off=.007):
    """A convex quad in text space (u right, v up, real m, text rotated 90 degrees clockwise so it runs down the hull)."""
    g = Geo(); n = 5
    (p0, p1, p2, p3) = [Vector(p) for p in poly]
    for j in range(n + 1):
        for i in range(n + 1):
            s, t = i / n, j / n
            p = (p0 * (1 - s) + p1 * s) * (1 - t) + (p3 * (1 - s) + p2 * s) * t
            a = math.radians(az) + p.y / 6.0; r = R + off
            g.v.append((r * math.sin(a), -r * math.cos(a), zk(z - p.x)))
    for j in range(n):
        for i in range(n):
            a = j * (n + 1) + i
            g.face([a, a + 1, a + n + 2, a + n + 1], [Z.black.uv(.3, .3), Z.black.uv(.35, .3), Z.black.uv(.35, .35), Z.black.uv(.3, .35)])
    return g
def seg(a, b, w):
    a, b = Vector(a), Vector(b); d = (b - a).normalized(); nrm = Vector((-d.y, d.x)) * w / 2
    return [a - nrm, b - nrm, b + nrm, a + nrm]
t = .46; H_, W_ = 2.7, 3.3
h = t / 2
LET = {
 'S': [seg((h * 0, H_ - h), (W_, H_ - h), t), seg((h, H_ - t * .9), (h, H_ / 2), t), seg((0, H_ / 2), (W_, H_ / 2), t), seg((W_ - h, H_ / 2), (W_ - h, t * .9), t), seg((0, h), (W_, h), t)],
 'P': [seg((0, H_ - h), (W_, H_ - h), t), seg((W_ - h, H_ - t * .9), (W_ - h, H_ * .42), t), seg((0, H_ * .42), (W_, H_ * .42), t), seg((h, H_ * .42 - .0), (h, 0), t)],
 'A': [seg((.1, 0), (W_ / 2, H_ - .1), t), seg((W_ - .1, 0), (W_ / 2, H_ - .1), t)],
 'C': [seg((0, H_ - h), (W_, H_ - h), t), seg((h, H_ - t * .9), (h, t * .9), t), seg((0, h), (W_, h), t)],
 'E': [seg((0, H_ - h), (W_, H_ - h), t), seg((0, H_ / 2), (W_ * .9, H_ / 2), t), seg((0, h), (W_, h), t), seg((h, H_ / 2), (h, h), t)],
 'X': [seg((.1, H_), (W_ - .1, 0), t * 1.05), seg((.1, 0), (W_ * .36, H_ * .36), t * 1.05), seg((W_ * .60, H_ * .62), (W_ - .1, H_), t * 1.05)],
}
txt = Geo(); z = 57.0
for ch in 'SPACEX':
    for q in LET[ch]:
        txt.add(decal([(p.x if hasattr(p, 'x') else p[0], (p.y if hasattr(p, 'y') else p[1]) - H_ / 2) for p in q], 0, z))
    z -= 6.6
P.mesh('lettering', txt, P.det)
fl = Geo(); fw, fh = 4.4, 2.32
fx, fy, fpw, fph = L.FLAG
g = decal([(0, -fh / 2), (fw, -fh / 2), (fw, fh / 2), (0, fh / 2)], 0, 16.4)
n = 5; k = 0
for j in range(n):
    for i in range(n):
        uv = lambda s, t: ((fx + s / n * fpw) / 2048, 1 - (fy + (1 - t / n) * fph) / 2048)
        g.uv[k] = (uv(i, j), uv(i + 1, j), uv(i + 1, j + 1), uv(i, j + 1)); k += 1
fl.add(g)
P.mesh('flag', fl, P.det)

# ------------------------------------------------ colliders
def ringp(r, z, n=20): return [tuple(on_cyl(a, zk(z), r * K).translation) for a in np.arange(0, 360, 360 / n)]
P.hull_collider('col_tank', ringp(6, 3.2) + ringp(6, L.B_INTER))
for k in range(12):
    pts = []
    for a in (30 * k, 30 * k + 15, 30 * k + 30):
        for rr in (5.99, 5.80):
            pts += [tuple(on_cyl(a, zk(zz), rr * K).translation) for zz in (L.B_INTER, float(L.b_top(a)))]
    P.hull_collider(f'col_inter{k}', pts)
    pts = []
    for a in (30 * k, 30 * k + 15, 30 * k + 30):
        for rr in (5.99, 5.90):
            pts += [tuple(on_cyl(a, zk(zz), rr * K).translation) for zz in (L.B_BASE, 3.2)]
    P.hull_collider(f'col_base{k}', pts)
for i, a in enumerate(L.GF_AZ):
    P.hull_collider(f'col_fin{i}', [tuple(Rz(a) @ Vector((s * .3 * K, -r * K, zk(z)))) for s in (-1, 1) for r, z in ((5.9, .8), (8.2, 3.2), (8.2, 5), (5.9, 10))])

P.node('top', (0, 0, zk(L.BZ_TOP)), (0, 0, 1), 6)
for nm, key in (('ring21', 'a'), ('ring14', 'b'), ('ring7', 'c')):
    P.node(nm, (0, 0, ZM), (0, 0, -1), 4)
finish(P)

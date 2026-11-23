"""Cargo forward section: crew section's outer mould line, a clamshell bay facing leeward and a crane mount in its ceiling."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fwd import *
P = start('ITS_FwdCargo'); M = materials(P)
D0, D1 = L.DOOR_Z; DA = L.DOOR_AZ; LN = -L.LINER
zk = lambda z: (z - O) * K
ext = (D0, D1, 30.5, 32.5, 34.5, 37.0, 38.7)
indoor = lambda a, z: (a < DA or a > 360 - DA) and D0 < z < D1
P.mesh('hull', skin(H.Z_SPLIT, H.Z_TIP, 'fwd', O, extra=ext, keep=lambda a, z: not indoor(a, z)), M, smooth_angle=32)
det, inn = Geo(), Geo()
joint(P, det, floor=True); det.add(ports(P, [q for q in RCS if abs(q[0]) != 16]))

# ---------------- hold: liner, frames, floor, ceiling
def remap(g, zone, sx=2.6, sz=2.6):
    """Cylindrical metres mapped into a zone (repeats are folded, so panels stay continuous enough for a liner)."""
    out = Geo(); out.v = g.v
    for f in g.f:
        pts = [g.v[i] for i in f]
        az = [math.atan2(p[0], -p[1]) * 3.4 for p in pts]; zz = [p[2] for p in pts]
        a0 = math.floor(min(az) / sx) * sx; z0 = math.floor(min(zz) / sz) * sz
        fold = lambda t: t if t <= 1 else max(0, 2 - t)
        out.face(f, [zone.uv(fold((a - a0) / sx), fold((z - z0) / sz)) for a, z in zip(az, zz)])
    return out
liner = skin(D0, D1, 'fwd', O, extra=ext, keep=lambda a, z: DA < a < 360 - DA, off=LN, flip=True)
inn.add(remap(liner, Z.wall))
og = skin(D0, D1, 'fwd', O, extra=ext, keep=lambda a, z: DA < a < 360 - DA)
ig = skin(D0, D1, 'fwd', O, extra=ext, keep=lambda a, z: DA < a < 360 - DA, off=LN)
det.add(wall(og, ig, Z.carbon))
# sills and headers across the opening
for z, up in ((D0, True), (D1, False)):
    a = skin(D0 - .6 if up else D1, D0 if up else D1 + .6, 'fwd', O, extra=ext, keep=lambda a_, z_: a_ < DA or a_ > 360 - DA)
    b_ = skin(D0 - .6 if up else D1, D0 if up else D1 + .6, 'fwd', O, extra=ext, keep=lambda a_, z_: a_ < DA or a_ > 360 - DA, off=LN)
    det.add(wall(a, b_, Z.carbon))
rf = (H.RB + LN) * K
def arc_frame(z, w, h, zone, a0=DA + 2, a1=360 - DA - 2, n=40):
    """Hoop frame hugging the liner at height z."""
    g = Geo(); rows = []
    for i in range(n + 1):
        az = a0 + (a1 - a0) * i / n; row = []
        for dr, dz in ((LN + .02, -w), (LN - h, -w * .8), (LN - h, w * .8), (LN + .02, w)):
            p = H.point(az, z + dz, dr); row.append(len(g.v)); g.v.append((float(p[0]) * K, float(p[1]) * K, zk(float(p[2]))))
        rows.append(row)
    for r0, r1 in zip(rows, rows[1:]):
        for k in range(3):
            g.face([r0[k], r0[k + 1], r1[k + 1], r1[k]], [zone.uv(0, k / 3), zone.uv(0, (k + 1) / 3), zone.uv(.2, (k + 1) / 3), zone.uv(.2, k / 3)])
    return g
for z in (30.2, 32.2, 34.2, 36.2, 38.2, 39.9):
    inn.add(arc_frame(z, .09, .22, Z.grey))
def rib(az, z0, z1, w, h, zone, n=8):
    g = Geo(); rows = []
    for i in range(n + 1):
        z = z0 + (z1 - z0) * i / n; row = []
        for da, dr in ((-w, LN + .02), (-w * .7, LN - h), (w * .7, LN - h), (w, LN + .02)):
            p = H.point(az + math.degrees(da / 5.5), z, dr); row.append(len(g.v)); g.v.append((float(p[0]) * K, float(p[1]) * K, zk(z)))
        rows.append(row)
    for r0, r1 in zip(rows, rows[1:]):
        for k in range(3):
            g.face([r0[k], r0[k + 1], r1[k + 1], r1[k]][::-1], [zone.uv(0, k / 3), zone.uv(0, (k + 1) / 3), zone.uv(.3, (k + 1) / 3), zone.uv(.3, k / 3)][::-1])
    return g
for a in range(75, 300, 15):
    inn.add(rib(a, D0, D1, .07, .14, Z.alu))
for s in (1, -1):                                  # door longerons
    inn.add(rib(s * 63.2, D0, D1, .28, .30, Z.grey, 12))
# floor deck on a closed disc, with a payload adapter ring and tie-down tracks
fz = zk(L.BAY_FLOOR)
def disc(z, r, zone, up=True, seg=72):
    g = Geo(); c = 0; g.v.append((0, 0, z))
    for i in range(seg):
        a = TAU * i / seg; g.v.append((r * math.sin(a), -r * math.cos(a), z))
    for i in range(seg):
        j = (i + 1) % seg
        uv = lambda p: zone.uv(.5 + p[0] / (2 * r) * .98, .5 + p[1] / (2 * r) * .98)
        f = [0, 1 + i, 1 + j]
        g.face(f if up else f[::-1], [uv(g.v[k]) for k in (f if up else f[::-1])])
    return g
fl = Geo(); fl.v.append((0, 0, fz)); fa = np.arange(0, 360, 4)
for a in fa:
    p = H.point(a, L.BAY_FLOOR, LN + .04); fl.v.append((float(p[0]) * K, float(p[1]) * K, fz))
for i in range(len(fa)):
    q = [0, 1 + i, 1 + (i + 1) % len(fa)]
    fl.face(q, [Z.deck.uv(.5 + fl.v[k][0] / 9, .5 + fl.v[k][1] / 9) for k in q])
inn.add(fl)
for x in np.arange(-2.8, 2.9, .7):
    ln = 2 * math.sqrt(max(0, 3.2 ** 2 - x * x))
    inn.add(box(.07, ln, .025, zone=Z.alu, bevel=.006, center=(x, 0, fz + .01)))
    for y in np.arange(-ln / 2 + .25, ln / 2 - .1, .7):
        inn.add(cyl(.035, .03, 8, zone=Z.steel, center_z=False), T(x, y, fz + .015))
inn.add(lathe([(1.30, fz), (1.30, fz + .10), (1.24, fz + .14), (1.12, fz + .14), (1.06, fz + .10), (1.06, fz)], 48, zone=Z.white))
inn.add(bolts(24, 1.18, .022), T(0, 0, fz + .14))
for k in range(8):
    inn.add(box(.10, .34, .10, zone=Z.white, bevel=.015), Rz(45 * k) @ T(0, -1.45, fz + .05))
# ceiling: dome bulkhead with beams and the crane's mounting plate
cz = zk(L.BAY_TOP); rc = float(H.body_r(L.BAY_TOP) + LN) * K; dy = float(H.droop(L.BAY_TOP)) * K
inn.add(disc(cz + .10, rc + .12, Z.dome, up=False), T(0, dy, 0))
cm = Rz(L.CR_AZ)
for x in (-1.0, 0, 1.0):
    ln = 2 * math.sqrt(rc * rc - x * x) - .25
    inn.add(box(.12, ln, .12, zone=Z.grey, bevel=.02), cm @ T(x, 0, cz + .06) )
for y in (-1.6, -.5, .5, 1.6):
    inn.add(box(2 * math.sqrt(rc * rc - y * y) - .3, .09, .09, zone=Z.alu, bevel=.015), cm @ T(0, y, cz + .07))
inn.add(cyl(.42, .05, 32, zone=Z.steel, bevel=.01), T(0, 0, cz + .025)); inn.add(bolts(12, .37, .02), T(0, 0, cz) @ Rx(180))
# windward wall: lockers, ladder, crane control panel, cable trays, lamps
def on_liner(az, z, d=.0):
    return surf(az, z, O, LN - d)
def inward(m):
    return m @ Ry(180)
for az, z, w, h, d in ((150, 30.1, 1.5, 1.5, .40), (170, 30.1, 1.2, 1.1, .34), (192, 30.3, 1.6, 1.7, .40), (212, 29.9, 1.0, 1.0, .30), (128, 29.9, 1.1, 1.0, .30)):
    f = inward(on_liner(az, z, -.06))
    inn.add(box(w, h, d, zone=Z.white, bevel=.03, center=(0, 0, d / 2)), f)
    for k in range(2):
        inn.add(rounded_rect_ring(w / 2 - .08, h - .12, .06, .025, .015, 3, zone=Z.grey, base=d), f @ T((k - .5) * w / 2, 0, 0))
        inn.add(box(.03, .18, .03, zone=Z.steel, bevel=.006, center=((k - .5) * w / 2 + .16, 0, d + .015)), f)
for az in (105, 255):                              # ladders and handrails to the ceiling
    for z in np.arange(29.4, 39.2, .55):
        f = inward(on_liner(az, z, -.06)); inn.add(tube([(-.22, 0, 0), (-.22, 0, .14), (.22, 0, .14), (.22, 0, 0)], .016, 6, zone=Z.steel), f)
for az in (90, 135, 225, 270):
    pts = [tuple(inward(on_liner(az + 2, z, .26)) @ Vector((0, 0, 0))) for z in np.arange(29.2, 39.8, 1.2)]
    inn.add(tube(pts, .045, 8, zone=Z.rubber)); pts = [(p[0] * .985, p[1] * .985, p[2]) for p in pts]; inn.add(tube(pts, .02, 6, zone=Z.copper))
lamps = Geo()
for az, z in ((100, 39.0), (140, 39.0), (180, 39.0), (220, 39.0), (260, 39.0), (100, 33.2), (180, 33.2), (260, 33.2)):
    f = inward(on_liner(az, z, .03)); inn.add(box(.52, .16, .08, zone=Z.dark, bevel=.02, center=(0, 0, .03)), f)
    lamps.add(quad_patch(.46, .11, Z.lamp, .075), f)
    if z > 35:
        add_spot(P, 'bayLight', (f @ Vector((0, 0, .12))), (f.to_3x3() @ Vector((0, -.9, .6))), power=900, angle=95, reach=16)
inn.add(lamps)
P.mesh('bay', inn, P.det, smooth_angle=36)

# ---------------- doors
for nm, s in (('doorR', 1), ('doorL', -1)):
    keep = (lambda a, z: 0 < a < DA) if s > 0 else (lambda a, z: 360 - DA < a < 360)
    og = skin(D0 + .03, D1 - .03, 'fwd', O, extra=ext, keep=keep)
    ig = skin(D0 + .03, D1 - .03, 'fwd', O, extra=ext, keep=keep, off=-.20)
    lg = skin(D0 + .03, D1 - .03, 'fwd', O, extra=ext, keep=keep, off=-.20, flip=True)
    e0 = Vector(H.point(s * DA, D0, -.10)); e1 = Vector(H.point(s * DA, D1, -.02))
    e0, e1 = [(v - Vector((0, 0, O))) * K for v in (e0, e1)]
    e0 += Vector((math.sin(math.radians(s * DA)), -math.cos(math.radians(s * DA)), 0)) * -.02
    ax = frame_axes(e0, e1 - e0, x=Vector((math.sin(math.radians(s * DA)), -math.cos(math.radians(s * DA)), 0)))
    piv = P.empty(nm, ax, P.model)
    P.mesh(nm + '_skin', og, M, parent=piv, frame=ax, smooth_angle=32)
    d = Geo(); d.add(remap(lg, Z.wall)); d.add(wall(og, ig, Z.carbon))
    for z in (29.3, 31.2, 33.1, 35.0, 36.9, 38.6, 39.9):       # ribs
        rows = []; g = Geo()
        for i in range(11):
            a = s * (1.5 + (DA - 3) * i / 10); row = []
            for dr, dz in ((-.19, -.10), (-.42, -.07), (-.42, .07), (-.19, .10)):
                p = H.point(a, z + dz, dr); row.append(len(g.v)); g.v.append((float(p[0]) * K, float(p[1]) * K, zk(float(p[2]))))
            rows.append(row)
        for r0, r1 in zip(rows, rows[1:]):
            for k in range(3):
                q = [r0[k], r0[k + 1], r1[k + 1], r1[k]]
                g.face(q if s > 0 else q[::-1], [Z.grey.uv(0, k / 3), Z.grey.uv(0, (k + 1) / 3), Z.grey.uv(.3, (k + 1) / 3), Z.grey.uv(.3, k / 3)])
        d.add(g)
    for a in (14, 28, 42):                                     # stringers
        rows = []; g = Geo()
        for i in range(9):
            z = D0 + .3 + (D1 - D0 - .6) * i / 8; row = []
            for da, dr in ((-.7, -.19), (-.5, -.32), (.5, -.32), (.7, -.19)):
                p = H.point(s * a + da, z, dr); row.append(len(g.v)); g.v.append((float(p[0]) * K, float(p[1]) * K, zk(z)))
            rows.append(row)
        for r0, r1 in zip(rows, rows[1:]):
            for k in range(3):
                g.face([r0[k], r0[k + 1], r1[k + 1], r1[k]][::-1], [Z.alu.uv(0, k / 3), Z.alu.uv(0, (k + 1) / 3), Z.alu.uv(.3, (k + 1) / 3), Z.alu.uv(.3, k / 3)])
        d.add(g)
    for z in (30.2, 33.0, 35.8, 38.6):                         # latches along the split
        p = surf(s * 1.9, z, O, -.30); d.add(box(.14, .30, .22, zone=Z.steel, bevel=.02), p)
    P.mesh(nm + '_in', d, P.det, parent=piv, frame=ax, smooth_angle=34)
    for j, (a0, a1) in enumerate(((1, 20), (20, 40), (40, 59))):
        pts = []
        for a in (a0, a1):
            for z in (D0 + .1, 34, D1 - .1):
                for off in (0, -.2):
                    p = H.point(s * a, z, off); pts.append((float(p[0]) * K, float(p[1]) * K, zk(float(p[2]))))
        P.hull_collider(f'col_{nm}{j}', pts, parent=piv, frame=ax)
    q0 = P.rest_quat(piv)
    for f, deg in ((0, 0), (45, 58), (90, 112)):
        P.key('bayDoors', piv, f, rotation_quaternion=q0 @ Quaternion((0, 0, 1), math.radians(s * deg)))
    for z in (29.4, 31.6, 33.8, 36.0, 38.2, 39.8):             # hinge knuckles on the hull
        t = (z - D0) / (D1 - D0); c = e0 + (e1 - e0) * t
        det.add(cyl(.06, .34, 12, zone=Z.steel, bevel=.01), frame_axes(c, e1 - e0))
        det.add(box(.20, .24, .10, zone=Z.grey, bevel=.02), surf(s * (DA + 1.9), z, O, -.14))
P.mesh('detail', det, P.det)

# ---------------- colliders: hollow hold
def cp(a, z, off=0.0):
    p = H.point(a, z, off); return (float(p[0]) * K, float(p[1]) * K, zk(float(p[2])))
for k, a in enumerate(range(60, 300, 24)):
    P.hull_collider(f'col_wall{k}', [cp(aa, z, off) for aa in (a, a + 12, a + 24) for z in (28.6, 34, 40.3) for off in (0, LN)])
P.hull_collider('col_floor', [cp(a, z, -.02) for a in list(range(0, 360, 20)) for z in (27, 28.5)])
P.hull_collider('col_nose', [cp(a, z) for a in range(0, 360, 30) for z in (40.5, 43, 46, 48, 49.2)])
P.node('bottom', (0, 0, Z0), (0, 0, -1), 6)
P.node('cargo', (0, 0, fz + .14), (0, 0, 1), 3)
P.node('crane', (0, 0, cz), (0, 0, -1), 1)
P.bake_clips(0)
finish(P)

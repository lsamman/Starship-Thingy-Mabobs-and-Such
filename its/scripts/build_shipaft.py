"""Aft section of the ship: tanks, fairings, skirt and engine bay (z 0.8 to 27 m real)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
P = start('ITS_ShipAft'); O = H.O_AFT
M = P.material('its_aft', spec=(.55, .55, .56), shininess=.45)
zk = lambda z: (z - O) * K

P.mesh('hull', skin(0, H.Z_SPLIT, 'aft', O, skirt=True), M, smooth_angle=32)
det = Geo(); bay = Geo()

# ------------------------------------------------ skirt inside
WALL = .16
az = H.col_az(H.Z_R3); n = len(az)
def skirt_ring(off, t):
    z = H.skirt_z(az) * t + H.Z_R3 * (1 - t)
    r = H.RB + off
    return [(r * math.sin(math.radians(a)) * K, -r * math.cos(math.radians(a)) * K, zk(zz)) for a, zz in zip(az, z)]
inner = Geo(); rows = []
for t in (1, .66, .33, 0):
    rows.append([len(inner.v) + i for i in range(n)]); inner.v += skirt_ring(-WALL, t)
rows.append([len(inner.v) + i for i in range(n)])
inner.v += [(x, y, zk(11.6)) for x, y, _ in skirt_ring(-WALL, 0)]
for j, (a, b) in enumerate(zip(rows, rows[1:])):
    for k in range(n):
        k2 = (k + 1) % n
        s0, s1 = (az[k] % 60) / 60, (az[k] % 60 + (az[k2] - az[k]) % 360) / 60
        t0, t1 = (j / 4, (j + 1) / 4)
        inner.face([a[k2], a[k], b[k], b[k2]], [Z.wall.uv(min(s1, 1), t0), Z.wall.uv(s0, t0), Z.wall.uv(s0, t1), Z.wall.uv(min(s1, 1), t1)])
bay.add(inner)
rim = Geo(); o_, i_ = skirt_ring(0, 1), skirt_ring(-WALL, 1)
rim.v = o_ + i_
for k in range(n):
    k2 = (k + 1) % n
    rim.face([k, n + k, n + k2, k2], [Z.carbon.uv(0, 0), Z.carbon.uv(0, .12), Z.carbon.uv(.3, .12), Z.carbon.uv(.3, 0)])
bay.add(rim)
# skirt stringers, hoop frames
for a in np.arange(0, 360, 10):
    zb = float(H.skirt_z(a)) + .25
    r = H.RB - WALL
    p = lambda z, d: (Vector(((r - d) * math.sin(math.radians(a)), -(r - d) * math.cos(math.radians(a)), z - O))) * K
    g = box(.05, .09, (11.4 - zb) * K, zone=Z.carbon, bevel=.008)
    bay.add(g, T(*p((zb + 11.4) / 2, .06)) @ Rz(a))
for z in (5.4, 7.6, 9.6):
    bay.add(ring((H.RB - WALL - .26) * K, (H.RB - WALL) * K, zk(z) - .025, zk(z) + .025, Z.carbon, 72))

# ------------------------------------------------ thrust cone down to the sea-level engines (slide 36)
CZ, CR = (11.6, 9.8, 7.8, 5.6, 3.5), (5.82, 5.05, 3.75, 2.35, 1.35)
cone = lathe([(r * K, zk(z)) for z, r in zip(CZ, CR)][::-1], 72, zone=Z.dome)
bay.add(cone)
for k in range(24):
    a = 15 * k + 7.5
    for (z0, r0), (z1, r1) in zip(zip(CZ, CR), zip(CZ[1:], CR[1:])):
        p0 = on_cyl(a, zk(z0), r0 * K).translation; p1 = on_cyl(a, zk(z1), r1 * K).translation
        d = (p1 - p0); m = frame_axes((p0 + p1) / 2, d, x=on_cyl(a, 0, 1).translation.cross(Vector((0, 0, 1))))
        bay.add(box(.04, .13, d.length, zone=Z.carbon, bevel=.006), m)
zt = L.SL_Z                                   # engine mounting plane of the three center engines
bay.add(cyl(CR[-1] * K + .02, zk(3.5) - zt - .10, 36, zone=Z.alu, bevel=.015, center_z=False), T(0, 0, zt + .10))
for a in L.SL_AZ:
    c = on_cyl(a, 0, L.SL_R).translation
    bay.add(cyl(.30, .16, 24, zone=Z.steel, bevel=.02, center_z=False), T(c.x, c.y, zt))
    bay.add(bolts(12, .26), T(c.x, c.y, zt - .004) @ Rx(180))
    # LOX and CH4 feeds swept in from the cone
    for s in (-1, 1):
        p0 = on_cyl(a + s * 22, zk(6.2), 2.62 * K + .05).translation
        p1 = on_cyl(a + s * 26, zk(4.4), 2.3 * K).translation; p2 = on_cyl(a + s * 24, zt + .28, 1.75 * K).translation
        p3 = on_cyl(a + s * 10, zt + .14, 1.50 * K).translation
        bay.add(tube([tuple(p) for p in (p0, p1, p2, p3)], .085, 12, zone=Z.steel if s > 0 else Z.alu))
# ------------------------------------------------ vacuum engine mounts: tripods off the cone with a puck on top
for a in L.VAC_AZ:
    c = on_cyl(a, 0, L.VAC_R).translation; top = L.VAC_Z
    bay.add(cyl(.40, .20, 28, zone=Z.steel, bevel=.03, center_z=False), T(c.x, c.y, top))
    bay.add(cyl(.52, .07, 28, zone=Z.alu, bevel=.015, center_z=False), T(c.x, c.y, top + .18))
    bay.add(bolts(16, .46, .016), T(c.x, c.y, top + .25))
    for da, rr, zz in ((-13, 4.9, 9.55), (13, 4.9, 9.55), (0, 5.7, 10.6), (-18, 3.2, 6.9), (18, 3.2, 6.9)):
        bay.add(strut(on_cyl(a + da, zk(zz), rr * K).translation, Vector((c.x, c.y, top + .22)) + (on_cyl(a + da, 0, rr * K).translation - c).normalized() * .34, .055, Z.carbon))
    # feed line down from the cone
    q = on_cyl(a, 0, 1).translation
    bay.add(tube([tuple(Vector((c.x, c.y, top + .95)) + q * .1), tuple(Vector((c.x, c.y, top + .6)) + q * .06), tuple(Vector((c.x, c.y, top + .22)))], .13, 14, zone=Z.alu))
    bay.add(cyl(.17, .06, 16, zone=Z.steel, bevel=.012), T(c.x, c.y, top + .50) @ T(q.x * .05, q.y * .05, 0))
# ring manifolds and methalox RCS bottles hung between the mounts
for rr, zz, t, zn in ((2.75, 5.95, .07, Z.steel), (3.1, 6.5, .05, Z.alu), (4.35, 8.45, .06, Z.steel)):
    bay.add(tube([tuple(on_cyl(a, zk(zz), rr * K + .10).translation) for a in np.arange(0, 360, 7.5)], t, 8, zone=zn, closed=True))
for a in (0, 120, 180, 240):
    f = on_cyl(a, zk(9.0), 5.15 * K)
    bay.add(lathe([(0, -.62), (.16, -.56), (.25, -.40), (.25, .40), (.16, .56), (0, .62)], 18, zone=Z.copper if a % 120 else Z.white), f @ Rx(-90))
    for yy in (-.25, .25):
        bay.add(box(.62, .06, .06, zone=Z.dark, bevel=.01, center=(0, yy, .1)), f)
P.mesh('engine_bay', bay, P.det, smooth_angle=36)

# ------------------------------------------------ outside details
def port_set(spots, d=.26):
    g = Geo(); lead = groups(spots)
    for az_, z in spots:
        fr = surf(az_, z, O, 0.0); g.add(rcs_port(d), fr)
        if (az_, z) in lead:
            P.empty('RCSthruster', fr, P.model)
    return g
aft = [(s * a, z) for s in (1, -1) for a, z in ((40, 9.4), (40, 8.7), (86, 11.0), (86, 10.3), (86, 9.6), (86, 8.9), (150, 8.6), (150, 7.9))]
det.add(port_set(aft))
# propellant transfer and umbilical plates, leeward side where ships mate (render 20)
for s in (1, -1):
    h = Geo()
    h.add(box(.95, .62, .05, zone=Z.grey, bevel=.02, center=(0, 0, .0)))
    for sx in (-.24, .24):
        h.add(cyl(.15, .06, 24, zone=Z.steel, bevel=.012, center_z=False), T(sx, .03, .02))
        h.add(cyl(.09, .075, 20, zone=Z.dark, center_z=False), T(sx, .03, .02))
    for sx in (-.4, 0, .4):
        h.add(cyl(.035, .06, 10, zone=Z.alu, center_z=False), T(sx, -.22, .02))
    for sx in (-.24, .24):                             # probe cones reach past the hull so two ships can mate side by side
        h.add(lathe([(.14, .08), (.12, .20), (.09, .235), (0, .235)][::1], 20, zone=Z.steel), T(sx, .03, 0))
    det.add(stick(h, s * 62, 7.9, O))
    P.empty('dockA' if s > 0 else 'dockB', surf(s * 62, 7.9, O) @ T(0, 0, .24) @ Rx(90), P.model)
    f = surf(s * 62, 7.9, O); P.hull_collider('col_dock%d' % (s > 0), [tuple(f @ Vector((x, y, z))) for x in (-.4, .4) for y in (-.2, .25) for z in (-.1, .23)])
# joint ring at the top and the tank dome under the forward section
r = H.RB * K
det.add(ring(r - .30, r - .004, L.AFT_TOP - .16, L.AFT_TOP - .002, Z.carbon))
dome = lathe([(r - .28, L.AFT_TOP - .14)] + [((r - .30) * math.cos(t), L.AFT_TOP - .60 + .46 * math.sin(t) ** .8) for t in np.radians((0.01, 12, 30, 50, 70))] + [(0, L.AFT_TOP - .14)], 60, zone=Z.invar)
det.add(dome)
P.mesh('detail', det, P.det)

# ------------------------------------------------ colliders
def ringpts(z, full=True):
    az_ = np.concatenate([np.array([-9, 9, 40, 80]) + c for c in H.RIDGE_AZ])
    p = H.point(az_, z); return [(p[0][i] * K, p[1][i] * K, zk(z)) for i in range(len(az_))]
P.hull_collider('col_tank', sum((ringpts(z) for z in (6.4, 14.2, 15.6, 27)), []))
for k in range(12):
    a0, a1 = 30 * k, 30 * k + 30; pts = []
    for a in (a0, (a0 + a1) / 2, a1):
        for rr in (H.RB - .02, H.RB - .3):
            pts += [(rr * math.sin(math.radians(a)) * K, -rr * math.cos(math.radians(a)) * K, zk(z)) for z in (float(H.skirt_z(a)), 6.4)]
    P.hull_collider(f'col_skirt{k}', pts)
P.hull_collider('col_thrust', [tuple(on_cyl(a, zz, rr).translation) for a in range(0, 360, 45) for zz, rr in ((L.SL_Z + .02, .9), (zk(7.0), 1.9))])

P.node('top', (0, 0, L.AFT_TOP), (0, 0, 1), 6); P.node('bottom', (0, 0, L.AFT_BOT), (0, 0, -1), 6)
for i, a in enumerate(L.SL_AZ):
    c = on_cyl(a, 0, L.SL_R).translation; P.node(f'sl{i + 1}', (c.x, c.y, L.SL_Z), (0, 0, -1), 1)
for i, a in enumerate(L.VAC_AZ):
    c = on_cyl(a, 0, L.VAC_R).translation; P.node(f'vac{i + 1}', (c.x, c.y, L.VAC_Z), (0, 0, -1), 2)
for i, a in enumerate(L.LEG_AZ):
    f = on_cyl(a, zk(L.LEG_H[1]), L.LEG_H[0] * K); P.node(f'leg{i + 1}', f.translation, f.to_3x3() @ Vector((0, 0, 1)), 2)
for i, a in enumerate(L.FAN_AZ):
    f = on_cyl(a, zk(L.FAN_P[1]), L.FAN_P[0] * K); P.node(f'fan{i + 1}', f.translation, f.to_3x3() @ Vector((0, 0, -1)), 1)
finish(P)

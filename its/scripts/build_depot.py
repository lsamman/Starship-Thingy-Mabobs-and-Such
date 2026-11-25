"""Storage depot nose and stretched tank for the Expendable Block 3 Core, after the middle ship of NASA/SpaceX's "Starship Vehicle
Configurations" chart: bare bright steel, no flaps, no tiles, taller than the tanker. Origin at the joint's stack node; azimuth 0 is the
docking side. The raceways take over SEP's core's section (measured, as in build_racewaycap.py) and end in its tapered dome."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
from depot_layout import *
P = start('STMS_B3_Depot'); MS = sep_mat(P, 'stms_depot', 'stms_depot_diff', 'stms_depot_nrm', 'stms_steelmask_diff')
RR_ = [(ZB, HL.R), (ZJ, HL.R)] + [(ZJ + z, r) for z, r in HL.OGIVE[1:]] + [(ZJ + z, r) for z, r in HL.CAP[1:]]
rr = lambda z: float(np.interp(z, *zip(*RR_)))
pt = lambda az, z, o=0.0: V(((rr(z) + o) * math.sin(math.radians(az)), -(rr(z) + o) * math.cos(math.radians(az)), z))
N = 96; zs = sorted({ZB, *[ZB + RING * k for k in range(1, int((ZJ - ZB) / RING) + 1)], *[z for z, _ in RR_ if z < RR_[-1][0]], *[ZJ + x for x in (.42, 1.33, 2.2, 2.97, 3.75, 4.97, 6.0)]})
arc = [0.0]
for a, b in zip(zs, zs[1:]): arc.append(arc[-1] + math.hypot(b - a, rr(b) - rr(a)))      # metres along the skin, so the rings keep their height up the nose
g = Geo(); uv = lambda k, j: (k / N * 2, arc[j] / RING / 8)
for z in zs: g.v += [tuple(pt(k * 360 / N, z)) for k in range(N)]
for j in range(len(zs) - 1):
    for k in range(N):
        k2 = (k + 1) % N; g.face([j * N + k, j * N + k2, (j + 1) * N + k2, (j + 1) * N + k], [uv(k, j), uv(k + 1, j), uv(k + 1, j + 1), uv(k, j + 1)])
n = len(g.v); g.v.append((0, 0, RR_[-1][0])); j = len(zs) - 1
for k in range(N): g.face([j * N + k, j * N + (k + 1) % N, n], [uv(k, j), uv(k + 1, j), uv(k + .5, j)])
P.mesh('depot_hull', g, MS, smooth_angle=30)
w = Geo()                                                # weld beads
for z in np.arange(ZB + RING, ZJ + 6.2, RING):
    b = len(w.v); prof = ((-.014, -.002), (-.006, .005), (.006, .005), (.014, -.002))
    for dz, o in prof: w.v += [tuple(pt(k * 360 / N, z + dz, o)) for k in range(N)]
    for i in range(3):
        for k in range(N): k2 = (k + 1) % N; w.face([b + i * N + k, b + i * N + k2, b + (i + 1) * N + k2, b + (i + 1) * N + k], [(k / N * 2, i * .004), ((k + 1) / N * 2, i * .004), ((k + 1) / N * 2, i * .004 + .004), (k / N * 2, i * .004 + .004)])
for s in (-1, 1):                                        # raceways
    rows = []; ends = [(dz + ZE, a, c) for dz, a, c in RINGS]; col = [(z, 1, 1) for z in np.arange(ZB - .002, ZE - .5, 1.2)] + ends
    for z, wd, hh in col:
        b = len(w.v); rows.append((b, z))
        for az, r in SEC: t = math.radians(s * (C + (az - C) * wd)); r_ = R0 + (r + .003 - R0) * hh; w.v.append((r_ * math.sin(t), -r_ * math.cos(t), z))
    m = len(SEC)
    for (a, za), (b, zb) in zip(rows, rows[1:]):
        for k in range(m - 1): f = [a + k, a + k + 1, b + k + 1, b + k]; u = [(k / m * .25, za / RING / 8), ((k + 1) / m * .25, za / RING / 8), ((k + 1) / m * .25, zb / RING / 8), (k / m * .25, zb / RING / 8)]; w.face(f if s < 0 else f[::-1], u if s < 0 else u[::-1])
P.mesh('depot_trim', w, MS, smooth_angle=50)
d = Geo(); F = lambda az, z, o=0.0: frame_axes(tuple(pt(az, z, o)), z=V((math.sin(math.radians(az)), -math.cos(math.radians(az)), 0)))
MP = P.material('its_solar', spec=(.25, .25, .28), shininess=.6); pn = Geo()      # skin panels for the coolers, on the side away from the docking hardware
for i in range(3):
    A, B = 162.5 + 12 * i, 173.5 + 12 * i
    for j in range(13):
        za, zb = .35 + j * .72, .35 + (j + 1) * .72 - .05; q = [pt(A, za, .034), pt(B, za, .034), pt(B, zb, .034), pt(A, zb, .034)]; n = len(pn.v); pn.v += [tuple(p) for p in q]; s = (i + j) % 4
        pn.face([n, n + 1, n + 2, n + 3], [(.02, (s + .02) / 4), (.98, (s + .02) / 4), (.98, (s + .98) / 4), (.02, (s + .98) / 4)])
        b = [pt(az, z, o) for o in (-.02, .029) for az, z in ((A - .2, za - .012), (B + .2, za - .012), (B + .2, zb + .012), (A - .2, zb + .012))]; n = len(d.v); d.v += [tuple(p) for p in b]
        for f in ((4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): d.face([n + x for x in f], [Z.alu.uv(*u) for u in ((0, 0), (.3, 0), (.3, .3), (0, .3))])
P.mesh('depot_panels', pn, MP)
P.empty('depotSun', Matrix(((-1, 0, 0, 0), (0, 1, 0, HL.R + .25), (0, 0, 1, 5.0), (0, 0, 0, 1))), P.model)
for az in (60, 300):                                     # vents
    for z in (9.2, 9.5): d.add(cyl(.075, .05, 20, zone=Z.dark, bevel=.01), F(az, z) @ T(0, 0, .012)); d.add(cyl(.05, .06, 18, zone=Z.grey), F(az, z) @ T(0, 0, .014))
for az in (80, 100, 260, 280):                           # roll, yaw and pitch thrusters, and the pair that settles propellant
    for dz, v_ in ((0, (1, 0, .35)), (.28, (-1, 0, .35)), (.56, (0, 1, .35)), (-.28, (0, -1, .35))):
        z = ZJ + .55 + dz; f = F(az, z); f2 = f.copy(); dd = f.to_3x3() @ V((v_[0], v_[1], v_[2])).normalized()
        d.add(cyl(.075, .012, 18, zone=Z.alu), f); d.add(cyl(.052, .02, 14, zone=Z.rubber), f); P.empty('RCSthruster', frame_axes(f.translation + f.to_3x3() @ V((0, 0, .03)), dd), P.model)
d.add(lathe([(HL.R - .004, ZB), (2.765, ZB), (2.765, .30), (2.36, .33), (0, .36)], N, zone=Z.wall, flip=True))
P.mesh('depot_detail', d, P.det, smooth_angle=40)
ring_ = lambda z: [tuple(pt(k * 15, z)) for k in range(24)]
for i, (a, b) in enumerate(((.36, ZJ), (ZJ, ZJ + 1.82), (ZJ + 1.82, ZJ + 3.36), (ZJ + 3.36, ZJ + 4.64), (ZJ + 4.64, ZJ + 5.81), (ZJ + 5.81, ZJ + 7.4), (ZJ + 7.4, ZJ + 8.5))): P.hull_collider(f'col{i}', ring_(a) + ring_(b))
for k in range(12): P.hull_collider(f'col_s{k}', [tuple(p * 1) for a in (30 * k, 30 * k + 15, 30 * k + 30) for z in (ZB, .40) for p in (pt(a, z), pt(a, z, -.06))])
P.node('bottom', (0, 0, 0), (0, 0, -1), 5)
P.variants = (); finish(P)

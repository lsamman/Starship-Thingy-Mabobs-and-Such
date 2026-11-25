"""HLS cargo section, after SpaceX's cargo lander render (April 2024): smooth white ogive, one wide door that swings up like an awning, and a
crane frame that leans out of the bay over the winch's load. z = 0 at the barrel-ogive joint (HL.Z_OGIVE); door at azimuth 0."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Cargo'); MH = hull_mat(P, 'hls_cargo'); O = HL.Z_OGIVE; up = V((0, 0, O)); AZ = HL.CG_AZ; S0, H0 = HL.CG_SILL, HL.CG_HEAD; ZB = HL.Z_SKIN - O; FL, CE = HL.CG_FLOOR, HL.CG_CEIL
h = lambda a, z, r=None, off=0.0: hp(a, z + O, off, r) - up
R_ = lambda z: rad(z + O)
rz = [z for z, _ in HL.OGIVE]
zs = sorted({ZB, S0, 0.0, H0, *rz, -1.2, .42, 1.33, 2.2, 2.97, 3.75, 4.97, 6.0})
indoor = lambda a, z: abs(wrap(a)) < AZ and S0 < z < H0
g = skin([z + O for z in zs], 'cargo', O, lambda a, z: not indoor(a, z - O))
cz = [O + z for z, _ in HL.CAP]; tip = skin([z for z in cz if z < O + 8.56], 'cargo', O); k = len(g.v); g.v += tip.v; [g.face([i + k for i in f], u) for f, u in zip(tip.f, tip.uv)]
ids = sorted([i for i, p in enumerate(g.v) if abs(p[2] - 8.555) < 1e-4], key=lambda i: math.atan2(g.v[i][0], -g.v[i][1])); n = len(g.v); g.v.append((0, 0, 8.565))
for a, b in zip(ids, ids[1:] + ids[:1]): g.face([a, b, n], [(.5, .99)] * 3)
P.mesh('hull', g, MH, smooth_angle=30)
d = Geo(); TH = .09                                       # bay lining, ribs, jambs
iz = [z for z in zs if FL < z < CE] ; iz = [FL] + iz + [CE]; SI = 3.75
for z0, z1 in zip(iz, iz[1:]):
    for i in range(96):
        a0, a1 = i * SI, (i + 1) * SI
        if indoor((a0 + a1) / 2, (z0 + z1) / 2): continue
        q = [h(a0, z0, R_(z0) - TH), h(a0, z1, R_(z1) - TH), h(a1, z1, R_(z1) - TH), h(a1, z0, R_(z0) - TH)]; n = len(d.v); d.v += [tuple(p) for p in q]
        d.face(range(n, n + 4), [Z.wall.uv((i % 8 + t) / 8, (z - FL) / 5) for t, z in ((0, z0), (0, z1), (1, z1), (1, z0))])
def strip(A, B, zone):
    n = len(d.v); d.v += [tuple(p) for p in (A[0], B[0], B[1], A[1])]; d.face(range(n, n + 4), [zone.uv(*t) for t in ((0, 0), (.1, 0), (.1, .1), (0, .1))])
for s in (-1, 1):                                        # jambs, sill, head
    jz = [z for z in zs if S0 <= z <= H0]
    for a, b in zip(jz, jz[1:]):
        A, B = (h(s * AZ, a), h(s * AZ, a, R_(a) - TH)), (h(s * AZ, b), h(s * AZ, b, R_(b) - TH)); strip(A, B, Z.white) if s < 0 else strip(B, A, Z.white)
for i in range(28):
    a, b = -AZ + i * SI, -AZ + (i + 1) * SI
    strip((h(a, S0), h(a, S0, R_(S0) - TH)), (h(b, S0), h(b, S0, R_(S0) - TH)), Z.white)
    strip((h(b, H0), h(b, H0, R_(H0) - TH)), (h(a, H0), h(a, H0, R_(H0) - TH)), Z.white)
    strip((h(a, S0, R_(S0) - TH), h(a, FL, R_(FL) - TH)), (h(b, S0, R_(S0) - TH), h(b, FL, R_(FL) - TH)), Z.wall)
ci = [tuple(h(a, CE, R_(CE) - TH)) for a in np.arange(AZ, 360 - AZ + .1, SI)]; fl = [tuple(h(i * SI, FL, R_(FL) - TH)) for i in range(96)]
d.add(plate([p[:2] for p in fl], [], FL, Z.deck, up=True)); d.add(plate([p[:2] for p in ci], [], CE, Z.wall, up=False))
for a in np.arange(60, 301, 12.0):                       # stringers and ring frames on the back wall
    d.add(tube([tuple(h(a, z, R_(z) - TH - .02)) for z in iz], .03, 5, zone=Z.alu))
for z in (-1.2, .42, 1.33): d.add(tube([tuple(h(a, z, R_(z) - TH - .04)) for a in np.arange(AZ + 2, 360 - AZ - 1.9, 4)], .05, 6, zone=Z.alu))
for s in (-1, 1):
    for x in (.5, 1.3): d.add(box(.10, 3.4, .05, zone=Z.grey, bevel=.01, center=(s * x, .2, FL + .02)))
d.add(box(1.5, 1.5, .02, zone=Z.alu, bevel=.008, center=(0, 0, CE - .008)))      # winch plate
d.add(lathe([(R_(ZB) - .004, ZB), (2.765, ZB), (2.765, ZB + .25), (2.36, -3.26), (1.6, -3.0), (0, -2.85)], 96, zone=Z.wall, flip=True))
# ---------------- door: hinged along its top edge; the curved sides tuck down into the opening as it comes up
HY, HZ = -R_(H0) + .02, H0 - .03; hf = T(0, HY, HZ); door = P.empty('door', hf, P.model); ds, di = Geo(), Geo(); e = .22
dz_ = [S0 + .055] + [z for z in zs if S0 < z < H0] + [H0 - .008]; da = [-AZ + i * SI for i in range(29)]; cl = lambda a: max(-AZ + e, min(AZ - e, a)); DT = .10
for z0, z1 in zip(dz_, dz_[1:]):
    for a0, a1 in zip(da, da[1:]):
        q = [(a0, z0), (a1, z0), (a1, z1), (a0, z1)]; n = len(ds.v); ds.v += [tuple(h(cl(a), z)) for a, z in q]; ds.face(range(n, n + 4), [huv(abs(a), z + O, 'cargo') for a, z in q])
        n = len(di.v); di.v += [tuple(h(cl(a), z, R_(z) - DT)) for a, z in q[::-1]]; di.face(range(n, n + 4), [Z.alu.uv((a + AZ) / 105, (z - S0) / 5.2) for a, z in q[::-1]])
for s in (-1, 1):
    for z0, z1 in zip(dz_, dz_[1:]):
        f = [h(s * (AZ - e), z0), h(s * (AZ - e), z0, R_(z0) - DT), h(s * (AZ - e), z1, R_(z1) - DT), h(s * (AZ - e), z1)]; f = f if s < 0 else f[::-1]; n = len(di.v); di.v += [tuple(p) for p in f]; di.face(range(n, n + 4), [Z.white.uv(*t) for t in ((0, 0), (.1, 0), (.1, .1), (0, .1))])
for z, fw in ((dz_[0], 1), (dz_[-1], 0)):
    for a0, a1 in zip(da, da[1:]):
        f = [h(cl(a0), z), h(cl(a0), z, R_(z) - DT), h(cl(a1), z, R_(z) - DT), h(cl(a1), z)]; f = f[::-1] if not fw else f; n = len(di.v); di.v += [tuple(p) for p in f]; di.face(range(n, n + 4), [Z.white.uv(*t) for t in ((0, 0), (.1, 0), (.1, .1), (0, .1))])
for z in np.arange(S0 + .35, H0 - .3, .62):              # ribs across the inside, and the truss at the hinge end
    di.add(tube([tuple(h(a, float(z), R_(z) - DT - .03)) for a in np.arange(-AZ + 1.5, AZ - 1.4, 3)], .045, 6, zone=Z.alu))
for a in (-36, -18, 0, 18, 36): di.add(tube([tuple(h(a, float(z), R_(z) - DT - .03)) for z in np.linspace(S0 + .1, H0 - .25, 12)], .035, 6, zone=Z.alu))
rib = np.arange(S0 + .35, H0 - .3, .62)
for i, (z0, z1) in enumerate(zip(rib[-4:], rib[-3:])):
    for a0, a1 in ((-36, -18), (-18, 0), (0, 18), (18, 36)):
        p, q = ((a0, z0), (a1, z1)) if i % 2 else ((a1, z0), (a0, z1)); di.add(strut(h(p[0], float(p[1]), R_(p[1]) - DT - .04), h(q[0], float(q[1]), R_(q[1]) - DT - .04), .025, Z.white, 5))
for a in np.arange(-AZ + 4, AZ - 3, 7): di.add(box(.07, .05, .10, zone=Z.steel, bevel=.01), T(*h(float(a), S0 + .13, R_(S0) - DT - .02)) @ Rz(float(a)))      # latches along the lower edge
for x in (-.9, 0, .9): di.add(box(.16, .12, .14, zone=Z.white, bevel=.02), T(x, -math.sqrt(max(.1, (R_(H0) - .13) ** 2 - x * x)) + .02, HZ - .08))
P.mesh('doorskin', ds, MH, parent=door, frame=hf, smooth_angle=30); P.mesh('doorframe', di, P.det, parent=door, frame=hf)
q0 = P.rest_quat(door)
for f, a in ((0, 0), (90, -HL.CG_SWING)): P.key('CargoDoor', door, f, rotation_quaternion=q0 @ Quaternion((1, 0, 0), math.radians(a)))
for i in range(7):
    a0, a1 = -AZ + 15 * i, -AZ + 15 * (i + 1)
    P.hull_collider(f'col_door{i}', [tuple(h(a, z, R_(z) - o)) for a in (a0, (a0 + a1) / 2, a1) for z in (S0 + .02, 0, H0 - .02) for o in (0, .09)], parent=door, frame=hf)
# ---------------- crane frame: two telescoping legs on the sill and a crossbar; it leans out over the load
X, Y, Z0, LL, EX = HL.FRAME_X, HL.FRAME_Y, HL.FRAME_Z, HL.FRAME_L, HL.FRAME_OUT; ff = T(0, Y, Z0); fr, tp = Geo(), Geo(); XT = HL.FRAME_TOPX
leg_ = lambda s, l: (s * (X - (X - XT) * l / LL), Y, Z0 + l)
for s in (-1, 1):
    fr.add(tube([leg_(s, 0), leg_(s, LL - .35)], .065, 12, zone=Z.grey)); fr.add(cyl(.10, .20, 14, zone=Z.steel, bevel=.01), T(s * X, Y, Z0) @ Ry(90)); fr.add(tube([leg_(s, LL - .47), leg_(s, LL - .33)], .085, 12, zone=Z.alu))
    p = leg_(s, 1.5); fr.add(tube([p, (p[0], Y + .26, Z0 + .2)], .03, 8, zone=Z.alu)); fr.add(box(.10, .14, .12, zone=Z.alu, bevel=.015), T(p[0], Y + .02, p[2]))
    tp.add(tube([leg_(s, LL - EX - .55), leg_(s, LL)], .048, 12, zone=Z.alu)); tp.add(box(.14, .12, .12, zone=Z.grey, bevel=.02), T(*leg_(s, LL)))
    d.add(box(.12, .22, Z0 - FL + .04, zone=Z.grey, bevel=.015), T(s * X, Y, (Z0 + FL) / 2))
tp.add(box(2 * XT, .10, .10, zone=Z.grey, bevel=.015), T(0, Y, Z0 + LL))
for x in (-.9, .9): tp.add(box(.14, .12, .12, zone=Z.alu, bevel=.02), T(x, Y, Z0 + LL)); tp.add(cyl(.06, .05, 14, zone=Z.steel, bevel=.008), T(x, Y - .08, Z0 + LL - .02) @ Ry(90))
fp = P.mesh('craneFrame', fr, P.det, parent=P.model, frame=ff); ft = P.mesh('craneTop', tp, P.det, parent=fp, frame=T(0, Y, Z0 + LL)); qf = P.rest_quat(fp); lt = ft.location.copy()
for f, a in ((0, 0), (60, HL.FRAME_LEAN), (100, HL.FRAME_LEAN)): P.key('craneFrameOut', fp, f, rotation_quaternion=qf @ Quaternion((1, 0, 0), math.radians(a)))
for f, x in ((0, 0), (40, 0), (100, EX)): P.key('craneFrameOut', ft, f, location=lt + V((0, 0, x)))
# ---------------- flag on the nose, RCS, colliders, nodes
fx, fy, fw, fh = L.FLAG; fl_ = Geo().add(lay(quad_patch(.95, .50, Zone(fx, fy, fw, fh, atlas=2048), nx=8, ny=4), 0, O + 5.1, O, sink=-.004)); P.mesh('flag', fl_, P.det)
spots = []
for az in (80, 100, 260, 280):
    z = O + .55; spots += [(az, z, (1, 0, .35)), (az, z + .28, (-1, 0, .35)), (az, z + .56, (0, 1, .35)), (az, z - .28, (0, -1, .35))]
rcs(P, d, spots, O); P.mesh('details', d, P.det, smooth_angle=40)
ring_ = lambda z, a0, a1, n, r=None: [tuple(h(a0 + (a1 - a0) * i / n, z, r)) for i in range(n + 1)]
for i in range(10):
    a0 = AZ + i * (360 - 2 * AZ) / 10; a1 = AZ + (i + 1) * (360 - 2 * AZ) / 10
    P.hull_collider(f'col_w{i}', [p for z in (ZB, 0) for o in (0, .12) for p in ring_(z, a0, a1, 3, R_(z) - o)]); P.hull_collider(f'col_v{i}', [p for z in (0, H0) for o in (0, .12) for p in ring_(z, a0, a1, 3, R_(z) - o)])
P.hull_collider('col_floor', [p for z, r in ((FL - .045, 1.2), (FL - .2, 1.9), (FL, 2.7)) for p in ring_(z, 0, 345, 23, r)])
for i in range(7): P.hull_collider(f'col_sill{i}', [p for z in (ZB, S0) for o in (0, .12) for p in ring_(z, -AZ + 15 * i, -AZ + 15 * i + 15, 3, HL.R - o)])
P.hull_collider('col_ceil', [p for z in (CE, H0) for p in ring_(z, AZ, 360 - AZ, 24, R_(H0) - .16)])
for i, (za, zb) in enumerate(((H0, 4.13), (4.13, 5.81), (5.81, 7.40), (7.40, 8.52))): P.hull_collider(f'col_n{i}', [p for z in (za, zb) for p in ring_(z, 0, 345, 23)])
P.node('bottom', (0, 0, HL.Z_TOP - O), (0, 0, -1), 5); P.node('cargo', (0, 0, FL), (0, 0, 1), 4); P.node('winch', (0, 0, CE), (0, 0, -1), 3)
P.bake_clips(0); finish(P)

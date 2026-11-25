"""HLS cargo section, after SpaceX's cargo lander render (April 2024): smooth white ogive, one wide door that swings up like an awning, and a bay
for the crane frame (build_hlscrane.py) or the winch boom. z = 0 at the barrel-ogive joint (HL.Z_OGIVE); door at azimuth 0."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_CargoAwning'); MH = hull_mat(P, 'hls_cargo'); O = HL.Z_OGIVE; up = V((0, 0, O)); AZ = HL.CG_AZ; S0, H0 = HL.CG_SILL, HL.CG_HEAD; ZB = HL.Z_SKIN - O; FL, CE = HL.CG_FLOOR, HL.CG_CEIL
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
TP = HL.CG_TOP; d, st = Geo(), Geo(); TH, SI, RB = .09, 3.75, .055; MB = sep_mat(P, 'stms_bay', 'stms_bay_diff', 'stms_bay_nrm', 'stms_steelmask_diff')
def sq(g, q, u):                                         # a quad of bay steel, mapped in metres
    n = len(g.v); g.v += [tuple(p) for p in q]; g.face(range(n, n + 4), [(x / 4, y / 4) for x, y in u])
def sheet(g, a0, a1, z0, z1, depth):
    r = math.radians(a1 - a0) * 2.6; x = math.radians(a0) * 2.6; sq(g, [h(a0, z0, R_(z0) - depth), h(a0, z1, R_(z1) - depth), h(a1, z1, R_(z1) - depth), h(a1, z0, R_(z0) - depth)], [(x, z0), (x, z1), (x + r, z1), (x + r, z0)])
def stringer(g, a, rows, depth, w=.034, f=.6):           # hat section standing in from the sheet
    for z0, z1 in zip(rows, rows[1:]):
        da = lambda z, k: math.degrees(w * k / R_(z)); lo = [h(a + da(z0, k), z0, R_(z0) - depth - o) for k, o in ((-1, -.004), (-f, RB), (f, RB), (1, -.004))]; hi = [h(a + da(z1, k), z1, R_(z1) - depth - o) for k, o in ((-1, -.004), (-f, RB), (f, RB), (1, -.004))]
        for k in range(3): sq(g, [lo[k], hi[k], hi[k + 1], lo[k + 1]], [(k * .05, z0), (k * .05, z1), (k * .05 + .05, z1), (k * .05 + .05, z0)])
iz = [FL] + [z for z in zs if FL < z < TP] + [TP]
for z0, z1 in zip(iz, iz[1:]):
    for i in range(96):
        a0, a1 = i * SI, (i + 1) * SI
        if not indoor((a0 + a1) / 2, (z0 + z1) / 2): sheet(st, a0, a1, z0, z1, TH)
for i in range(96):
    a = (i + .5) * SI; inside = abs(wrap(a)) < AZ
    stringer(st, a, [z for z in iz if z >= H0] if inside else iz, TH)
for z in (-1.2, .42, 2.97, 3.75):                        # hoops
    full = z > H0; A = np.arange(0, 360.1, 4) if full else np.arange(AZ + 1.5, 360 - AZ - 1.4, 4)
    st.add(tube([tuple(h(a, z, R_(z) - TH - RB - .02)) for a in A], .04, 6))
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
fl = [tuple(h(i * SI, FL, R_(FL) - TH)) for i in range(96)]; d.add(plate([p[:2] for p in fl], [], FL, Z.deck, up=True)); P.two_sided = True
for s in (-1, 1):
    for x in (.5, 1.3): d.add(box(.10, 3.4, .05, zone=Z.grey, bevel=.01, center=(s * x, .2, FL + .02)))
# ---------------- under the nose: flanged bulkhead ring with ribs, the dark of the nose behind it, and the header tank coming through
RT = R_(TP) - TH; st.add(lathe([(RT, TP - .10), (RT - .10, TP - .10), (RT - .10, TP), (1.55, TP + .02), (1.55, TP - .05), (1.50, TP - .05), (1.50, TP + .10)], 96, flip=True))
d.add(lathe([(1.50, TP + .10), (1.50, TP + .9), (1.2, TP + 1.5), (.3, TP + 1.9), (0, TP + 1.9)], 64, zone=Z.black, flip=True))
for k in range(16):
    a = 22.5 * k + 11.25; c_ = V((math.sin(math.radians(a)), -math.cos(math.radians(a)), 0)); st.add(tube([tuple(c_ * 1.52 + V((0, 0, TP - .03))), tuple(c_ * (RT - .07) + V((0, 0, TP - .08)))], .035, 5)); st.add(tube([tuple(c_ * 1.48 + V((0, 0, TP + .05))), tuple(c_ * .98 + V((0, 0, TP + .62)))], .03, 5))
ZC_, RC = TP + .72, 1.05; hd = [(RC * math.sin(math.radians(t)), ZC_ - RC * math.cos(math.radians(t))) for t in range(30, 141, 10)]; st.add(lathe([(0, TP - .42), (.10, TP - .40), (.30, TP - .28)] + hd, 48))
for x in (-.16, .16): st.add(tube([(x, .0, TP - .30), (x, .35, TP - .42), (x, 1.2, TP - .34), (x, 1.80, TP - .50)] + [(x, float(R_(z) - TH - .20), float(z)) for z in (3.2, 2.2, 1.0, 0, -1.4, FL + .02)], .075, 12))      # downcomers
for s in (-1, 1):                                        # gas bottles along the back wall
    for k, z0 in ((0, -2.55), (1, -2.55), (0, -1.05)): a = 180 + s * (20 + 8 * k); p = h(a, z0, HL.R - TH - .26); d.add(tube([tuple(p), tuple(p + V((0, 0, 1.3)))], .125, 16, zone=Z.black)); d.add(tube([tuple(p + V((0, 0, .06))), tuple(p + V((0, 0, .12)))], .135, 16, zone=Z.alu)); d.add(tube([tuple(p + V((0, 0, 1.16))), tuple(p + V((0, 0, 1.22)))], .135, 16, zone=Z.alu))
wm = Geo(); wm.add(box(1.5, 1.5, .02, zone=Z.alu, bevel=.008, center=(0, 0, CE + .012)))      # mount for the winch boom, hidden unless wanted: the crane frame doesn't need it
for y in (-.6, .6):
    xw = math.sqrt((R_(CE) - TH - .03) ** 2 - y * y); wm.add(box(2 * xw, .12, .16, zone=Z.alu, bevel=.015, center=(0, y, CE + .10))); wm.add(box(2 * xw, .20, .02, zone=Z.alu, center=(0, y, CE + .19)))
P.mesh('winchmount', wm, P.det)
d.add(lathe([(R_(ZB) - .004, ZB), (2.765, ZB), (2.765, ZB + .25), (2.36, -3.26), (1.6, -3.0), (0, -2.85)], 96, zone=Z.wall, flip=True))
# ---------------- door: hinged along its top edge; the curved sides tuck down into the opening as it comes up
HY, HZ = -R_(H0) + .02, H0 - .03; hf = T(0, HY, HZ); door = P.empty('door', hf, P.model); ds, di, db = Geo(), Geo(), Geo(); e = .22
dz_ = [S0 + .055] + [z for z in zs if S0 < z < H0] + [H0 - .008]; da = [-AZ + i * SI for i in range(29)]; cl = lambda a: max(-AZ + e, min(AZ - e, a)); DT = .10
for z0, z1 in zip(dz_, dz_[1:]):
    for a0, a1 in zip(da, da[1:]):
        q = [(a0, z0), (a1, z0), (a1, z1), (a0, z1)]; n = len(ds.v); ds.v += [tuple(h(cl(a), z)) for a, z in q]; ds.face(range(n, n + 4), [huv(abs(a), z + O, 'cargo') for a, z in q])
        sq(db, [h(cl(a), z, R_(z) - DT) for a, z in q[::-1]], [(math.radians(a) * 2.6, z) for a, z in q[::-1]])
for s in (-1, 1):
    for z0, z1 in zip(dz_, dz_[1:]):
        f = [h(s * (AZ - e), z0), h(s * (AZ - e), z0, R_(z0) - DT), h(s * (AZ - e), z1, R_(z1) - DT), h(s * (AZ - e), z1)]; f = f if s < 0 else f[::-1]; n = len(di.v); di.v += [tuple(p) for p in f]; di.face(range(n, n + 4), [Z.white.uv(*t) for t in ((0, 0), (.1, 0), (.1, .1), (0, .1))])
for z, fw in ((dz_[0], 1), (dz_[-1], 0)):
    for a0, a1 in zip(da, da[1:]):
        f = [h(cl(a0), z), h(cl(a0), z, R_(z) - DT), h(cl(a1), z, R_(z) - DT), h(cl(a1), z)]; f = f[::-1] if not fw else f; n = len(di.v); di.v += [tuple(p) for p in f]; di.face(range(n, n + 4), [Z.white.uv(*t) for t in ((0, 0), (.1, 0), (.1, .1), (0, .1))])
rows_ = [S0 + .10] + [z for z in zs if S0 + .2 < z < H0 - .3] + [H0 - .30]
for i in range(28): stringer(db, -AZ + (i + .5) * SI, rows_, DT)
for z in (-1.2, .42, 2.0): db.add(tube([tuple(h(a, z, R_(z) - DT - RB - .015)) for a in np.arange(-AZ + 2, AZ - 1.9, 3)], .035, 6))
# inside hinges: brackets hung from the frame over the opening, arms curving down onto the door, a spreader tying them to its first hoop
for x in (-.42, 0, .42):
    pv = V((x, HY + .02, HZ)); yb = -math.sqrt((R_(HZ + .42) - TH - .02) ** 2 - x * x)
    for q in (-.075, .075): d.add(box(.03, .15, .50, zone=Z.alu, bevel=.01), T(x + q, (pv.y + yb) / 2 + .08, HZ + .20) @ Rx(math.degrees(math.atan2(yb - pv.y, .42)) * -1)); d.add(cyl(.042, .035, 18, zone=Z.grey, bevel=.008), T(x + q, HY, HZ) @ Ry(90))
    d.add(box(.30, .06, .30, zone=Z.alu, bevel=.012), T(x, yb + .05, HZ + .40)); d.add(cyl(.028, .26, 14, zone=Z.steel), T(x, HY, HZ) @ Ry(90))
    path = [V((x, HY, HZ)), V((x, pv.y + .10, pv.z - .10)), V((x, pv.y + .12, pv.z - .30))] + [h(math.degrees(math.asin(x / R_(z))), z, R_(z) - DT - .09) for z in (2.0, 1.4)]
    for q in (-.03, .03): di.add(tube([tuple(p + V((q, 0, 0))) for p in path], .032, 8, zone=Z.white))
    di.add(cyl(.04, .10, 16, zone=Z.white, bevel=.008), T(x, HY, HZ) @ Ry(90)); di.add(box(.24, .07, .16, zone=Z.white, bevel=.015), T(x, -math.sqrt((R_(1.4) - DT - .06) ** 2 - x * x), 1.4))
for s in (-1, 1): di.add(strut(h(s * 9.3, 2.0, R_(2.0) - DT - .09), h(s * 30, 1.4, R_(1.4) - DT - .08), .032, Z.white, 8)); di.add(strut(h(s * 9.3, 1.4, R_(1.4) - DT - .09), h(s * 36, .42, R_(.42) - DT - .09), .032, Z.white, 8))
di.add(tube([tuple(h(a, 2.0, R_(2.0) - DT - .10)) for a in np.arange(-14, 14.1, 4)], .04, 8, zone=Z.white))
d.add(box(.55, .16, .18, zone=Z.dark, bevel=.025), T(-.21, -R_(3.0) + .28, 2.93)); d.add(cyl(.07, .50, 18, zone=Z.grey, bevel=.01), T(.22, -R_(3.0) + .28, 2.93) @ Ry(90))      # drive
for a in np.arange(-AZ + 4, AZ - 3, 7): di.add(box(.07, .05, .10, zone=Z.steel, bevel=.01), T(*h(float(a), S0 + .13, R_(S0) - DT - .02)) @ Rz(float(a)))      # latches along the lower edge
P.mesh('doorskin', ds, MH, parent=door, frame=hf, smooth_angle=30); P.mesh('doorframe', di, P.det, parent=door, frame=hf); P.mesh('doorbay', db, MB, parent=door, frame=hf, smooth_angle=35); P.mesh('bay', st, MB, smooth_angle=35)
q0 = P.rest_quat(door)
for f, a in ((0, 0), (90, -HL.CG_SWING)): P.key('CargoDoor', door, f, rotation_quaternion=q0 @ Quaternion((1, 0, 0), math.radians(a)))
for i in range(7):
    a0, a1 = -AZ + 15 * i, -AZ + 15 * (i + 1)
    P.hull_collider(f'col_door{i}', [tuple(h(a, z, R_(z) - o)) for a in (a0, (a0 + a1) / 2, a1) for z in (S0 + .02, 0, H0 - .02) for o in (0, .09)], parent=door, frame=hf)
# ---------------- ramp over the sill, folded inward on its hinge; level with a lowered floor when out
RY, RZ_, RW, RL = HL.RAMP_Y, HL.RAMP_Z, HL.RAMP_W, HL.RAMP_L; rf = T(0, RY, RZ_ - .03); ramp = P.empty('ramp', rf, P.model); rg = Geo()
rg.add(box(2 * RW, RL - .06, .035, zone=Z.deck, bevel=.006), T(0, RY - RL / 2 - .01, RZ_ - .0175)); rg.add(box(2 * RW, .07, .037, zone=Z.stripe), T(0, RY - RL + .045, RZ_ - .0175))
for x in np.linspace(-RW + .1, RW - .1, 5): rg.add(box(.07, RL - .12, .03, zone=Z.alu, bevel=.006), T(float(x), RY - RL / 2, RZ_ - .05))
for x in (-1.2, 0, 1.2):                                 # leaf knuckles and straps onto the plate; the fixed knuckles and pins are on the posts
    for q in (-.055, .055): rg.add(cyl(.042, .05, 16, zone=Z.grey, bevel=.006), T(x + q, RY, RZ_ - .03) @ Ry(90))
    rg.add(box(.16, .34, .016, zone=Z.alu, bevel=.004), T(x, RY - .20, RZ_ - .043)); [rg.add(cyl(.014, .008, 8, zone=Z.steel), T(x + a_, RY - b_, RZ_ - .054) @ Rx(180)) for a_ in (-.05, .05) for b_ in (.12, .30)]
rg.add(tube([(-.95, RY, RZ_ - .03), (-.16, RY, RZ_ - .03)], .022, 10, zone=Z.steel)); rg.add(tube([(.16, RY, RZ_ - .03), (.95, RY, RZ_ - .03)], .022, 10, zone=Z.steel))
P.mesh('rampplate', rg, P.det, parent=ramp, frame=rf); qr = P.rest_quat(ramp)
for f, a in ((0, 180), (80, 0)): P.key('rampOut', ramp, f, rotation_quaternion=qr @ Quaternion((1, 0, 0), math.radians(-a)))
P.key('rampOut', ramp, 40, rotation_quaternion=qr @ Quaternion((1, 0, 0), math.radians(-90)))
P.hull_collider('col_ramp', [(x, y, z) for x in (-RW, RW) for y in (RY - .02, RY - RL) for z in (RZ_, RZ_ - .06)], parent=ramp, frame=rf)
for x in (-1.2, 0, 1.2): d.add(box(.14, .10, RZ_ - .06 - FL, zone=Z.grey, bevel=.01), T(x, RY, (RZ_ - .06 + FL) / 2)); d.add(cyl(.045, .05, 16, zone=Z.alu, bevel=.006), T(x, RY, RZ_ - .03) @ Ry(90)); d.add(cyl(.02, .20, 12, zone=Z.steel), T(x, RY, RZ_ - .03) @ Ry(90))
for s in (-1, 1): d.add(cyl(.05, .20, 18, zone=Z.white, bevel=.01), T(s * .60, RY, RZ_ - .03) @ Ry(90)); d.add(box(.10, .12, RZ_ - .06 - FL, zone=Z.grey, bevel=.01), T(s * .60, RY, (RZ_ - .06 + FL) / 2))      # rotary actuators
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
for i in range(12):
    for k, (z0, z1) in enumerate(((H0, 3.7), (3.7, TP))): P.hull_collider(f'col_u{i}{k}', [p for z in (z0, z1) for o in (0, .12) for p in ring_(z, 30 * i, 30 * i + 30, 3, R_(z) - o)])
P.hull_collider('col_ceil', [p for z in (TP, TP + .12) for p in ring_(z, 0, 345, 23, R_(z) - .06)])
for i, (za, zb) in enumerate(((TP, 5.81), (5.81, 7.40), (7.40, 8.52))): P.hull_collider(f'col_n{i}', [p for z in (za, zb) for p in ring_(z, 0, 345, 23)])
P.node('bottom', (0, 0, HL.Z_TOP - O), (0, 0, -1), 5); P.node('cargo', (0, 0, FL), (0, 0, 1), 4); P.node('winch', (0, 0, CE), (0, 0, -1), 3); P.node('crane', (0, HL.CR_Y, FL), (0, 0, 1), 2); P.node('floor1', (0, HL.FLOORS['Mid'][0], FL), (0, 0, 1), 2); P.node('floor2', (0, HL.FLOORS['Top'][0], FL), (0, 0, 1), 2)
P.bake_clips(0); finish(P)

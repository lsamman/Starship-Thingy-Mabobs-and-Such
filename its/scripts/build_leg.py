"""ITS landing leg: telescoping strut that lies on the black lower face of a leg fairing, with a wedge foot folded over
the skirt. Stock wheel-module layout (leg > wheelCollider, pistonbase > piston > foot, deployTgt) as in SHABTech's leg.
Authored deployed; frame 0 of legDeploy is stowed. Origin on the hull at the hinge, -Y outboard, +Z up."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
P = start('ITS_Leg'); N = 120
F_SWING, F_SLIDE, F_DONE = 60, 30, 100                    # pistons out by frame 100, before TsubSys = .85 hands over
TILT = math.radians(L.LEG_TILT); SL = math.radians(L.LEG_STOW)
U = Vector((0, -math.sin(TILT), -math.cos(TILT)))         # strut axis, deployed
SW = TILT + SL                                            # swing angle
HINGE = Vector((0, 0, 0))
SOLE = (L.LEG_SOLE - L.LEG_H[1]) * K
SUSP, RAD = .30, .42                                      # suspension travel, ankle height over the sole
WC = SOLE + RAD + SUSP
SLEN = -WC / math.cos(TILT); KNEE = U * SLEN
OUT_L = 3.62; IN_L = 3.50; NST = 3
STEP = (SLEN - IN_L) / NST
R1 = .33; RS = (.285, .24, .20)
print(f'strut {SLEN:.2f} step {STEP:.2f} knee y {KNEE.y:.2f} sole {SOLE:.3f}')
leg = P.empty('leg', None, P.model)
fU = lambda p: frame_axes(p, -U, x=Vector((1, 0, 0)))     # local +Z back up the strut
XA = Vector((1, 0, 0))

# ---------------- fixed: hinge brackets, the well in the fairing face, drag strut lugs
D = Vector((0, (6.92 - L.LEG_H[0]) * -K, (8.45 - L.LEG_H[1]) * K))     # drag strut pivot on the face
slope = frame_axes((0, 0, 0), Vector((0, -math.cos(SL), -math.sin(SL))), x=XA)   # +Z out of the face, +Y up it
if slope.to_3x3() @ Vector((0, 1, 0)) @ Vector((0, 0, 1)) < 0:
    slope = slope @ Rz(180)
b = Geo()
for s in (-1, 1):
    b.add(box(.10, .56, .40, zone=Z.black, bevel=.03), slope @ T(s * .40, .02, .06))
    b.add(cyl(.17, .06, 18, zone=Z.steel, bevel=.012), T(s * .46, 0, 0) @ Ry(90))
    b.add(box(.09, .30, .26, zone=Z.dark, bevel=.02), slope @ T(s * .24, D.z / math.cos(SL), .04))
b.add(tube([(-.50, 0, 0), (.50, 0, 0)], .085, 14, zone=Z.steel))
b.add(tube([tuple(D + Vector((-.30, 0, 0))), tuple(D + Vector((.30, 0, 0)))], .05, 12, zone=Z.steel))
P.mesh('bracket', b, P.det, parent=leg)

wc = P.empty('wheelCollider', T(*KNEE), leg); wc.muproperties.layer = 27

# ---------------- stage 1: outer tube with a faceted black cover on its outboard side
W = Vector((0, -math.cos(TILT), math.sin(TILT)))           # outboard, across the strut
g = Geo()
g.add(tube([tuple(U * .10), tuple(U * OUT_L)], R1, 24, zone=Z.dark))
for d, w, r in ((OUT_L - .16, .18, .045), (.35, .12, .03), (1.5, .07, .02), (2.6, .07, .02)):
    g.add(tube([tuple(U * d), tuple(U * (d + w))], R1 + r, 24, zone=Z.black))
g.add(tube([tuple(U * OUT_L), tuple(U * (OUT_L + .03))], R1 - .02, 20, zone=Z.rubber))
g.add(cyl(.26, .62, 20, zone=Z.black, bevel=.03), Ry(90))
g.add(box(.42, .40, .5, zone=Z.black, bevel=.05), frame_axes(U * .22, U, x=XA))
COL = OUT_L - .10                                           # drag strut collar
for s in (-1, 1):
    g.add(cyl(.10, .12, 14, zone=Z.black, bevel=.015), T(*(U * COL + XA * s * (R1 + .06))) @ Ry(90))
hf = T(0, 0, 0)
UNSWING = Matrix.Rotation(-SW, 4, 'X')                      # stowed -> deployed, about the hinge
pb = P.mesh('pistonbase', g, P.det, parent=leg, frame=hf)
P.key('legDeploy', pb, 0, rotation_quaternion=Quaternion((1, 0, 0), SW))
P.key('legDeploy', pb, F_SWING, rotation_quaternion=Quaternion()); P.key('legDeploy', pb, N, rotation_quaternion=Quaternion())

# ---------------- aeroshell: PICA-faced blister that follows the hull over the strut and foot; its nose cap stays on the ship
CUT = 12.15                                                  # real z where the moving shell starts
def prof(z):
    """Height over the hull and half-width of the blister (real metres)."""
    zs = np.array([5.03, 5.07, 5.18, 5.40, 5.9, 7.0, 8.2, 10.0, 12.0, 13.0, 13.9, 14.7, 15.2, 15.4])
    h = np.array([.04, .22, .56, .90, 1.12, 1.22, 1.12, 1.00, .92, .80, .52, .20, .05, .0])
    w = np.array([.95, 1.02, 1.12, 1.24, 1.36, 1.44, 1.42, 1.36, 1.28, 1.16, .92, .60, .34, .25])
    return float(H._pchip(z, zs, h)), float(H._pchip(z, zs, w))
US = np.array([-1.0, -.97, -.90, -.80, -.66, -.50, -.25, 0, .25, .50, .66, .80, .90, .97, 1.0])
LAT = lambda u: (1 - abs(u) ** 3.2) ** .62 if abs(u) < 1 else 0.0
def blister(zs, inner=0.0, flip=False):
    g = Geo(); rows = []
    for z in zs:
        h, w = prof(z); row = []
        for u in US:
            r0 = float(H.section_r(0, z)); az = math.degrees(u * (w - inner * .9) / r0)
            off = max(h * LAT(u) - inner, -.03) if h > inner else -.03
            p = H.point(az, max(z, 5.0), 0); n = (surf(az, max(z, 5.05), 0.0).to_3x3() @ V3((0, 0, 1)))
            q = V3((float(p[0]), float(p[1]), z)) + n * off
            row.append(len(g.v)); g.v.append(((q.x) * K, (q.y + L.LEG_H[0]) * K, (q.z - L.LEG_H[1]) * K))
        rows.append(row)
    zz0, zz1 = zs[0], zs[-1]
    for j, (a_, b_) in enumerate(zip(rows, rows[1:])):
        for k in range(len(US) - 1):
            uvq = [Z.pica.uv((US[kk] + 1) / 2, (zs[jj] - 5.0) / 10.5) for kk, jj in ((k, j), (k + 1, j), (k + 1, j + 1), (k, j + 1))]
            f = [a_[k], a_[k + 1], b_[k + 1], b_[k]]
            g.face(f[::-1] if flip else f, uvq[::-1] if flip else uvq)
    return g
V3 = Vector
ZS = [5.03, 5.07, 5.13, 5.22, 5.35, 5.6, 5.9, 6.3, 6.9, 7.5, 8.2, 9.0, 10.0, 11.0, CUT]
sh = Geo(); sh.add(blister(ZS), UNSWING)
li = Geo(); li.add(recolor(blister([5.3, 5.5, 5.8, 6.3, 6.9, 7.5, 8.2, 9.0, 10.0, 11.0, CUT], inner=.10, flip=True), Z.carbon), UNSWING)
P.mesh('aeroshell', sh, P.det, parent=pb, frame=hf, smooth_angle=50)
rb = Geo(); rb.add(li)
for z in (5.6, 7.2, 8.8, 10.4, 11.8):                         # frames tying the shell to the strut
    h, w = prof(z); rr = float(H.section_r(0, z)) + h * .55
    c_ = V3((0, (-rr + L.LEG_H[0]) * K, (z - L.LEG_H[1]) * K))
    if z > 7.6:
        rb.add(box(w * 2 * K * .74, .09, .06, zone=Z.alu, bevel=.012), UNSWING @ T(*c_))
P.mesh('shell_in', rb, P.det, parent=pb, frame=hf)
nose = blister([CUT + .04, 12.6, 13.0, 13.4, 13.9, 14.4, 14.8, 15.1, 15.3, 15.4])
P.mesh('nosecap', nose, P.det, parent=leg, smooth_angle=50)

# ---------------- stages 2 and 3
parent = pb; secs = []
for k, r in enumerate(RS):
    p0 = U * (STEP * (k + 1)); g = Geo()
    g.add(tube([tuple(p0 + U * .02), tuple(p0 + U * IN_L)], r, 22, zone=Z.grey if k == NST - 1 else Z.dark))
    g.add(tube([tuple(p0 + U * (IN_L - .14)), tuple(p0 + U * (IN_L + .02))], r + .035, 22, zone=Z.black))
    g.add(tube([tuple(p0 + U * (IN_L - .30)), tuple(p0 + U * (IN_L - .24))], r + .02, 22, zone=Z.dark))
    if k == NST - 1:                                        # ankle housing over the shock absorber
        g.add(lathe([(.22, .34), (.31, .26), (.33, -.10), (.33, -.16), (.27, -.18), (.18, -.18)][::-1], 24, zone=Z.black), T(*KNEE))
        g.add(bolts(12, .27, .018), T(*(KNEE + Vector((0, 0, .27)))))
    o = P.mesh(f'strut{k + 2}', g, P.det, parent=parent, frame=T(*p0))
    rest = o.location.copy(); st = rest - U * (STEP - .02)
    for f, l in ((0, st), (F_SLIDE, st), (F_DONE, rest), (N, rest)):
        P.key('legDeploy', o, f, location=l)
    secs.append(o); parent = o
P.empty('deployTgt', T(*KNEE), pb)

# ---------------- piston and foot
g = Geo(); g.add(tube([tuple(KNEE + Vector((0, 0, .05))), tuple(KNEE + Vector((0, 0, -.05)))], .16, 14, zone=Z.steel))
pi = P.mesh('piston', g, P.det, parent=pb, frame=T(*KNEE))
l1 = pi.location.copy(); l0 = U * (IN_L + .06)
for f, l, q in ((0, l0, Quaternion((1, 0, 0), -SW)), (F_SLIDE, l0, Quaternion((1, 0, 0), -SW)), (F_DONE, l1, Quaternion()), (N, l1, Quaternion())):
    P.key('legDeploy', pi, f, location=l, rotation_quaternion=q)
FC = KNEE + Vector((0, 0, -SUSP)); fT = T(*FC)
g = Geo()
# wedge shoe (SpaceX's Enceladus render): long toe outboard, short heel, faceted top rising to the ankle
def poly(y0, y1, w0, w1, wm, ym):                            # heel y0 (inboard +), toe y1 (outboard -), half-widths
    return [(-w0, y0), (w0, y0), (wm, ym), (w1, y1), (-w1, y1), (-wm, ym)]
rows = [([(x * .94, y * .97) for x, y in poly(.62, -1.30, .30, .18, .56, .06)], -RAD),
        (poly(.62, -1.30, .30, .18, .56, .06), -RAD + .05), (poly(.60, -1.27, .29, .17, .55, .06), -RAD + .16),
        (poly(.32, -.42, .20, .15, .30, .02), -.02), (poly(.24, -.30, .18, .14, .26, .0), .06)]
for r, z in rows:
    g.v += [(x, y, z) for x, y in r]
for j in range(len(rows) - 1):
    for k in range(6):
        k2 = (k + 1) % 6
        g.face([j * 6 + k2, j * 6 + k, (j + 1) * 6 + k, (j + 1) * 6 + k2][::-1], [Z.black.uv(k / 6, j / 5), Z.black.uv((k + 1) / 6, j / 5), Z.black.uv((k + 1) / 6, (j + 1) / 5), Z.black.uv(k / 6, (j + 1) / 5)][::-1])
for j, flip in ((0, True), (len(rows) - 1, False)):
    c = len(g.v); r, z = rows[j]; g.v.append((0, 0, z))
    for k in range(6):
        t = [c, j * 6 + k, j * 6 + (k + 1) % 6]
        g.face(t if not flip else t[::-1], [Z.rubber.uv(.5, .5), Z.rubber.uv(.2, .3), Z.rubber.uv(.3, .2)])
shoe = Geo(); shoe.add(g, fT)
import bmesh
def check(gm):                                               # outward winding, computed once from the volume's sign
    v = [Vector(p) for p in gm.v]; s = 0
    for f in gm.f:
        for a_, b_ in zip(f[1:], f[2:]):
            s += v[f[0]].dot(v[a_].cross(v[b_]))
    return s
if check(shoe) < 0:
    shoe.f = [f[::-1] for f in shoe.f]; shoe.uv = [u[::-1] for u in shoe.uv]
for y in np.arange(-1.05, .55, .27):                           # sole cleats
    w = .46 if y > -.1 else .46 + (y + .1) * .28
    shoe.add(box(2 * w * .9, .10, .05, zone=Z.rubber, bevel=.012), fT @ T(0, y, -RAD - .012))
shoe.add(cyl(.17, .46, 18, zone=Z.steel, bevel=.02), fT @ Ry(90))                  # ankle pin
for s in (-1, 1):
    shoe.add(box(.09, .34, .36, zone=Z.dark, bevel=.03), fT @ T(s * .20, 0, -.04))
    shoe.add(tube([tuple(fT @ Vector((s * .30, -.35, -.12))), tuple(fT @ Vector((s * .20, -1.10, -RAD + .16)))], .035, 8, zone=Z.dark))
shoe.add(tube([tuple(FC), tuple(FC + Vector((0, 0, SUSP + .16)))], .13, 16, zone=Z.alu))
fo = P.mesh('foot', shoe, P.det, parent=pi, frame=fT, smooth_angle=30)
l1 = fo.location.copy(); l0 = Vector((0, 0, -.05))
QF = Quaternion((1, 0, 0), math.radians(90 - 8))            # stowed: toe down the hull, sole outboard under the shell
for f, l, q in ((0, l0, QF), (F_SLIDE, l0, QF), (F_DONE - 10, l1, Quaternion()), (N, l1, Quaternion())):
    P.key('legDeploy', fo, f, location=l, rotation_quaternion=q)

# ---------------- drag strut: two nested tubes from the face to the collar, aimed frame by frame
def collar(deg):
    return Quaternion((1, 0, 0), math.radians(deg)) @ (U * COL)
keys = []
for f in (0, 8, 16, 24, 32, 40, 48, 54, F_SWING, N):
    t = min(1, f / F_SWING); deg = math.degrees(SW) * (1 - t * t * (3 - 2 * t))
    c = collar(deg); keys.append((f, c, (c - D).normalized(), (c - D).length))
print('drag strut', ['%.2f' % k[3] for k in keys])
BL = min(k[3] for k in keys) - .16
for s in (-1, 1):
    ga, gb = Geo(), Geo(); off = s * .36
    ga.add(tube([(0, 0, .05), (0, 0, BL)], .13, 14, zone=Z.black)); ga.add(tube([(0, 0, BL - .10), (0, 0, BL + .01)], .15, 14, zone=Z.dark)); ga.add(cyl(.12, .14, 14, zone=Z.dark, bevel=.015), Ry(90))
    gb.add(tube([(0, 0, .05), (0, 0, max(k[3] for k in keys) - BL + .25)], .10, 12, zone=Z.steel)); gb.add(cyl(.11, .14, 14, zone=Z.black, bevel=.015), Ry(90))
    fA = frame_axes(D + XA * s * .30, keys[-1][2], x=XA); fB = frame_axes(keys[-1][1] + XA * off, -keys[-1][2], x=XA)
    oa = P.mesh('drag%d' % (s > 0), Geo().add(ga, fA), P.det, parent=leg, frame=fA)
    ob = P.mesh('rod%d' % (s > 0), Geo().add(gb, fB), P.det, parent=leg, frame=fB)
    for f, c, d, ln in keys:
        dd = ((c + XA * off) - (D + XA * s * .30)).normalized()
        P.key('legDeploy', oa, f, rotation_quaternion=frame_axes((0, 0, 0), dd, x=XA).to_quaternion(), location=D + XA * s * .30)
        P.key('legDeploy', ob, f, rotation_quaternion=frame_axes((0, 0, 0), -dd, x=XA).to_quaternion(), location=c + XA * off)

# ---------------- colliders
def cap(name, d0, d1, r, parent):
    o = P.empty(name, frame_axes(U * ((d0 + d1) / 2), -U), parent); m = o.muproperties
    m.collider = 'MU_COL_CAPSULE'; m.isTrigger = False; m.radius = r; m.height = d1 - d0; m.direction = 'MU_Z'; m.center = (0, 0, 0); m.layer = 26
cap('pistonbaseCollider', 0, OUT_L, .3, pb); cap('col_strut', STEP * NST + .2, STEP * NST + IN_L, .22, secs[-1])
o = P.empty('piston_collider', T(*KNEE), pi); m = o.muproperties
m.collider = 'MU_COL_CAPSULE'; m.isTrigger = False; m.radius = .2; m.height = SUSP + .3; m.direction = 'MU_Z'; m.center = (0, 0, -SUSP / 2); m.layer = 26
P.hull_collider('col_bracket', [tuple(slope @ Vector((x, y, z))) for x in (-.5, .5) for y in (.25, -.5) for z in (-.1, .2)], parent=leg)
P.node('mount', (0, 0, 0), (0, 1, 0), 2)
P.bake_clips(0)
finish(P)

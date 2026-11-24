"""Ship quick disconnect arm for SLE's launch tower: truss, propellant lines, a hooded plate that meets SEP's QD plate, and a claw
that holds the booster. Origin at its node on the tower column; the plate's middle is at z 0. Frame 0 is connected."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import tower_layout as TL
import numpy as np
P = start('STMS_QDArm'); V = Vector
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arm_common.py')).read())
TX = TL.SHIP[0] + TL.HULL + .03 - TL.QD[0]; TY = TL.SHIP[1] - TL.QD[1]; H = V((-.60, .85, 0)); W, Z0, Z1 = 1.5, -.95, 1.25
E_ = V((TX + 1.9, TY, 0)); u = (E_ - H).normalized(); LEN = (E_ - H).length; A = Matrix((u, V((-u.y, u.x, 0)), V((0, 0, 1)))).transposed().to_4x4(); A.translation = H
bracket(-90, H, Z0 - .1, Z1 + .1); arm = P.empty('arm', A, P.model); g = Geo(); x0, x1 = .45, LEN + .1
truss(g, x0, x1, W, Z0, Z1, .10, 10); g.add(box(x1 - x0, W - .2, .05, zone=Z.deck, center=((x0 + x1) / 2, 0, Z0 - .02)))
for y, z, r, zn in ((-.42, -.35, .17, Z.white), (.05, -.38, .17, Z.white), (.45, -.45, .10, Z.alu), (-.45, .35, .09, Z.alu), (-.2, .4, .06, Z.copper), (.35, .35, .12, Z.dark)):
    g.add(tube([(x0 - .2, y, z), (x1 + .1, y, z)], r, 14, zone=zn))
    for x in np.linspace(x0 + .5, x1 - .3, 7): g.add(tube([(float(x) - .05, y, z), (float(x) + .05, y, z)], r + .03, 14, zone=Z.grey)); g.add(box(.06, .05, .5, zone=Z.dark, center=(float(x), y, z - .30)))
for s in (-1, 1):                                            # walkway rail on top
    g.add(tube([(x0, s * W / 2, Z1 + .65), (x1, s * W / 2, Z1 + .65)], .025, 8, zone=Z.white)); [g.add(tube([(float(x), s * W / 2, Z1), (float(x), s * W / 2, Z1 + .65)], .02, 6, zone=Z.white)) for x in np.linspace(x0, x1, 9)]
g.add(box(x1 - x0, W - .1, .04, zone=Z.deck, center=((x0 + x1) / 2, 0, Z1 + .12)))
for p_ in ((x0 + 1.2, -.75), (x0 + 5, .75)): g.add(box(.9, .28, .7, zone=Z.white, bevel=.03, center=(p_[0], p_[1], Z1 - .5)))
P.mesh('truss', Geo().add(g, A), P.det, parent=arm, frame=A)
PF = T(TX, TY, 0); plate = P.empty('plate', PF, arm); r = Geo()
r.add(box(.16, 1.06, 1.16, zone=Z.grey, bevel=.03, center=(.10, 0, 0))); r.add(box(.06, .90, 1.0, zone=Z.alu, bevel=.015, center=(.02, 0, 0)))
for y, z, rr in ((-.24, -.2, .15), (.24, -.2, .15), (-.26, .28, .08), (0, .30, .07), (.26, .28, .08)): r.add(cyl(rr, .10, 20, zone=Z.steel, bevel=.012), T(.0, y, z) @ Ry(90)); r.add(cyl(rr * .7, .06, 16, zone=Z.rubber), T(-.03, y, z) @ Ry(90)); r.add(tube([(.18, y, z), (.7, y, z * .9), (1.5, y * 1.2, z * .6 - .1), (2.4, y * 1.2, z * .6 - .1)], rr * .8, 12, zone=Z.alu))
for s in (-1, 1): r.add(box(1.5, .06, 1.5, zone=Z.white, bevel=.02, center=(.95, s * .72, .05))); r.add(tube([(.2, s * .5, -.5), (2.5, s * .5, -.6)], .07, 10, zone=Z.steel)); r.add(tube([(.2, s * .5, .5), (2.5, s * .5, .55)], .07, 10, zone=Z.steel))
r.add(box(1.5, 1.5, .06, zone=Z.white, bevel=.02, center=(.95, 0, .80))); r.add(box(.9, 1.2, .9, zone=Z.dark, bevel=.04, center=(1.7, 0, 0))); r.add(box(.06, 1.5, .12, zone=Z.stripe, center=(.20, 0, .80)))
P.mesh('platemesh', Geo().add(r, PF), P.det, parent=plate, frame=PF)
# ---------------- booster claw on a mast under the arm's end: a crosshead that slides back, two jaws with pads
CZ = TL.CLAW_Z - TL.QD_Z; m_ = Geo(); mx0, mx1 = LEN - 2.3, LEN - .3
for x in (mx0, mx1):
    for y in (-.6, .6): m_.add(tube([(x, y, Z0), (x, y, CZ - .55)], .09, 8, zone=Z.dark))
zs_ = np.linspace(Z0, CZ - .5, 5)
for a_, b_ in zip(zs_, zs_[1:]):
    for y in (-.6, .6): m_.add(tube([(mx0, y, float(a_)), (mx1, y, float(b_))], .055, 6, zone=Z.dark)); m_.add(tube([(mx0, y, float(b_)), (mx1, y, float(b_))], .055, 6, zone=Z.dark))
    for x in (mx0, mx1): m_.add(tube([(x, -.6, float(a_)), (x, .6, float(b_))], .055, 6, zone=Z.dark)); m_.add(tube([(x, -.6, float(b_)), (x, .6, float(b_))], .055, 6, zone=Z.dark))
for y in (-.45, .45): m_.add(box(mx1 - mx0 + .4, .16, .22, zone=Z.alu, bevel=.02, center=((mx0 + mx1) / 2, y, CZ - .42))); m_.add(tube([(mx0 - 4.2, y, Z0), (mx0, y, CZ * .62)], .09, 8, zone=Z.dark))
m_.add(box(.7, .5, .5, zone=Z.white, bevel=.03, center=(mx0 + .5, 0, CZ - .25)))
P.mesh('mast', Geo().add(m_, A), P.det, parent=arm, frame=A)
CF = T(TX, TY, CZ); claw = P.empty('claw', CF, arm); AX = V((TL.SHIP[0] - TL.QD[0] - TX, 0, 0)); c = Geo()
c.add(box(.75, 1.9, .62, zone=Z.grey, bevel=.05, center=(1.28, 0, 0))); c.add(box(2.4, .9, .42, zone=Z.dark, bevel=.03, center=(2.75, 0, -.02)))
for s in (-1, 1): c.add(cyl(.19, .80, 18, zone=Z.alu, bevel=.02), T(1.0, s * .75, 0)); c.add(tube([(1.5, s * .2, .12), (2.9, s * .2, .12)], .08, 10, zone=Z.steel)); c.add(box(.3, .3, .72, zone=Z.white, bevel=.03, center=(1.55, s * .62, .0)))
c.add(box(.06, 1.7, .12, zone=Z.stripe, center=(.90, 0, .12))); P.mesh('crosshead', Geo().add(c, CF), P.det, parent=claw, frame=CF)
pol = lambda r, a, z=0: V((AX.x + r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), z)); jaws = []
for s in (-1, 1):
    JF = CF @ T(1.0, s * .75, 0); jw = P.empty('jaw%d' % (s > 0), JF, claw); g_ = Geo(); path = [V((1.0, s * .75, 0)), pol(3.36, s * 20), pol(3.22, s * 28), pol(3.16, s * 36), pol(3.14, s * 44), pol(3.14, s * 51)]
    for z in (-.20, .20): g_.add(tube([tuple(p + V((0, 0, z))) for p in path], .11, 8, zone=Z.dark))
    for p in path[1:]: g_.add(tube([tuple(p + V((0, 0, -.2))), tuple(p + V((0, 0, .2)))], .07, 8, zone=Z.dark))
    g_.add(cyl(.16, .62, 16, zone=Z.steel, bevel=.015), T(1.0, s * .75, 0))
    for a in (33, 48): g_.add(box(.20, .46, .56, zone=Z.grey, bevel=.03), T(*pol(3.0, s * a)) @ Rz(s * a)); g_.add(box(.08, .42, .52, zone=Z.rubber, bevel=.02), T(*pol(2.885, s * a)) @ Rz(s * a))
    P.mesh('jawmesh%d' % (s > 0), Geo().add(g_, CF), P.det, parent=jw, frame=JF); jaws.append((s, jw))
# ---------------- retraction: jaws snap open, plate and claw pull back together, then the swing
CL = 'qdArm'; N_ = 104; back = A.to_3x3().inverted() @ V((1, 0, 0))
for o, d in ((plate, 1.2), (claw, 1.75)):
    l0 = o.location.copy()
    for f, l in ((0, l0), (8, l0), (28, l0 + back * d), (N_, l0 + back * d)): P.key(CL, o, f, location=l)
for s, jw in jaws:
    q = P.rest_quat(jw)
    for f, a in ((0, 0), (16, -72 * s), (N_, -72 * s)): P.key(CL, jw, f, rotation_quaternion=q @ Quaternion((0, 0, 1), math.radians(a)))
q = P.rest_quat(arm); yawA = math.atan2(u.y, u.x) % (2 * math.pi); sw = math.radians(68) - yawA
for f, a in ((0, 0), (24, 0), (N_, sw)): P.key(CL, arm, f, rotation_quaternion=q @ Quaternion((0, 0, 1), a))
P.clips['qdArmStage'] = {k: list(v) for k, v in P.clips[CL].items()}      # StagedAnimation plays its own copy
def bx(nm, M, c, s, par): P.hull_collider(nm, [tuple(M @ V((c[0] + i * s[0] / 2, c[1] + j * s[1] / 2, c[2] + k * s[2] / 2))) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)], parent=par)
bx('col_arm', A, ((x0 + x1) / 2, 0, (Z0 + Z1) / 2), (x1 - x0, W, Z1 - Z0 + .2), arm); bx('col_plate', PF, (1.2, 0, 0), (1.9, 1.4, 1.4), plate); bx('col_mast', A, ((mx0 + mx1) / 2, 0, (Z0 + CZ) / 2), (mx1 - mx0, 1.3, Z0 - CZ), arm)
print('qd arm: length %.2f, swing %.0f deg' % (LEN, math.degrees(sw)))
P.node('mount', (0, 0, 0), (0, -1, 0), 2); P.bake_clips(0); finish(P)

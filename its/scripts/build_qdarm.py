"""Ship quick disconnect arm for SLE's launch tower: truss, propellant lines, a hooded plate that meets SEP's QD plate.
Origin at its node on the tower column; the plate's middle is at z 0. Frame 0 is connected."""
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
CL = 'qdArm'; N_ = 220; l0 = plate.location.copy(); d_ = A.to_3x3().inverted() @ V((1, 0, 0))
for f, l in ((0, l0), (40, l0 + d_ * 1.2), (N_, l0 + d_ * 1.2)): P.key(CL, plate, f, location=l)
q = P.rest_quat(arm); yawA = math.atan2(u.y, u.x) % (2 * math.pi); sw = math.radians(80) - yawA
for f, a in ((0, 0), (40, 0), (N_, sw)): P.key(CL, arm, f, rotation_quaternion=q @ Quaternion((0, 0, 1), a))
def bx(nm, M, c, s, par): P.hull_collider(nm, [tuple(M @ V((c[0] + i * s[0] / 2, c[1] + j * s[1] / 2, c[2] + k * s[2] / 2))) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)], parent=par)
bx('col_arm', A, ((x0 + x1) / 2, 0, (Z0 + Z1) / 2), (x1 - x0, W, Z1 - Z0 + .2), arm); bx('col_plate', PF, (1.2, 0, 0), (1.9, 1.4, 1.4), plate)
print('qd arm: length %.2f, swing %.0f deg' % (LEN, math.degrees(sw)))
P.node('mount', (0, 0, 0), (0, -1, 0), 2); P.bake_clips(0); finish(P)

"""Crew access arm for SLE's launch tower: truss walkway, white room meeting the noses' EVA hatch. Origin at its node on the
tower column, floor at z 0 (the hatch sill). Frame 0 is out to the ship; crewArm draws the room in, then swings the arm away."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import tower_layout as TL
import numpy as np
P = start('STMS_CrewArm'); V = Vector; QD = False
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arm_common.py')).read())
TX = TL.SHIP[0] + TL.HULL - .07 - TL.CREW[0]; TY = TL.SHIP[1] - TL.CREW[1]           # hatch, from the node
H = V((-.60, -.85, 0)); ROOM = 2.1; W, HT = 1.36, 1.72                           # hinge; white room length; walkway section
E_ = V((TX + ROOM + .25, TY, 0)); u = (E_ - H).normalized(); LEN = (E_ - H).length; yawA = math.atan2(u.y, u.x)
A = Matrix((u, V((-u.y, u.x, 0)), V((0, 0, 1)))).transposed().to_4x4(); A.translation = H      # arm frame: x along, y left, z up
bracket(90, H, -1.0, HT + .5)
arm = P.empty('arm', A, P.model); g = Geo(); gl = Geo(); lp = Geo()
x0, x1 = .55, LEN + .15
truss(g, x0, x1, W, 0, HT, .07, 9)
g.add(box(x1 - x0, W - .1, .05, zone=Z.deck, center=((x0 + x1) / 2, 0, -.03))); g.add(box(x1 - x0, W + .04, .05, zone=Z.white, center=((x0 + x1) / 2, 0, HT + .05)))
for s in (-1, 1):
    g.add(box(x1 - x0, .03, .52, zone=Z.white, center=((x0 + x1) / 2, s * (W / 2 - .05), .28))); g.add(box(x1 - x0, .03, .34, zone=Z.white, center=((x0 + x1) / 2, s * (W / 2 - .05), HT - .18)))
    gl.add(quad_patch(x1 - x0, HT - .90, Zone(600, 600, 60, 60, atlas=1024)), T((x0 + x1) / 2, s * (W / 2 - .05), .54 + (HT - .88) / 2) @ Rx(90 if s < 0 else -90))
    for x in np.linspace(x0 + .1, x1 - .1, 10): g.add(box(.05, .05, HT - .9, zone=Z.dark, center=(float(x), s * (W / 2 - .05), .54 + (HT - .9) / 2)))
    g.add(tube([(x0, s * (W / 2 - .12), .62), (x1, s * (W / 2 - .12), .62)], .02, 8, zone=Z.alu))
lp.add(box(x1 - x0 - .6, .10, .03, zone=Z.lamp, center=((x0 + x1) / 2, 0, HT - .01)))
for x in np.linspace(x0 + .6, x1 - .6, 5): g.add(box(.5, .3, .22, zone=Z.grey, bevel=.02, center=(float(x), 0, -.16)))
for y in (-.28, .28): g.add(tube([(x0, y, -.20), (x1, y, -.20)], .05, 8, zone=Z.alu))
wk = Geo().add(g, A); P.mesh('walkway', wk, P.det, parent=arm, frame=A); P.mesh('walkglass', Geo().add(gl, A), P.material('its_glass', shader='KSP/Emissive/Bumped Specular', spec=(1, 1, 1), shininess=.8, emissive='its_glass_emit'), parent=arm, frame=A)
LM = P.material('its_det', shader='KSP/Emissive/Bumped Specular', spec=(.8, .8, .8), shininess=.4, emissive='hls_lamp_emit', name='hls_lamp'); P.mesh('armlamps', Geo().add(lp, A), LM, parent=arm, frame=A)
for x in (2.5, 6, 9.5): add_spot(P, 'armLight', A @ V((x, 0, HT - .1)), (0, 0, -1), parent=arm, power=90, angle=120, reach=4)
# ---------------- white room, square to the ship
RF = T(TX, TY, 0); room = P.empty('room', RF, arm); r = Geo(); RW, RH = 1.75, 1.9; a0, a1 = .42, .42 + ROOM                # x from the hull toward the tower
xm = (a0 + a1) / 2
r.add(box(a1 - a0, RW, .06, zone=Z.deck, center=(xm, 0, -.03))); r.add(box(a1 - a0, RW + .06, .08, zone=Z.white, bevel=.02, center=(xm, 0, RH)))
for s in (-1, 1): r.add(box(a1 - a0, .06, RH, zone=Z.white, bevel=.01, center=(xm, s * RW / 2, RH / 2))); r.add(box(.5, .02, .42, zone=Z.black, bevel=.02, center=(xm, s * (RW / 2 + .03), 1.15))); r.add(box(.06, .42, RH, zone=Z.white, center=(a0 + .03, s * (RW / 2 - .21), RH / 2)))
for s in (-1, 1): r.add(box(.05, .18, RH, zone=Z.white, center=(a1 - .03, s * (RW / 2 - .09), RH / 2)))
r.add(box(.06, RW, RH - 1.35, zone=Z.white, center=(a0 + .03, 0, (RH + 1.35) / 2)))
for k in range(6):                                           # bellows to the hull, shaped to it
    x = .04 + k * .075; w = .46 + (.03 if k % 2 else 0)
    ring_ = [(x - (0 if abs(y) < .01 else .03 * (y / w) ** 2), y, z) for y, z in ((-w, -.04), (-w, 1.30), (w, 1.30), (w, -.04))]
    for a, b in zip(ring_, ring_[1:] + ring_[:1]): r.add(tube([a, b], .05, 8, zone=Z.rubber))
for s in (-1, 1): r.add(box(.46, .02, 1.34, zone=Z.rubber, center=(.22, s * .47, .64)))
r.add(box(.46, .96, .02, zone=Z.rubber, center=(.22, 0, 1.31))); r.add(box(.46, .92, .04, zone=Z.deck, center=(.22, 0, -.03))); r.add(box(.10, .9, .03, zone=Z.stripe, center=(.02, 0, -.01)))
rl = Geo(); rl.add(box(1.2, .12, .03, zone=Z.lamp, center=(xm, 0, RH - .055)))
P.mesh('roommesh', Geo().add(r, RF), P.det, parent=room, frame=RF); P.mesh('roomlamp', Geo().add(rl, RF), LM, parent=room, frame=RF); add_spot(P, 'armLight', RF @ V((xm, 0, RH - .1)), (0, 0, -1), parent=room, power=120, angle=130, reach=4)
CL = 'crewArm'; N_ = 240; l0 = room.location.copy(); d_ = A.to_3x3().inverted() @ V((1.0, 0, 0)); d_.z = 0
for f, l in ((0, l0), (50, l0 + d_ * 1.05), (N_, l0 + d_ * 1.05)): P.key(CL, room, f, location=l)
q = P.rest_quat(arm); sw = math.radians(280) - yawA % (2 * math.pi)
for f, a in ((0, 0), (50, 0), (N_, sw)): P.key(CL, arm, f, rotation_quaternion=q @ Quaternion((0, 0, 1), a))
def bx(nm, M, c, s, par): P.hull_collider(nm, [tuple(M @ V((c[0] + i * s[0] / 2, c[1] + j * s[1] / 2, c[2] + k * s[2] / 2))) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)], parent=par)
mx = (x0 + x1) / 2; L2 = x1 - x0
bx('col_floor', A, (mx, 0, -.05), (L2, W, .1), arm); [bx('col_wall%d' % (s > 0), A, (mx, s * (W / 2 - .04), HT / 2), (L2, .06, HT), arm) for s in (-1, 1)]; bx('col_top', A, (mx, 0, HT + .05), (L2, W, .06), arm)
bx('col_rfloor', RF, (xm - .2, 0, -.05), (a1 - a0 + .4, RW, .1), room); [bx('col_rwall%d' % (s > 0), RF, (xm, s * RW / 2, RH / 2), (a1 - a0, .06, RH), room) for s in (-1, 1)]
print('crew arm: length %.2f, swing %.0f deg' % (LEN, math.degrees(sw)))
P.node('mount', (0, 0, 0), (0, 1, 0), 2); P.bake_clips(0); finish(P)

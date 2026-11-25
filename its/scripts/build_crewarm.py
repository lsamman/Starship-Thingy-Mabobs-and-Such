"""Crew access arm in the manner of the ship quick disconnect arm: a tubular dog-leg round the other side of the tower, a
walkway along it, and a white room at the noses' EVA hatch. Attaches radially to the rear column, square to the tower's
face at azimuth -37; frame: +x out of the column, the walkway floor at z 0 (the hatch sill)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import tower_layout as TL
import numpy as np
P = start('STMS_CrewArm'); V = Vector
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arm_common.py')).read())
ya = math.radians(TL.FACE_AZ); R_ = Matrix.Rotation(-ya, 3, 'Z'); O_ = V((*TL.CREW, 0)); rel = lambda x, y, z=0: R_ @ (V((x, y, z)) - O_)
N = V((1, 0, 0)); H = rel(6.9, -.5); E = rel(4.4, -9.2); TIP = rel(TL.SHIP[0] + TL.HULL - .10, TL.SHIP[1]); away = R_ @ V((1, 0, 0)); ROOM = 2.2
END = TIP + away * (ROOM + .45); d2 = END - E; d2.z = 0; L2 = d2.length; u2 = d2.normalized(); u1 = (E - H).normalized(); um = (u1 + u2).normalized(); MID = E + u2 * (L2 * .45)
hinge(N, H, (-2.0, .8), 1.1); arm = P.empty('arm', T(*H), P.model); HF = T(*H); g = Geo(); W = 1.5
S0 = section(H + u1 * .35, u1, 1.1, -1.9, 1.7); S1 = section(E, um, 2.1, -2.0, 1.95); S2 = section(MID, u2, 1.75, -1.0, 1.95); S3 = section(END, u2, W + .1, -.35, 1.95)
space_truss(g, S0, S1, 5, .13); space_truss(g, S1, S2, 6, .13); space_truss(g, S2, S3, 6, .08, .7); g.add(tube([(H.x, H.y, -1.9), (H.x, H.y, 1.8)], .2, 14, zone=Z.dark))
deck(g, H + u1 * .5, E, 1.0, -.03, rail=.75); F2 = deck(g, E - u2 * .5, END, 1.25, -.03); gl = Geo(); lp = Geo()
for s in (-1, 1):                                            # enclosed walkway along the outer leg: white below, glass band, white above
    for z0, z1, zn in ((.0, .55, Z.white), (1.45, 1.80, Z.white)): g.add(box(L2, .03, z1 - z0, zone=zn), F2 @ T(0, s * .64, (z0 + z1) / 2 + .03))
    gl.add(quad_patch(L2, .90, Zone(600, 600, 60, 60, atlas=1024)), F2 @ T(0, s * .64, 1.03) @ Rx(90 if s < 0 else -90))
    for x in np.linspace(-L2 / 2, L2 / 2, 12): g.add(box(.05, .05, .9, zone=Z.dark), F2 @ T(float(x), s * .64, 1.03))
    g.add(tube([tuple(F2 @ V((-L2 / 2, s * .54, .72))), tuple(F2 @ V((L2 / 2, s * .54, .72)))], .02, 6, zone=Z.alu))
g.add(box(L2, 1.36, .05, zone=Z.white), F2 @ T(0, 0, 1.85)); lp.add(box(L2 - 1, .10, .03, zone=Z.lamp), F2 @ T(0, 0, 1.81))
for k in range(5): g.add(box(.6, .5, .30, zone=Z.white, bevel=.03), F2 @ T(-L2 / 2 + 2 + k * 3.6, 0, 2.02)); add_spot(P, 'armLight', F2 @ V((-L2 / 2 + 2 + k * 3.6, 0, 1.75)), (0, 0, -1), parent=arm, power=90, angle=120, reach=4)
for y in (-.4, .4): g.add(tube([tuple(F2 @ V((-L2 / 2, y, -.16))), tuple(F2 @ V((L2 / 2, y, -.16)))], .06, 8, zone=Z.alu))
P.mesh('truss', g, P.det, parent=arm, frame=HF)
P.mesh('walkglass', gl, P.material('its_glass', shader='KSP/Emissive/Bumped Specular', spec=(1, 1, 1), shininess=.8, emissive='its_glass_emit'), parent=arm, frame=HF)
LM = P.material('its_det', shader='KSP/Emissive/Bumped Specular', spec=(.12, .12, .12), shininess=.4, emissive='hls_lamp_emit', name='hls_lamp'); P.mesh('armlamps', lp, LM, parent=arm, frame=HF)
# ---------------- white room, square to the ship: x away from it
RF = Matrix.Translation(TIP) @ Matrix.Rotation(math.atan2(away.y, away.x), 4, 'Z'); room = P.empty('room', RF, arm); r = Geo(); RW, RH = 1.9, 2.0; a0, a1 = .42, .42 + ROOM; xm = (a0 + a1) / 2
r.add(box(ROOM, RW, .06, zone=Z.deck, center=(xm, 0, -.03))); r.add(box(ROOM, RW + .06, .08, zone=Z.white, bevel=.02, center=(xm, 0, RH)))
for s in (-1, 1): r.add(box(ROOM, .06, RH, zone=Z.white, bevel=.01, center=(xm, s * RW / 2, RH / 2))); r.add(box(.6, .02, .45, zone=Z.black, bevel=.02, center=(xm, s * (RW / 2 + .03), 1.2))); r.add(box(.06, .48, RH, zone=Z.white, center=(a0 + .03, s * (RW / 2 - .24), RH / 2)))
r.add(box(.06, RW, RH - 1.35, zone=Z.white, center=(a0 + .03, 0, (RH + 1.35) / 2)))
bl = Geo(); fl = Geo(); dl = [Geo(), Geo()]
for k in range(6):
    w = .46 + (.03 if k % 2 else 0); x = .04 + k * .075; rg = [(x, y, z) for y, z in ((-w, -.04), (-w, 1.30), (w, 1.30), (w, -.04))]
    for a, b in zip(rg, rg[1:] + rg[:1]): bl.add(tube([a, b], .05, 8, zone=Z.rubber))
for s in (-1, 1): bl.add(box(.46, .02, 1.34, zone=Z.rubber, center=(.22, s * .47, .64)))
bl.add(box(.46, .96, .02, zone=Z.rubber, center=(.22, 0, 1.31))); fl.add(box(.46, .84, .03, zone=Z.deck, center=(.22, 0, -.03))); fl.add(box(.10, .82, .03, zone=Z.stripe, center=(.02, 0, -.02)))
for k, sg in enumerate((-1, 1)): dl[k].add(box(.035, .47, 1.30, zone=Z.white, bevel=.008, center=(a0 + .085, sg * .735, .68))); dl[k].add(box(.04, .26, .34, zone=Z.black, bevel=.01, center=(a0 + .085, sg * .735, .98))); dl[k].add(box(.03, .03, .30, zone=Z.alu, bevel=.006, center=(a0 + .115, sg * .56, .62)))      # two leaves, parked behind the jambs
r.add(box(2.0, 1.1, .04, zone=Z.deck, center=(a1 + .5, 0, -.06)));  rl = Geo(); rl.add(box(1.2, .12, .03, zone=Z.lamp, center=(xm, 0, RH - .055)))
P.mesh('roommesh', Geo().add(r, RF), P.det, parent=room, frame=RF); P.mesh('roomlamp', Geo().add(rl, RF), LM, parent=room, frame=RF); add_spot(P, 'armLight', RF @ V((xm, 0, RH - .1)), (0, 0, -1), parent=room, power=120, angle=130, reach=4)
# ---------------- letting go, in stages: gangway in, bellows back, doors shut, room back, arm away. Frame 0 is connected.
BF = RF @ T(a0, 0, 0); bel = P.empty('bellows', BF, room); P.mesh('bellowsmesh', Geo().add(bl, RF), P.det, parent=bel, frame=BF); gang = P.empty('gangway', RF, room); P.mesh('gangmesh', Geo().add(fl, RF), P.det, parent=gang, frame=RF)
CL = 'crewArm'; NF = 300; k0 = gang.location.copy()
for f, x in ((0, 0), (6, 0), (30, .46), (NF, .46)): P.key(CL, gang, f, location=k0 + V((x, 0, 0)))
for f, x in ((0, 1), (16, 1), (46, .24), (NF, .24)): P.key(CL, bel, f, scale=(x, 1, 1))
for k, sg in enumerate((-1, 1)):
    lf = P.empty('leaf%d' % k, RF, room); P.mesh('leafmesh%d' % k, Geo().add(dl[k], RF), P.det, parent=lf, frame=RF); q0 = lf.location.copy()
    for f, y in ((0, 0), (34, 0), (72, 1), (NF, 1)): P.key(CL, lf, f, location=q0 + V((0, -sg * .495 * y, 0)))
l0 = room.location.copy(); q = P.rest_quat(arm)
for f, l in ((0, l0), (62, l0), (112, l0 + away * 1.2), (NF, l0 + away * 1.2)): P.key(CL, room, f, location=l)
for f, a in ((0, 0), (104, 0), (NF, 92)): P.key(CL, arm, f, rotation_quaternion=q @ Quaternion((0, 0, 1), math.radians(a)))
P.clips['crewArmStage'] = {k: list(v) for k, v in P.clips[CL].items()}         # StagedAnimation plays its own copy
seg_collider('col_low0', [p for p in section(H + u1 * .5, u1, 1.0, -.1, -.02)], [p for p in section(E, um, 1.2, -.1, -.02)], arm); seg_collider('col_low1', section(E, u2, 1.2, -.1, -.02), section(END, u2, 1.25, -.1, -.02), arm)
for s in (-1, 1): k_ = V((-u2.y, u2.x, 0)) * s * .64; seg_collider('col_wall%d' % (s > 0), section(E + u2 * 1.0 + k_, u2, .06, 0, 1.8), section(END + k_, u2, .06, 0, 1.8), arm)
def bx(nm, c, s): P.hull_collider(nm, [tuple(RF @ V((c[0] + i * s[0] / 2, c[1] + j * s[1] / 2, c[2] + k * s[2] / 2))) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)], parent=room)
bx('col_rfloor', (xm, 0, -.05), (ROOM + .9, RW, .1)); [bx('col_rwall%d' % (s > 0), (xm, s * RW / 2, RH / 2), (ROOM, .06, RH)) for s in (-1, 1)]
print('crew arm: legs %.1f + %.1f m' % ((E - H).length, L2))
P.bake_clips(0); finish(P)

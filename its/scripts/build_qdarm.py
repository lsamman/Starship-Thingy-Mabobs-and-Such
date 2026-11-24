"""Ship quick disconnect arm after the real one (2022-25 photographs): a dog-leg of heavy black tube from the rear column, up to
a box platform full of pipework, and a boom on top with the X-shaped plate. It reaches round the chopstick carriage. Origin is
SLE's free node; the frame is the tower's. Frame 0 is connected."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import tower_layout as TL
import numpy as np
P = start('STMS_QDArm'); V = Vector
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arm_common.py')).read())
O_ = V(TL.NODE); N = V((TL.NODE_N[0], TL.NODE_N[1], 0)).normalized(); rel = lambda x, y, z=0: V((x, y, z)) - V((O_.x, O_.y, 0))
H = rel(7.0, 1.6); E = rel(4.2, 9.9); PZ = TL.QD_Z - O_.z                    # hinge, elbow, plate height
TIP = rel(TL.SHIP[0] + TL.HULL + .03, TL.SHIP[1]); END = TIP + V((2.6, 0, 0)); d2 = (END - E); d2.z = 0; L2 = d2.length; u2 = d2.normalized(); u1 = (E - H).normalized(); MID = E + u2 * (L2 * .52); ZB, ZT = PZ - 2.35, PZ - .75   # platform floor and top chord
hinge(N, H, (-2.2, 1.6), 1.1); arm = P.empty('arm', T(*H), P.model); HF = T(*H); g = Geo()
um = (u1 + u2).normalized(); S0 = section(H + u1 * .35, u1, 1.2, -2.4, 1.7); S1 = section(E, um, 2.3, -2.7, .9); S2 = section(MID, u2, 2.0, ZB - .9, ZT); S3 = section(END - u2 * .2, u2, 1.9, ZB, ZT)
space_truss(g, S0, S1, 5, .16); space_truss(g, S1, S2, 6, .17); space_truss(g, S2, S3, 5, .10, .7)
g.add(tube([(H.x, H.y, -2.5), (H.x, H.y, 1.8)], .24, 14, zone=Z.dark))
for s in (0, 1): g.add(tube([tuple(S1[s]), tuple(S2[s] + V((0, 0, .0)))], .2, 12, zone=Z.dark))
PLT = deck(g, MID - u2 * .6, END, 1.9, ZB + .08, rail=None); deck(g, E, MID, 1.0, -.6, rail=.6); deck(g, H + u1 * .4, E, .9, -.6, rail=.6)
g.add(box(1.5, 1.0, .5, zone=Z.white, bevel=.03), PLT @ T(-2.2, .35, .5)); [g.add(box(.5, .4, 1.0, zone=Z.grey, bevel=.03), PLT @ T(x, -.6, .6)) for x in (-3.4, -1.0, 1.2)]
# pipework: two lagged mains that snake down the dog-leg, smaller lines beside them, runs of cable on the side
def pipe(off, z, r, zn, up=.0):
    q = lambda c, dr, k, zz: c + V((-dr.y, dr.x, 0)) * k + V((0, 0, zz)); pts = [q(H + u1 * .9, u1, off, z), q(E - u1 * 1.2, u1, off, z), q(E, um, off, z), q(E + u2 * 1.2, u2, off, z), q(MID - u2 * 1.5, u2, off, z), q(MID - u2 * .6, u2, off, ZB + .55 + up), q(END - u2 * 7.2, u2, off, ZB + .55 + up)] + [q(END - u2 * k, u2, max(-.4, min(.4, off)), ZB + .55 + up + h) for k, h in ((6.2, 0), (5.45, 0), (5.22, .04), (5.03, .17), (4.92, .36), (4.9, .56))] + [q(END - u2 * 4.9, u2, max(-.4, min(.4, off)), ZT + .16)]
    g.add(tube([tuple(p) for p in pts], r, 12, zone=zn)); [g.add(tube([tuple(a.lerp(b, t)), tuple(a.lerp(b, t) + (b - a).normalized() * .08)], r + .035, 12, zone=Z.grey)) for a, b in zip(pts, pts[1:]) if (b - a).length > 2 for t in (.25, .5, .75)]
pipe(.35, -.1, .20, Z.white); pipe(-.15, -.15, .20, Z.white, .1); pipe(-.55, .0, .10, Z.alu); pipe(.68, -.2, .08, Z.copper, -.2)
g.add(box(.5, 1.7, .7, zone=Z.grey, bevel=.04), T(*(H + u1 * .85 + V((0, 0, -.12)))) @ Rz(math.degrees(math.atan2(u1.y, u1.x))))      # manifold the mains start from
CA, CB = S2[3], S3[3]
for k in range(5): g.add(tube([tuple(p + V((0, 0, -.12 * k - .5))) for p in (CA, CB)], .018, 5, zone=Z.steel))
for t in np.linspace(0, 1, 7): c = CA.lerp(CB, float(t)); g.add(tube([tuple(c), tuple(c + V((0, 0, -1.06)))], .035, 6, zone=Z.dark))
# tan stabiliser plates under the platform
for s in (-1, 1): g.add(box(1.8, .5, .14, zone=Z.invar, bevel=.02), PLT @ T(-1.2, s * .6, -.55) @ Rz(s * 24)); g.add(box(.3, .3, .5, zone=Z.invar, bevel=.02), PLT @ T(-1.9, s * .5, -.35))
deck(g, END - u2 * 5.8, END, 1.8, ZT + .06)
AF = T(END.x, END.y, ZT + .085) @ Rz(math.degrees(math.atan2(-u2.y, -u2.x)))        # deck top at the boom end; +X back along the arm
for k in (-1, 1): g.add(box(4.5, .10, .09, zone=Z.steel, bevel=.01), AF @ T(2.5, k * .62, .045)); g.add(box(.12, .22, .26, zone=Z.dark, bevel=.02), AF @ T(4.72, k * .62, .13)); g.add(box(.12, .22, .26, zone=Z.dark, bevel=.02), AF @ T(.28, k * .62, .13))
g.add(box(1.0, 1.0, .18, zone=Z.grey, bevel=.02), AF @ T(4.9, 0, .09))        # where the mains come up
P.mesh('truss', Geo().add(g), P.det, parent=arm, frame=HF)
for nm, a, b in (('col_a', S0, S1), ('col_b', S1, S2), ('col_c', S2, S3)): seg_collider(nm, a, b, arm)
# ---------------- boom with the X plate; frame: x away from the ship
BA = math.degrees(math.atan2(-u2.y, -u2.x)); BK = lambda k, y, z: T(2.6, 0, 0) @ Rz(BA) @ V((k, y, z))      # k metres back along the arm from its end
PF = T(TIP.x, TIP.y, PZ); plate = P.empty('plate', PF, arm); r = Geo()
for s1 in (-1, 1):
    for s2 in (-1, 1): r.add(box(.16, .16, .82, zone=Z.invar, bevel=.02), T(.16, s1 * .30, s2 * .36) @ Rx(-s1 * s2 * 34)); r.add(box(.12, .24, .16, zone=Z.alu, bevel=.02), T(.08, s1 * .52, s2 * .70)); r.add(cyl(.05, .16, 10, zone=Z.steel), T(.04, s1 * .52, s2 * .70) @ Ry(90))
r.add(box(.14, .62, .86, zone=Z.alu, bevel=.03, center=(.10, 0, 0))); r.add(box(.08, .5, .7, zone=Z.grey, bevel=.02, center=(.04, 0, 0)))
for y, z, rr in ((-.13, .16, .11), (.13, .16, .11), (-.13, -.14, .09), (.13, -.14, .09), (0, -.28, .05)):
    r.add(cyl(rr, .12, 18, zone=Z.steel, bevel=.012), T(.0, y, z) @ Ry(90)); r.add(tube([(.16, y, z), (.8, y * 1.2, z), (1.7, y * 1.6, z * .6 - .03)] + [tuple(BK(k, y * 2.0, zz)) for k, zz in ((.1, -.20), (.5, -.22), (1.0, -.22))], rr * .85, 10, zone=Z.white if rr > .08 else Z.copper))
for s in (-1, 1):
    for z0, z1, rr in ((.0, .0, .07), (-.34, -.38, .06)): r.add(tube([(.2, s * .3, z0), (2.1, s * .40, z1), tuple(BK(.2, s * .46, z1)), tuple(BK(1.0, s * .46, z1))], rr, 10, zone=Z.dark))
    [r.add(tube([(x, s * (.3 + (x - .2) * .052), 0), (x + .4, s * (.3 + (x + .2) * .052), -.36)], .04, 6, zone=Z.dark)) for x in (.4, .9, 1.4)]
CF = T(2.6, 0, 0) @ Rz(BA); DK = ZT + .085 - PZ                # carriage, in the arm's direction; DK: deck top
r.add(box(1.5, 1.15, -DK + .02, zone=Z.dark, bevel=.04, center=(1.65, 0, DK / 2 + .07)), CF); r.add(box(1.3, .8, .16, zone=Z.grey, bevel=.03, center=(1.65, 0, .16)), CF); r.add(box(.06, 1.0, .10, zone=Z.stripe, center=(.88, 0, .0)), CF)
for k in (-1, 1):
    r.add(box(1.5, .16, .16, zone=Z.alu, bevel=.02, center=(1.65, k * .62, DK + .17)), CF); [r.add(cyl(.08, .14, 14, zone=Z.steel), CF @ T(x, k * .62, DK + .17) @ Rx(90)) for x in (1.1, 2.2)]
r.add(box(.06, 1.0, .10, zone=Z.stripe, center=(.30, 0, .56)))
P.mesh('boom', Geo().add(r, PF), P.det, parent=plate, frame=PF)
P.hull_collider('col_boom', [(TIP.x + x, TIP.y + y, PZ + z) for x in (.1, 2.6) for y in (-.45, .45) for z in (-.5, .5)] + [tuple(PF @ BK(k, y, z)) for k in (.9, 2.4) for y in (-.55, .55) for z in (-.6, .2)], parent=plate)
CL = 'qdArm'; NF = 108; l0 = plate.location.copy()
for f, l in ((0, l0), (6, l0 + V((.3, 0, 0))), (20, l0 + V((.3, 0, 0)) - u2 * 1.3), (NF, l0 + V((.3, 0, 0)) - u2 * 1.3)): P.key(CL, plate, f, location=l)
q = P.rest_quat(arm); SW = -92
for f, a in ((0, 0), (14, 0), (NF, SW)): P.key(CL, arm, f, rotation_quaternion=q @ Quaternion((0, 0, 1), math.radians(a)))
P.clips['qdArmStage'] = {k: list(v) for k, v in P.clips[CL].items()}         # StagedAnimation plays its own copy
print('QD arm: legs %.1f + %.1f m' % ((E - H).length, L2))
P.node('mount', (0, 0, 0), (-N.x, -N.y, 0), 3); P.bake_clips(0); finish(P)

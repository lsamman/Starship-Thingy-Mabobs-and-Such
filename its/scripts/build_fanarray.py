"""Seven-petal fan array (Saturn and Jupiter renders). Stowed it hangs inside the skirt; deploying, it slides down past the
rim, swings outboard, unfolds each petal's three panels and opens the fan. Origin on the inside of the skirt at the rim,
-Y outboard, +Z up the ship. Authored deployed; frame 0 is stowed."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
P = start('ITS_FanArray')
MS = P.material('its_solar', spec=(.9, .9, .95), shininess=.6)
NP, ANG, R0, SEG, NS = 7, 9.8, .62, 2.62, 4
SLIDE, OFF, PIT = 3.80, .34, .040                  # slide travel, stand-off of the package from the wall, petal pitch
F = dict(slide=(0, 45), swing=(45, 85), fold=(85, 160), fan=(150, 220)); N = 220
XA = Vector((1, 0, 0))
PIV = Vector((0, OFF, -SLIDE + 3.05))              # hinge of the arm, deployed
W = lambda r: r * math.tan(math.radians(ANG / 2)) * .97

# ---------------- fixed: rails and bracket on the skirt wall
b = Geo()
for s in (-1, 1):
    b.add(box(.09, .13, 3.5, zone=Z.alu, bevel=.015, center=(s * .52, .09, 1.45)))
    b.add(box(.05, .06, 3.4, zone=Z.dark, bevel=.01, center=(s * .52, .18, 1.45)))
    for z in (-.1, 1.0, 2.1, 3.0):
        b.add(box(.24, .10, .18, zone=Z.grey, bevel=.02, center=(s * .52, .05, z)))
for z in (-.1, 1.5, 3.0):
    b.add(box(1.0, .06, .08, zone=Z.grey, bevel=.015, center=(0, .05, z)))
b.add(box(.26, .16, .34, zone=Z.white, bevel=.02, center=(0, .12, 2.6)))
b.add(tube([(.0, .16, 2.4), (.10, .14, 1.8), (.30, .12, 1.4), (.44, .12, 1.2)], .02, 6, zone=Z.rubber))
P.mesh('base', b, P.det)

slide = P.empty('slide', T(0, 0, 0), P.model)
for f, z in ((0, SLIDE - 0), (F['slide'][1], 0.0), (N, 0.0)):
    P.key('fanDeploy', slide, f, location=Vector((0, 0, z)))
g = Geo()
for s in (-1, 1):
    g.add(box(.10, .16, .46, zone=Z.white, bevel=.02, center=(s * .52, OFF - .06, PIV.z + .22)))
    g.add(cyl(.09, .10, 14, zone=Z.steel, bevel=.012), T(s * .48, PIV.y, PIV.z) @ Ry(90))
g.add(box(1.0, .08, .12, zone=Z.white, bevel=.015, center=(0, OFF - .07, PIV.z + .34)))
g.add(tube([(-.5, PIV.y, PIV.z), (.5, PIV.y, PIV.z)], .04, 10, zone=Z.steel))
P.mesh('carriage', g, P.det, parent=slide)

# ---------------- arm: at rest points straight up beside the rails, deployed straight outboard
AF = Matrix(((1, 0, 0, PIV.x), (0, 0, -1, PIV.y), (0, 1, 0, PIV.z), (0, 0, 0, 1)))     # X across, Y up the ship (panel normal), Z outboard
arm = P.empty('arm', AF, slide)
q1 = P.rest_quat(arm)
q0 = (Matrix.Rotation(math.radians(-90), 3, 'X') @ AF.to_3x3())                       # outboard (-Y) -> up (+Z)
if (q0 @ Vector((0, 0, 1))).z < 0:
    q0 = (Matrix.Rotation(math.radians(90), 3, 'X') @ AF.to_3x3())
q0 = q0.to_quaternion()
DOWN = (Matrix.Rotation(math.radians(90), 3, 'X') @ AF.to_3x3()).to_quaternion()
if (DOWN @ Vector((0, 0, 1))).z > 0: DOWN = (Matrix.Rotation(math.radians(-90), 3, 'X') @ AF.to_3x3()).to_quaternion()
# it hangs from the hinge: package below the carriage, so it slides out of the skirt first and then swings up and out
for f, q in ((0, DOWN), (F['swing'][0], DOWN), (F['swing'][1], q1), (N, q1)):
    P.key('fanDeploy', arm, f, rotation_quaternion=q)
a = Geo()
a.add(cyl(.10, .34, 18, zone=Z.white, bevel=.015, center_z=False), AF @ T(0, 0, .05))
a.add(box(.60, .10, .20, zone=Z.white, bevel=.02), AF @ T(0, 0, .06))
a.add(cyl(.13, .10, 18, zone=Z.dark, bevel=.012, center_z=False), AF @ T(0, 0, .36))
P.mesh('armbody', a, P.det, parent=arm, frame=AF)
SP = AF @ T(0, 0, .46)
piv = P.empty('sunPivot', SP, arm)
P.empty('suncatcher', SP @ T(0, .2, 3.0), piv)
h = Geo()
h.add(cyl(.12, .16, 18, zone=Z.white, bevel=.015), SP)
h.add(box(.34, .42, .24, zone=Z.white, bevel=.025), SP @ T(0, 0, .16))
h.add(cyl(.20, .40, 24, zone=Z.alu, bevel=.02), SP @ T(0, 0, .30) @ Rx(90))
h.add(bolts(10, .16, .014), SP @ T(0, .20, .30) @ Rx(-90))
P.mesh('hub', h, P.det, parent=piv, frame=SP)

# ---------------- petals: fan root at the hub, turning about the panel normal (local Y)
HUB = SP @ T(0, 0, .30)


def panel(r0, r1):
    """One panel of a petal between radii (along local Z, hub at 0): cells in front (+Y), film and battens behind."""
    c, d = Geo(), Geo(); t = .007
    z0, z1 = 0.0, r1 - r0
    P4 = [(-W(r0), z0 + .015), (W(r0), z0 + .015), (W(r1), z1 - .015), (-W(r1), z1 - .015)]
    n = len(c.v)
    uv = lambda x, z: (.5 + x / (2 * W(R0 + NS * SEG)) * .96, .02 + .96 * (r0 + z - R0) / (NS * SEG))
    c.v += [(x, t, z) for x, z in P4]
    c.face([3, 2, 1, 0], [uv(*P4[k]) for k in (3, 2, 1, 0)])
    d.v += [(x, 0, z) for x, z in P4]
    d.face([0, 1, 2, 3], [(0, -10)] * 4)
    # edge frame and battens
    for s in (-1, 1):
        d.add(strut((s * W(r0), .0, z0 + .01), (s * W(r1), .0, z1 - .01), .016, Z.dark, 6))
        d.add(strut((s * W(r0) * .33, -.004, z0 + .02), (s * W(r1) * .33, -.004, z1 - .02), .009, Z.dark, 4))
    for z, r in ((z0 + .015, r0), (z1 - .015, r1), ((z0 + z1) / 2, (r0 + r1) / 2)):
        d.add(strut((-W(r), 0, z), (W(r), 0, z), .012, Z.dark, 6))
    for s in (-.5, .5):                             # hinges
        d.add(cyl(.02, .09, 8, zone=Z.steel), T(s * W(r1), 0, z1) @ Ry(90))
    return c, d


for i in range(NP):
    lay = (i - (NP - 1) / 2) * PIT
    B = HUB @ T(0, lay, 0)
    a_ = (i - (NP - 1) / 2) * ANG
    root = P.empty(f'petal{i}', B @ Ry(a_), piv)
    qd = P.rest_quat(root); qs = (B.to_3x3().inverted() @ B.to_3x3()).to_quaternion()
    qs = piv.matrix_world.to_quaternion().inverted() @ B.to_quaternion()
    for f, q in ((0, qs), (F['fan'][0], qs), (F['fan'][1], qd), (N, qd)):
        P.key('fanDeploy', root, f, rotation_quaternion=q)
    d0 = Geo(); d0.add(box(.07, .028, R0 - .05, zone=Z.white, bevel=.008, center=(0, 0, (R0 + .05) / 2)))
    d0.add(cyl(.15, .030, 18, zone=Z.white, bevel=.006), Rx(90))
    par, fr = root, B @ Ry(a_) @ T(0, 0, R0)
    for k in range(NS):
        r0, r1 = R0 + k * SEG, R0 + (k + 1) * SEG
        c, d = panel(r0, r1)
        if k == 0:
            d.add(d0, T(0, 0, -R0))
        c2, d2 = Geo(), Geo(); c2.add(c, fr); d2.add(d, fr)
        # one mesh, one material per panel: frame and film take two flat patches of the solar sheet
        d2.uv = [tuple(((.90, .05) if u_[0][1] < -9 else (.10, .05)) for _ in u_) for u_ in d2.uv]
        d2.add(c2); o = P.mesh(f'panel{i}_{k}', d2, MS, parent=par, frame=fr)
        if k:
            qr = P.rest_quat(o); ql = qr @ Quaternion((1, 0, 0), math.radians(179 if k % 2 else -179))
            st = (F['fold'][0] + 8 * (k - 1), F['fold'][1] - 8 * (NS - 1 - k))
            mid = qr @ Quaternion((1, 0, 0), math.radians(90 if k % 2 else -90))
            for f, q in ((0, ql), (st[0], ql), ((st[0] + st[1]) // 2, mid), (st[1], qr), (N, qr)):
                P.key('fanDeploy', o, f, rotation_quaternion=q)
        par, fr = o, fr @ T(0, 0, SEG)
P.hull_collider('col_base', [(x, y, z) for x in (-.6, .6) for y in (0, .2) for z in (-.2, 3.1)])
P.node('mount', (0, 0, 0), (0, -1, 0), 1)
P.bake_clips(0)
finish(P)

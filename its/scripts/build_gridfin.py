"""Booster grid fin: coffin-shaped lattice hanging from a ball hinge under its fairing (slide 33, landing render).
Origin on the hull at the hinge, -Y outward, +Z up the booster. finDeploy swings it out; `ctrl` turns about its span."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
P = start('ITS_GridFin')
HY = -.34                                             # hinge stand-off
LEN, WS, WB, SH, CH = 4.40, 2.06, 1.02, 1.72, .40     # span, shoulder width, tip width, shoulder position, chord
H0 = T(0, HY, 0)
# deployed frame: X out along the span, Y across, Z up the booster
F = Matrix(((0, 1, 0, 0), (-1, 0, 0, HY), (0, 0, 1, 0), (0, 0, 0, 1)))
OUT = [(.30, -.34), (SH, -WS / 2), (LEN - .06, -WB / 2), (LEN, -WB / 2 + .07), (LEN, WB / 2 - .07), (LEN - .06, WB / 2), (SH, WS / 2), (.30, .34)]


def wall_strip(a, b, t, c, zone):
    """Blade from a to b in the fin plane: thickness t, chord c, knife edges fore and aft."""
    a, b = Vector((*a, 0)), Vector((*b, 0)); d = (b - a); ln = d.length; d.normalize(); n = Vector((-d.y, d.x, 0))
    g = Geo(); e = min(.035, c * .12)
    sec = ((0, c / 2), (t / 2, c / 2 - e), (t / 2, -c / 2 + e), (0, -c / 2), (-t / 2, -c / 2 + e), (-t / 2, c / 2 - e))
    for p in (a, b):
        for x, z in sec:
            g.v.append(tuple(p + n * x + Vector((0, 0, z))))
    for k in range(6):
        k2 = (k + 1) % 6; L_ = min(1, ln / 2.8)
        g.face([k, 6 + k, 6 + k2, k2], [zone.uv(0, k / 6), zone.uv(L_, k / 6), zone.uv(L_, (k + 1) / 6), zone.uv(0, (k + 1) / 6)])
    return g


def clip(p, d):
    """Interval of the line p + t d inside the outline."""
    t0, t1 = -50.0, 50.0; n = len(OUT)
    for i in range(n):
        a, b = OUT[i], OUT[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        nx, ny = -ey, ex                              # inward normal for this winding
        num = (p[0] - a[0]) * nx + (p[1] - a[1]) * ny; den = d[0] * nx + d[1] * ny
        if abs(den) < 1e-9:
            if num < 0: return None
            continue
        t = -num / den
        if den > 0: t0 = max(t0, t)
        else: t1 = min(t1, t)
    return (t0, t1) if t1 - t0 > .08 else None


fin = Geo(); lat = Geo()
area = sum(OUT[i][0] * OUT[(i + 1) % 8][1] - OUT[(i + 1) % 8][0] * OUT[i][1] for i in range(8))
if area < 0: OUT = OUT[::-1]
dx, dy = .40, .62 * .40 / .40                         # diamonds: .40 wide, .62 tall
for s in (1, -1):
    d = Vector((dy, s * dx, 0)).normalized()
    for k in range(-14, 15):
        p = (2.0 + k * dy, 0)
        c = clip(p, (d.x, d.y))
        if c:
            a, b = [(p[0] + d.x * t, p[1] + d.y * t) for t in c]
            lat.add(wall_strip(a, b, .028, CH * .86, Z.black))
n = len(OUT)
for i in range(n):
    fin.add(wall_strip(OUT[i], OUT[(i + 1) % n], .085, CH, Z.black))
for x, y in OUT:                                      # round the frame's corners
    fin.add(cyl(.0425, CH - .07, 10, zone=Z.black), T(x, y, 0))
# root casting: gusset plates, ball, trunnion
fin.add(box(.34, .66, CH * .9, zone=Z.black, bevel=.05, center=(.22, 0, 0)))
fin.add(lathe([(0, -.30), (.14, -.27), (.25, -.17), (.30, 0), (.25, .17), (.14, .27), (0, .30)], 24, zone=Z.dark))
for s in (-1, 1):
    fin.add(wall_strip((.10, s * .10), (1.05, s * .30), .05, CH * .95, Z.black))
    fin.add(cyl(.15, .06, 18, zone=Z.steel, bevel=.012, center_z=False), T(0, 0, s * .27) @ (Rx(180) if s < 0 else Matrix()))
fin.add(bolts(8, .11, .014), T(0, 0, .33))
for y in (-.25, 0, .25):
    fin.add(cyl(.03, .05, 8, zone=Z.steel), T(.40, y, 0) @ Ry(90))
lat2 = Geo(); lat2.add(lat, F); fin2 = Geo(); fin2.add(fin, F)

# fixed part: backing plate on the hull, shaft, actuator pair and harness
b = Geo()
b.add(box(.80, .62, .06, zone=Z.grey, bevel=.02), T(0, -.02, 0) @ Rx(90))
b.add(cyl(.20, -HY - .20, 20, zone=Z.steel, bevel=.012, center_z=False), T(0, 0, 0) @ Rx(90))
b.add(cyl(.27, .08, 22, zone=Z.dark, bevel=.015, center_z=False), T(0, -.02, 0) @ Rx(90))
b.add(bolts(12, .235, .016), T(0, -.10, 0) @ Rx(90))
for s in (-1, 1):
    b.add(cyl(.075, .50, 14, zone=Z.alu, bevel=.012), T(s * .36, -.11, .06))
    b.add(cyl(.045, .20, 12, zone=Z.steel), T(s * .36, -.11, -.26))
    b.add(tube([(s * .36, -.11, .31), (s * .34, -.09, .42), (s * .20, -.06, .46), (s * .10, -.05, .30)], .022, 6, zone=Z.rubber))
P.mesh('base', b, P.det)
dep = P.empty('deploy', H0, P.model)
q0 = Quaternion((1, 0, 0), math.radians(90))           # stowed: the span hangs down
ctrl = P.empty('ctrl', F, dep)
P.mesh('lattice', lat2, P.det, parent=ctrl, frame=F, smooth_angle=25)
P.mesh('frame', fin2, P.det, parent=ctrl, frame=F, smooth_angle=35)
pts = [tuple(F @ Vector((x, y, z))) for x, y in OUT for z in (-.08, .08)]
P.hull_collider('col_fin', pts, parent=ctrl, frame=F)
P.hull_collider('col_base', [(x, y, z) for x in (-.4, .4) for y in (0, -.12) for z in (-.3, .3)])
for f, q in ((0, q0), (60, Quaternion())):
    P.key('finDeploy', dep, f, rotation_quaternion=q)
P.empty('CoL', T(0, HY - 2.0, 0), P.model)
P.node('mount', (0, 0, 0), (0, 1, 0), 1)
P.bake_clips(0)
finish(P)

"""Payload plate with a modular fairing (SimpleAdjustableFairings): base ring and plate, and one half of each fairing piece.
A piece's transform sits at its own bottom, its half faces +x; the plugin copies, stacks and turns them."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
import fairing_layout as F
P = start('STMS_B3_FairingBase'); R = F.R; V = Vector
MW = P.material('stms_fairing', spec=(.22, .22, .22), shininess=.25); MI = P.material('its_det', spec=(.25, .25, .25), shininess=.25, name='fin'); MS = sep_mat(P, 'stms_steel', 'stms_steel_diff', 'stms_steel_nrm', 'stms_steelmask_diff')
# ---------------- base: steel skirt to the core's skin, white ring under the fairing, payload plate on a truss cone
st = Geo(); st.add(lathe([(R, F.SKIRT), (R, .12)], 96, uv_fn=lambda a, r, z, s: (a / 90, z * .3))); P.mesh('skirt', st, MS, smooth_angle=30)
g = Geo()
g.add(lathe([(R, .12), (R + .03, .13), (R + .03, .22), (R, .24), (R, F.Z0), (R - .10, F.Z0), (R - .10, .30), (2.55, .20), (1.9, .30), (1.55, .52), (1.42, .60), (0, .60)], 96, zone=Z.white))
g.add(lathe([(1.40, .60), (1.40, .68), (1.30, .70), (1.16, .70), (1.10, .64), (1.10, .60)], 64, zone=Z.alu)); g.add(bolts(48, 1.25, .018), T(0, 0, .70)); g.add(bolts(72, R - .05, .016), T(0, 0, F.Z0))
for k in range(24): g.add(box(.05, .95, .16, zone=Z.alu, bevel=.01), Rz(15 * k) @ T(0, -2.05, .34) @ Rx(-12))
for k in range(8): g.add(box(.30, .22, .20, zone=Z.grey, bevel=.03), Rz(45 * k + 12) @ T(0, -2.45, .32))
for k in range(12): g.add(box(.12, .10, .05, zone=Z.dark, bevel=.01), Rz(30 * k) @ T(0, -(R + .02), .18))
for a0 in range(0, 360, 60): g.add(tube([tuple(on_cyl(a0 + t, .26, 2.3).translation) for t in range(0, 41, 8)], .03, 6, zone=Z.copper))
g.add(lathe([(R - .004, F.SKIRT), (R - .06, F.SKIRT), (R - .06, .0), (1.5, .12), (0, .14)], 96, zone=Z.wall, flip=True))
P.mesh('base', g, P.det, smooth_angle=32)
# ---------------- one half of each piece; azimuth here is about +x
N = 32
def half(prof, rows, inner, seg=N):
    """Outer skin, inner skin and edges of a half shell. prof: (r, z) upward. The sheet's u runs round the half."""
    o, i = Geo(), Geo(); y0, y1 = rows; arc = [0.0]
    for p, q in zip(prof, prof[1:]): arc.append(arc[-1] + math.dist(p, q))
    for k in range(seg + 1):
        t = math.pi * (k / seg - .5); ca, sa = math.cos(t), math.sin(t)
        for (r, z) in prof: o.v.append((r * ca, r * sa, z))
        for (r, z) in prof: i.v.append(((r - inner) * ca, (r - inner) * sa, z))
    m = len(prof); uv = lambda k, j: ((.5 + k / seg * 2047) / 2048, 1 - (y1 - 3 - (y1 - y0 - 6) * arc[j] / arc[-1]) / 2048)
    for k in range(seg):
        for j in range(m - 1):
            o.face([k * m + j, (k + 1) * m + j, (k + 1) * m + j + 1, k * m + j + 1], [uv(k, j), uv(k + 1, j), uv(k + 1, j + 1), uv(k, j + 1)])
            zz = lambda a, b: Z.wall.uv((a / 8) % 1.0001, (arc[b] / 2.2) % 1.0001); i.face([k * m + j + 1, (k + 1) * m + j + 1, (k + 1) * m + j, k * m + j], [Z.wall.uv(.1 + .1 * (k % 8), .3), Z.wall.uv(.2 + .1 * (k % 8), .3), Z.wall.uv(.2 + .1 * (k % 8), .1), Z.wall.uv(.1 + .1 * (k % 8), .1)])
    e = Geo()
    for k, fl in ((0, False), (seg, True)):                # split edges
        t = math.pi * (k / seg - .5); ca, sa = math.cos(t), math.sin(t)
        for (p, q) in zip(prof, prof[1:]):
            n = len(e.v); e.v += [(p[0] * ca, p[0] * sa, p[1]), (q[0] * ca, q[0] * sa, q[1]), ((q[0] - inner) * ca, (q[0] - inner) * sa, q[1]), ((p[0] - inner) * ca, (p[0] - inner) * sa, p[1])]; f = [n, n + 1, n + 2, n + 3]; e.face(f if not fl else f[::-1], [Z.dark.uv(*u) for u in ((0, 0), (0, .5), (.1, .5), (.1, 0))])
    return o, i.add(e)
def piece(nm, z, prof, rows, inner=.05, cols=6, full=False):
    fr = T(0, 0, z); e = P.empty(nm, fr, P.model); o, i = half(prof, rows, inner)
    if full:
        o2, i2 = Geo(), Geo(); [(o2.add(o, Rz(a)), i2.add(i, Rz(a))) for a in (0, 180)]; o, i = o2, i2
    P.mesh(nm + '_out', Geo().add(o, fr), MW, parent=e, frame=fr, smooth_angle=40); P.mesh(nm + '_in', Geo().add(i, fr), MI, parent=e, frame=fr, smooth_angle=40)
    if not full:
        for k in range(cols):
            t0, t1 = [math.pi * (q / cols - .5) for q in (k, k + 1)]
            for j, (a, b) in enumerate(zip(prof[::3] if len(prof) > 4 else prof, (prof[3::3] if len(prof) > 4 else prof[1:]))):
                P.hull_collider(f'{nm}_col{k}_{j}', [(r_ * math.cos(t), r_ * math.sin(t), q[1] + z) for q in (a, b) for r_ in (q[0], q[0] - .08) for t in (t0, (t0 + t1) / 2, t1)], parent=e, frame=fr)
    else: P.hull_collider(nm + '_col', [(r_ * math.cos(t), r_ * math.sin(t), q + z) for r_, q in ((F.CAPR, 0), (.3, F.CAPH * .85)) for t in np.linspace(0, TAU, 12)], parent=e, frame=fr)
    return e
zc = [F.CONE * t for t in np.linspace(0, 1, 16)]; cone = [(F.ogive(z / F.CONE), z) for z in zc]
sl = (cone[-2][0] - cone[-1][0]) / (cone[-1][1] - cone[-2][1])
caps = [(F.CAPR, 0.0)] + [(F.CAPR * math.cos(t), F.CAPH * math.sin(t)) for t in np.linspace(.15, math.pi / 2 - .02, 9)]
piece('FWallBase', F.Z0, [(R, 0), (R, F.WB)], F.ROWS['base']); piece('FWall', F.Z0 + F.WB, [(R, 0), (R, F.WALL)], F.ROWS['wall']); piece('FCone', F.Z0 + F.WB, cone, F.ROWS['cone']); piece('FCap', F.Z0 + F.WB + F.CONE, caps, F.ROWS['cap'], full=True)
P.hull_collider('col_base', [(r * math.cos(t * TAU / 20), r * math.sin(t * TAU / 20), z) for r, z in ((R, F.SKIRT), (R, .30), (1.4, .6)) for t in range(20)])
P.node('top', (0, 0, .70), (0, 0, 1), 3); P.node('bottom', (0, 0, 0), (0, 0, -1), 5)
P.variants = (); import facing; _ff = facing.fix_facing; facing.fix_facing = lambda objs, *a, **k: _ff([o for o in objs if not o.name.startswith('F')], *a, **k)
finish(P)

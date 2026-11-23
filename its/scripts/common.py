"""Helpers shared by the ITS build scripts. K scales real metres to KSP metres."""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sl import *
import hull as H, layout as L
from shell import *
K = H.K


class Zones:
    def __init__(self, ppm=170):
        self.z = {k: Zone(*v, atlas=2048, ppm=ppm) for k, v in L.DET.items()}

    def __getattr__(self, k):
        return self.__dict__['z'][k]


Z = Zones()


def start(name):
    if not hasattr(bpy.types.Material, 'mumatprop'): enable_addon()
    clean_scene(); np.random.seed(7)
    P = Part(name)
    P.out = sys.argv[sys.argv.index('--') + 1]
    P.det = P.material('its_det', spec=(.8, .8, .8), shininess=.4)
    return P


def finish(P, variants=()):
    P.variants = variants
    P.export(P.out); P.save_blend(P.out)


def surf(az, z, origin, off=0.0):
    """Frame on the ship's skin: +Z along the outward normal, +Y up the ship. off in real metres."""
    e = .05
    p = Vector(H.point(az, z, off)); pa = Vector(H.point(az + .4, z, off)) - Vector(H.point(az - .4, z, off))
    pz = Vector(H.point(az, min(z + e, H.Z_TIP - .01), off)) - Vector(H.point(az, z - e, off))
    n = pa.cross(pz).normalized()
    up = (pz - pz.dot(n) * n).normalized()
    x = up.cross(n)
    m = Matrix((x, up, n)).transposed().to_4x4()
    m.translation = (p - Vector((0, 0, origin))) * K
    return m


def wall(outer, inner, zone):
    """Close the rim between two skins that share topology (inner built with flip=True, same vertex order)."""
    g = Geo()
    from collections import Counter
    cnt = Counter()
    for f in outer.f:
        for a, b in zip(f, f[1:] + f[:1]):
            cnt[frozenset((a, b))] += 1
    for f in outer.f:
        for a, b in zip(f, f[1:] + f[:1]):
            if cnt[frozenset((a, b))] == 1 and a != b:
                n = len(g.v)
                g.v += [outer.v[a], outer.v[b], inner.v[b], inner.v[a]]
                l = (Vector(outer.v[a]) - Vector(outer.v[b])).length
                g.face([n + 1, n, n + 3, n + 2], [zone.uv(0, 0), zone.uv(min(1, l), 0), zone.uv(min(1, l), .1), zone.uv(0, .1)])
    return g


def ring(r0, r1, z0, z1, zone, seg=72, a0=0, a1=360, bevel=.0):
    """Rectangular-section ring, all four sides. r0 < r1."""
    return lathe([(r0, z0), (r1, z0), (r1, z1), (r0, z1), (r0, z0)], seg, a0, a1, zone=zone)


def recolor(g, zone, ppm=None):
    """Planar-map a Geo's faces onto a zone by world position (dominant axis), for shapes without their own uvs."""
    out = Geo(); out.v = list(g.v)
    sm, tm = zone.span_m()
    for f in g.f:
        pts = [Vector(g.v[i]) for i in f]
        n = (pts[1] - pts[0]).cross(pts[-1] - pts[0])
        ax = max(range(3), key=lambda i: abs(n[i]))
        o = [i for i in range(3) if i != ax]
        a0 = min(p[o[0]] for p in pts); b0 = min(p[o[1]] for p in pts)
        wa = max(p[o[0]] for p in pts) - a0; wb = max(p[o[1]] for p in pts) - b0
        s0 = (a0 / sm) % 1; t0 = (b0 / tm) % 1
        ka = min(1, sm / wa) if wa > sm else 1; kb = min(1, tm / wb) if wb > tm else 1
        s0 = min(s0, 1 - min(1, wa * ka / sm)); t0 = min(t0, 1 - min(1, wb * kb / tm))
        out.face(f, [zone.uv(s0 + (p[o[0]] - a0) * ka / sm, t0 + (p[o[1]] - b0) * kb / tm) for p in pts])
    return out


def rcs_port(d=.28, zone=None):
    """Flush methalox thruster: bezel ring, dark throat set into the skin. Local +Z out."""
    g = Geo(); r = d / 2
    g.add(lathe([(r * 1.32, -.02), (r * 1.26, .012), (r, .018), (r * .78, .013), (r * .40, .011), (0, .011)], 16, zone=Z.black))
    return g


def bolts(n, r, br=.012, zone=None):
    g = Geo()
    p = cyl(br, br * .8, 6, zone=zone or Z.steel, center_z=False)
    for i in range(n):
        a = TAU * i / n
        g.add(p, T(r * math.cos(a), r * math.sin(a), 0))
    return g


def strut(a, b, r, zone=None, sides=8):
    return tube([tuple(a), tuple(b)], r, sides, zone=zone or Z.grey)


def groups(spots):
    """Ports in one cluster share one thruster transform (the middle port's): a plume and a sound emitter per port adds up."""
    by = {}
    for az, z in spots:
        by.setdefault((az, round(z / 4)), []).append((az, z))
    return {sorted(v, key=lambda q: q[1])[len(v) // 2] for v in by.values()}


def subdiv(g, L_=.16):
    """Split long quads so a flat piece can be bent onto the hull without the hull showing through its middle."""
    out = Geo(); out.v = list(g.v)
    for f, uv in zip(g.f, g.uv):
        if len(f) != 4:
            out.face(f, uv); continue
        p = [Vector(g.v[i]) for i in f]
        nu = max(1, math.ceil(max((p[1] - p[0]).length, (p[2] - p[3]).length) / L_)); nv = max(1, math.ceil(max((p[3] - p[0]).length, (p[2] - p[1]).length) / L_))
        if nu == nv == 1:
            out.face(f, uv); continue
        q = [Vector(t) for t in uv]; n0 = len(out.v); uvs = []
        for j in range(nv + 1):
            for i in range(nu + 1):
                a, b = i / nu, j / nv
                out.v.append(tuple((p[0] * (1 - a) + p[1] * a) * (1 - b) + (p[3] * (1 - a) + p[2] * a) * b))
                uvs.append(tuple((q[0] * (1 - a) + q[1] * a) * (1 - b) + (q[3] * (1 - a) + q[2] * a) * b))
        for j in range(nv):
            for i in range(nu):
                k = [j * (nu + 1) + i, j * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i]
                out.face([n0 + t for t in k], [uvs[t] for t in k])
    return out


def stick(g, az, z, origin, L_=.16, sink=.008):
    """Bend a detail authored flat (x across, y up, z off the surface) onto the ship's skin at (az, z real)."""
    g = subdiv(g, L_); out = Geo(); out.f, out.uv, out.smooth = g.f, g.uv, g.smooth
    r = float(H.section_r(az, z))
    for x, y, h in g.v:
        out.v.append(tuple(surf(az + math.degrees(x / K / r), z + y / K, origin) @ Vector((0, 0, h - sink))))
    return out


def stick_cyl(g, az, z, R, L_=.16, sink=.004):
    """The same on a cylinder of radius R (KSP metres)."""
    g = subdiv(g, L_); out = Geo(); out.f, out.uv, out.smooth = g.f, g.uv, g.smooth
    for x, y, h in g.v:
        a = math.radians(az) + x / R; rr = R + h - sink
        out.v.append((rr * math.sin(a), -rr * math.cos(a), z + y))
    return out

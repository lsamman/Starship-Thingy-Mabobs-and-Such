"""The outer surface of SEP's Block 3 nosecone, rebuilt from the measured rings in layout.py (no SEP mesh data),
and the window rows laid onto it. Blender axes in the nosecone model's frame; azimuth 0 is -y, the leeward steel."""
import math
from mathutils import Matrix, Vector
from sl import Geo, Zone, rounded_rect_ring
import layout as L

STEP = 360 / L.NOSE_SIDES
COS = math.cos(math.pi / L.NOSE_SIDES)
ZS = [z for z, _ in L.NOSE_RINGS]


def _seg(z):
    for i in range(len(ZS) - 1):
        if z <= ZS[i + 1] or i == len(ZS) - 2:
            return i


def ring_r(z):
    """Vertex radius at height z: straight between the measured rings, as in the mesh."""
    i = _seg(z); (z0, r0), (z1, r1) = L.NOSE_RINGS[i], L.NOSE_RINGS[i + 1]
    return r0 + (r1 - r0) * (z - z0) / (z1 - z0)


def slope(z):
    i = _seg(z); (z0, r0), (z1, r1) = L.NOSE_RINGS[i], L.NOSE_RINGS[i + 1]
    return (r1 - r0) / (z1 - z0)


def facet_az(az):
    return STEP * (math.floor(az / STEP) + .5)


def normal(az, z):
    """Outward normal of the flat facet under (az, z): the plane x.u = apothem(z)."""
    a = math.radians(facet_az(az))
    return Vector((math.sin(a), -math.cos(a), -slope(z) * COS)).normalized()


def point(az, z, off=0.0):
    """Point on the faceted shell at azimuth az (deg) and height z, pushed off along the facet normal."""
    ac = facet_az(az); rho = ring_r(z) * COS / math.cos(math.radians(az - ac)); a = math.radians(az)
    return Vector((rho * math.sin(a), -rho * math.cos(a), z)) + normal(az, z) * off


def surf(az, z, off=0.0):
    """Frame on the shell: +Z out along the normal, +Y up the surface, +X toward increasing azimuth."""
    n = normal(az, z); up = Vector((0, 0, 1)); up = (up - up.dot(n) * n).normalized(); x = up.cross(n)
    m = Matrix((x, up, n)).transposed().to_4x4(); m.translation = point(az, z, off)
    return m


def subdiv(g, L_):
    """Split long quads so a flat piece bends onto the facets without the hull showing through its middle."""
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


def stick(g, az, z, L_=.12, sink=L.NOSE_SINK):
    """Bend a piece authored flat (x across, y up the surface, z off it) onto the shell, centred at (az, z), sunk."""
    g = subdiv(g, L_); out = Geo(); out.f, out.uv, out.smooth = g.f, g.uv, g.smooth
    r = ring_r(z); c = 1 / math.sqrt(1 + slope(z) ** 2)
    for x, y, h in g.v:
        out.v.append(tuple(point(az + math.degrees(x / r), z + y * c, h - sink)))
    return out


def outline(w, h, rad, seg=4):
    pts = []
    for cx, cy, a0 in ((w / 2 - rad, h / 2 - rad, 0), (-w / 2 + rad, h / 2 - rad, 90), (-w / 2 + rad, -h / 2 + rad, 180), (w / 2 - rad, -h / 2 + rad, 270)):
        for k in range(seg + 1):
            t = math.radians(a0 + 90 * k / seg); pts.append((cx + rad * math.cos(t), cy + rad * math.sin(t)))
    return pts


def pane(w, h, cell, rings=3):
    """Rounded glass pane facing +Z, in rings so it can follow the facets. Each pane shows one of eight rooms."""
    g = Geo(); pts = outline(w, h, h * .36); m = len(pts)
    uv = lambda p: ((cell % 4 + .5 + p[0] / w * .9) / 4, (cell // 4 + .5 + p[1] / h * .9) / 2)
    g.v.append((0, 0, 0))
    for k in range(1, rings + 1):
        g.v += [(x * k / rings, y * k / rings, 0) for x, y in pts]
    for i in range(m):
        i2 = (i + 1) % m
        g.face([0, 1 + i, 1 + i2], [uv((0, 0)), uv(pts[i]), uv(pts[i2])])
        for k in range(1, rings):
            a, b = 1 + (k - 1) * m, 1 + k * m
            s0, s1 = k / rings, (k + 1) / rings
            g.face([a + i, b + i, b + i2, a + i2], [uv((pts[i][0] * s0, pts[i][1] * s0)), uv((pts[i][0] * s1, pts[i][1] * s1)),
                                                     uv((pts[i2][0] * s1, pts[i2][1] * s1)), uv((pts[i2][0] * s0, pts[i2][1] * s0))])
    return g


def windows(variant, zone):
    """Frames and glass for every window of a variant, laid on the shell. Returns (frames, glass, centres)."""
    frames, glass, spots = Geo(), Geo(), []
    F = L.NOSE_FRAME
    for row, (z, n, span, w, h) in enumerate(L.NOSE_ROWS[variant]):
        for i in range(n):
            az = -span + 2 * span * i / (n - 1) if n > 1 else 0.0
            fw, fh = w + 2 * F, h + 2 * F
            frames.add(stick(rounded_rect_ring(fw, fh, fh * .42, F + .004, L.NOSE_FRAME_H, 4, zone=zone), az, z))
            glass.add(stick(pane(w, h, (i * 3 + row * 5) % 8), az, z, .08, -L.NOSE_GLASS_OFF))
            spots.append((az, z, fw, fh))
    return frames, glass, spots

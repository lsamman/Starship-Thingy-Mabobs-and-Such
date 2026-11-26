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
    uv = lambda p: ((cell % 4 + .5 + p[0] / w * .9) / 8 + .5, (cell // 4 + .5 + p[1] / h * .9) / 4 + .5)   # rooms: top right
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


def arc(z):
    """Length along the shell's profile from its bottom ring up to z."""
    s = 0.0
    for (z0, r0), (z1, r1) in zip(L.NOSE_RINGS, L.NOSE_RINGS[1:]):
        if z <= z0:
            break
        t = min(z, z1) - z0; s += t * math.hypot(1, (r1 - r0) / (z1 - z0))
    return s


def arc_inv(s):
    lo, hi = L.NOSE_RINGS[0][0], L.NOSE_RINGS[-1][0]
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if arc(m) < s else (lo, m)
    return (lo + hi) / 2


def big_window(frame, glass, zone, sink=L.NOSE_SINK):
    """The ITS crew section's geodesic window (its/scripts/fwd.py nose_window), on SEP's faceted nose: an equilateral
    lattice inside a half-ellipse, x across and s up the skin. Every point goes through point(), the same bending onto
    the facets that stick() does, and the ribs are sampled finely so they follow the facets between lattice nodes."""
    B = L.NOSE_BIG; s0, s1 = arc(B['z0']), arc(B['z1']); ha = B['ha']

    def inside(x, s):
        t = (s - s0) / (s1 - s0)
        return 0 <= t <= 1 and abs(x) <= ha * math.sqrt(max(0, 1 - t ** 2.1))

    def P3(x, s, off):
        z = arc_inv(s)
        return point(math.degrees(x / ring_r(z)), z, off)

    def nrm(x, s):
        z = arc_inv(s)
        return normal(math.degrees(x / ring_r(z)), z)

    # glass: a fine grid inside the outline, fine enough that it stays above the facet edges
    g = Geo(); nx, ns = 56, 26; ids = {}
    for j in range(ns + 1):
        s = s0 + (s1 - s0) * j / ns * .998
        w = ha * math.sqrt(max(1e-4, 1 - ((s - s0) / (s1 - s0)) ** 2.1))
        for i in range(nx + 1):
            x = -w + 2 * w * i / nx
            ids[(i, j)] = (len(g.v), x / ha, (s - s0) / (s1 - s0)); g.v.append(tuple(P3(x, s, L.NOSE_GLASS_OFF)))
    for j in range(ns):
        for i in range(nx):
            q = [ids[(i, j)], ids[(i + 1, j)], ids[(i + 1, j + 1)], ids[(i, j + 1)]]
            g.face([t[0] for t in q], [(.02 + (t[1] * .5 + .5) * .46, .52 + t[2] * .46) for t in q])
    glass.add(g)

    def beam(pts, w, h):
        """Flat-topped rib along a polyline on the skin, its foot sunk."""
        g = Geo(); rows = []
        for i, (x, s) in enumerate(pts):
            x0, sa = pts[max(0, i - 1)]; x1, sb = pts[min(len(pts) - 1, i + 1)]
            n = nrm(x, s); d = (P3(x1, sb, 0) - P3(x0, sa, 0)); d = (d - d.dot(n) * n).normalized(); side = d.cross(n).normalized()
            p = P3(x, s, 0)
            row = []
            for u, v in ((-w, -sink), (-w * .7, h), (w * .7, h), (w, -sink)):
                row.append(len(g.v)); g.v.append(tuple(p + side * u + n * v))
            rows.append(row)
        for a, b in zip(rows, rows[1:]):
            for k in range(3):
                g.face([a[k], b[k], b[k + 1], a[k + 1]][::-1], [zone.uv(.1, .1), zone.uv(.1, .4), zone.uv(.4, .4), zone.uv(.4, .1)])
        return g

    def clip(a, b):
        """Part of a segment inside the outline."""
        ia, ib = inside(*a), inside(*b)
        if ia and ib:
            return a, b
        if not ia and not ib:
            return None
        lo, hi = (a, b) if ia else (b, a)
        p, q = lo, hi
        for _ in range(24):
            m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if inside(*m):
                p = m
            else:
                q = m
        return lo, p

    def fine(a, b, step=.06):
        n = max(2, math.ceil(math.dist(a, b) / step))
        return [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1)]
    side = B['side']; hgt = side * math.sqrt(3) / 2
    for j in range(-1, math.ceil((s1 - s0) / hgt) + 1):
        for i in range(-math.ceil(ha / side) - 1, math.ceil(ha / side) + 2):
            a = ((i + .5 * (j % 2)) * side, s0 + j * hgt)
            for dx, dj in ((side, 0), (side / 2, hgt), (-side / 2, hgt)):
                c = clip(a, (a[0] + dx, a[1] + dj))
                if c and math.dist(*c) > .03 and max(c[0][1], c[1][1]) > s0 + 1e-4:    # not the ribs hidden in the lower rim
                    frame.add(beam(fine(*c), .016, .016))
    rim = []
    for k in range(97):
        th = math.pi * k / 96
        rim.append((ha * math.cos(th), s0 + (s1 - s0) * math.sin(th) ** (2 / 2.1) * .999))
    frame.add(beam(rim, .038, .022)); frame.add(beam(fine((ha, s0), (-ha, s0)), .038, .022))


def in_door(az, z, D, pad=7):
    """Would a small window at (az, z) clash with the docking door D (layout.DOCK or DOCK_C)?"""
    return D['az'] - D['hw'] - pad < az < D['az'] + D['hw'] + pad and z - .2 < D['z'][1] and z + .17 > D['z'][0]


def windows(variant, zone):
    """Frames and glass for every window of a variant, laid on the shell: the big window, then the small rows.
    Windows where the side docking door goes are kept apart, so the door switch can show them when the door is elsewhere.
    Returns (frames, glass, small-window spots, side-door frames, side-door glass, their spots)."""
    frames, glass, spots = Geo(), Geo(), []; fs, gs, ss = Geo(), Geo(), []
    big_window(frames, glass, zone)
    F = L.NOSE_FRAME; w, h = L.SMALL
    for row, (z, n, span) in enumerate(L.NOSE_SMALL_ROWS[:L.NOSE_SMALL_COUNT[variant]]):
        for i in range(n):
            az = -span + 2 * span * i / (n - 1) if n > 1 else 0.0
            if abs(az) < L.EVA_HW + 6 and z - .3 < L.EVA_Z[1] and z + .3 > L.EVA_Z[0]: continue          # the EVA hatch is here
            assert not ('centre' in L.NOSE_DOORS[variant] and in_door(az, z, L.DOCK_C[variant])), (variant, az, z)      # the centred door keeps clear of every window
            side = in_door(az, z, L.DOCK)                   # under the side docking door: shown only when the door is elsewhere
            fw, fh = w + 2 * F, h + 2 * F
            (fs if side else frames).add(stick(rounded_rect_ring(fw, fh, fh * .42, F + .004, L.NOSE_FRAME_H, 4, zone=zone), az, z))
            (gs if side else glass).add(stick(pane(w, h, (i * 3 + row * 5) % 8), az, z, .08, -L.NOSE_GLASS_OFF))
            (ss if side else spots).append((az, z, fw, fh))
    return frames, glass, spots, fs, gs, ss

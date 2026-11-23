"""Forward section of the ship (z 27 to 49.5 m real), shared by the crew, cargo and tanker variants."""
from common import *
O = H.O_FWD
Z0 = L.FWD_BOT                     # joint with the aft section


def materials(P):
    M = P.material('its_fwd', spec=(.55, .55, .56), shininess=.45)
    return M


def joint(P, g, floor=True):
    """Field-joint ring and bolt circle at the split, plus a closing bulkhead under the cabin."""
    r = H.RB * K
    g.add(ring(r - .34, r - .004, Z0 + .002, Z0 + .16, Z.carbon))
    for k in range(48):
        a = 7.5 * k + 3.75
        g.add(cyl(.028, .03, 6, zone=Z.steel, center_z=False), on_cyl(a, Z0 + .16, r - .2) @ Rx(-90))
    if floor:
        g.add(lathe([(0, Z0 + .30), (1.2, Z0 + .28), (2.4, Z0 + .18), (r - .3, Z0 + .03)], 48, zone=Z.dome, flip=True))


def ports(P, spots, name='RCSthruster', d=.30):
    g = Geo(); lead = groups(spots)
    for az, z in spots:
        fr = surf(az, z, O, 0.0)
        g.add(rcs_port(d), fr)
        if (az, z) in lead:
            P.empty(name, fr, P.model)
    return g


# RCS on the fairing flanks and shoulders, where the renders put the dark ports
RCS = [(s * a, z) for s in (1, -1) for a, z in ((16, 30.3), (16, 29.5), (16, 28.7), (102, 31.0), (102, 30.2), (102, 29.4), (150, 30.5), (150, 29.7))] + \
      [(s * a, z) for s in (1, -1) for a, z in ((80, 43.2), (80, 42.4), (104, 43.2), (152, 43.2))]


def colliders(P, hollow=False):
    if not hollow:
        pts = []
        for z in (27, 34, 39, 43, 46, 48, 49.2):
            az = np.arange(0, 360, 30.0) if z > 33 else np.concatenate([np.array([-9, 9, 40, 80]) + c for c in H.RIDGE_AZ])
            p = H.point(az, z)
            pts += [(p[0][i] * K, p[1][i] * K, (z - O) * K) for i in range(len(az))]
        P.hull_collider('col_body', pts)


def nose_window(P, glass, frame):
    """Geodesic nose window: an equilateral lattice laid on the skin inside a half-ellipse, as in SpaceX's renders."""
    s0, s1 = H.arc(45.55), H.arc(48.65)
    ha = 2.75                      # half-width of the lower edge along the skin
    A = lambda z: float(H.body_r(z))

    def inside(x, s):
        t = (s - s0) / (s1 - s0)
        return 0 <= t <= 1 and abs(x) <= ha * math.sqrt(max(0, 1 - t ** 2.1))

    def P3(x, s, off):
        z = float(H.arc_inv(s)); r = max(A(z), .35)
        return (Vector(H.point(math.degrees(x / r), z, off)) - Vector((0, 0, O))) * K

    def nrm(x, s):
        e = .03
        a = (P3(x + e, s, 0) - P3(x - e, s, 0)).cross(P3(x, s + e, 0) - P3(x, s - e, 0))
        return a.normalized()

    # glass: a fine grid inside the outline
    g = Geo(); nx, ns = 26, 18; ids = {}
    for j in range(ns + 1):
        s = s0 + (s1 - s0) * j / ns * .998
        w = ha * math.sqrt(max(1e-4, 1 - ((s - s0) / (s1 - s0)) ** 2.1))
        for i in range(nx + 1):
            x = -w + 2 * w * i / nx
            ids[(i, j)] = (len(g.v), x / ha, (s - s0) / (s1 - s0)); g.v.append(tuple(P3(x, s, .012)))
    for j in range(ns):
        for i in range(nx):
            q = [ids[(i, j)], ids[(i + 1, j)], ids[(i + 1, j + 1)], ids[(i, j + 1)]]
            g.face([t[0] for t in q], [(.02 + (t[1] * .5 + .5) * .46, .52 + t[2] * .46) for t in q])
    glass.add(g)

    def beam(pts, w, h):
        """Flat-topped rib along a polyline on the skin."""
        g = Geo(); rows = []
        for i, (x, s) in enumerate(pts):
            x0, sa = pts[max(0, i - 1)]; x1, sb = pts[min(len(pts) - 1, i + 1)]
            d = (P3(x1, sb, 0) - P3(x0, sa, 0)).normalized(); n = nrm(x, s); side = d.cross(n).normalized()
            p = P3(x, s, 0)
            row = []
            for u, v in ((-w, -.005), (-w * .7, h), (w * .7, h), (w, -.005)):
                row.append(len(g.v)); g.v.append(tuple(p + side * u + n * v))
            rows.append(row)
        for a, b in zip(rows, rows[1:]):
            for k in range(3):
                g.face([a[k], b[k], b[k + 1], a[k + 1]][::-1], [Z.black.uv(.1, .1), Z.black.uv(.1, .4), Z.black.uv(.4, .4), Z.black.uv(.4, .1)])
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
    side = .78; hgt = side * math.sqrt(3) / 2
    for j in range(-1, 8):
        for i in range(-8, 9):
            a = ((i + .5 * (j % 2)) * side, s0 + j * hgt)
            for dx, dj in ((side, 0), (side / 2, hgt), (-side / 2, hgt)):
                c = clip(a, (a[0] + dx, a[1] + dj))
                if c and math.dist(*c) > .05:
                    (x0, t0), (x1, t1) = c
                    frame.add(beam([(x0 + (x1 - x0) * k / 2, t0 + (t1 - t0) * k / 2) for k in range(3)], .026, .03))
    rim = []
    for k in range(49):
        th = math.pi * k / 48
        rim.append((ha * math.cos(th), s0 + (s1 - s0) * math.sin(th) ** (2 / 2.1) * .999))
    frame.add(beam(rim, .06, .042)); frame.add(beam([(ha - 2 * ha * k / 24, s0) for k in range(25)], .06, .042))


ROWS = ((44.55, 7, 60, .74, .50), (41.95, 10, 64, .74, .56), (39.35, 16, 66, .50, .42), (36.55, 18, 70, .48, .40))


def windows(P, glass, frame):
    for z, n, span, w, h in ROWS:
        for i in range(n):
            az = -span + 2 * span * i / (n - 1)
            ww, hh = w * K, h * K
            frame.add(stick(rounded_rect_ring(ww + .07, hh + .07, hh * .42, .038, .022, 4, zone=Z.white), az, z, O))
            m = 4; g = Geo(); rad = hh * .36; c = len(g.v); g.v.append((0, 0, .008)); pts = []
            for cx, cy, a0 in ((ww / 2 - rad, hh / 2 - rad, 0), (-ww / 2 + rad, hh / 2 - rad, 90), (-ww / 2 + rad, -hh / 2 + rad, 180), (ww / 2 - rad, -hh / 2 + rad, 270)):
                for k in range(m + 1):
                    t = math.radians(a0 + 90 * k / m); pts.append((cx + rad * math.cos(t), cy + rad * math.sin(t)))
            for p in pts:
                g.v.append((p[0], p[1], .008))
            # each pane takes one of eight cells, so lit and dark rooms differ
            cell = (i * 7 + int(z * 3)) % 8
            uv = lambda p: ((cell % 4 + .5 + p[0] / ww * .9) / 8 + .5, (cell // 4 + .5 + p[1] / hh * .9) / 4 + .5)
            for k in range(len(pts)):
                k2 = (k + 1) % len(pts)
                g.face([c, c + 1 + k, c + 1 + k2], [uv((0, 0)), uv(pts[k]), uv(pts[k2])])
            glass.add(stick(g, az, z, O, 9, sink=-.008))

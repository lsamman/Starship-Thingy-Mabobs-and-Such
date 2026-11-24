# shared by the crew access arm and the ship quick disconnect arm (executed in their namespace)
def section(c, along, w, z0, z1):
    """Four corners of a box section at point c, across the horizontal direction 'along'."""
    s = V((-along.y, along.x, 0)).normalized() * (w / 2); return [c - s + V((0, 0, z0)), c + s + V((0, 0, z0)), c + s + V((0, 0, z1)), c - s + V((0, 0, z1))]


def space_truss(g, A, B, n, r, web=.6, zone=None):
    """Tubular box truss between two four-corner sections."""
    zone = zone or Z.dark; lerp = lambda t: [a.lerp(b, t) for a, b in zip(A, B)]
    for a, b in zip(A, B): g.add(tube([tuple(a), tuple(b)], r, 10, zone=zone))
    rows = [lerp(k / n) for k in range(n + 1)]
    for k, q in enumerate(rows):
        for i in range(4): g.add(tube([tuple(q[i]), tuple(q[(i + 1) % 4])], r * web, 8, zone=zone))
        if k:
            p = rows[k - 1]
            for i in range(4): a, b = (p[i], q[(i + 1) % 4]) if (k + i) % 2 else (p[(i + 1) % 4], q[i]); g.add(tube([tuple(a), tuple(b)], r * web * .85, 6, zone=zone))


def deck(g, c0, c1, w, z, zone=None, t=.05, rail=None):
    d = (c1 - c0); d.z = 0; L_ = d.length; F = Matrix.Translation((c0 + c1) / 2 + V((0, 0, z))) @ Matrix.Rotation(math.atan2(d.y, d.x), 4, 'Z'); g.add(box(L_, w, t, zone=zone or Z.deck), F)
    for s in (-1, 1) if rail else ():
        for zz in (rail * .55, rail): g.add(tube([tuple(F @ V((-L_ / 2, s * w / 2, zz))), tuple(F @ V((L_ / 2, s * w / 2, zz)))], .022, 6, zone=Z.white))
        for x in np.linspace(-L_ / 2, L_ / 2, max(2, int(L_ / 1.5) + 1)): g.add(tube([tuple(F @ V((float(x), s * w / 2, 0))), tuple(F @ V((float(x), s * w / 2, rail)))], .018, 6, zone=Z.white))
    return F


def hinge(N, H, zs, w=1.0):
    """Column plates, gusseted arms and pins out to the hinge line."""
    b = Geo(); yaw = math.degrees(math.atan2(N.y, N.x)); NF = Rz(yaw); z0, z1 = min(zs), max(zs)
    b.add(box(.18, w, z1 - z0 + 1.4, zone=Z.dark, bevel=.02), NF @ T(.09, 0, (z0 + z1) / 2))
    for s in (-1, 1): b.add(box(.5, .12, z1 - z0 + 1.0, zone=Z.dark, bevel=.02), NF @ T(.05, s * w * .52, (z0 + z1) / 2))
    for z in zs:
        for s in (-1, 1): b.add(tube([tuple(NF @ V((.1, s * w * .42, z + .5))), (H.x, H.y, z)], .13, 10, zone=Z.dark)); b.add(tube([tuple(NF @ V((.1, s * w * .42, z - .5))), (H.x, H.y, z)], .13, 10, zone=Z.dark))
        b.add(cyl(.34, .30, 24, zone=Z.alu, bevel=.03), T(H.x, H.y, z))
        for s in (-1, 1): [b.add(cyl(.05, .06, 8, zone=Z.steel), NF @ T(.20, s * w * .36, z + q) @ Ry(90)) for q in (-.7, .7)]
    b.add(tube([(H.x, H.y, z0 - .3), (H.x, H.y, z1 + .3)], .17, 16, zone=Z.steel))
    P.mesh('hinge', b, P.det); P.hull_collider('col_hinge', [tuple(NF @ V((x, y, z))) for x in (0, .2) for y in (-w / 2, w / 2) for z in (z0 - .7, z1 + .7)] + [(H.x, H.y, z) for z in (z0, z1)])


def seg_collider(nm, A, B, parent): P.hull_collider(nm, [tuple(p) for p in A + B], parent=parent)

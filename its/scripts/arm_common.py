# shared by the crew access arm and the quick disconnect arm (executed in their namespace)
def truss(g, x0, x1, w, z0, z1, r, n, zone=None):
    zone = zone or Z.dark; xs = np.linspace(x0, x1, n + 1)
    for s in (-1, 1):
        for z in (z0 - .06, z1 + .06): g.add(tube([(x0, s * w / 2, z), (x1, s * w / 2, z)], r, 8, zone=zone))
        for i, x in enumerate(xs):
            g.add(tube([(float(x), s * w / 2, z0 - .06), (float(x), s * w / 2, z1 + .06)], r * .7, 8, zone=zone))
            if i < n: g.add(tube([(float(x), s * w / 2, z0 - .06 if i % 2 else z1 + .06), (float(xs[i + 1]), s * w / 2, z1 + .06 if i % 2 else z0 - .06)], r * .6, 6, zone=zone))
    for i, x in enumerate(xs):
        for z in (z0 - .10, z1 + .10): g.add(tube([(float(x), -w / 2, z), (float(x), w / 2, z)], r * .7, 8, zone=zone))
        if i < n: g.add(tube([(float(x), -w / 2, z0 - .10), (float(xs[i + 1]), w / 2, z0 - .10)], r * .5, 6, zone=zone))


def bracket(rot, Hw, z0, z1):
    """Column clamp and the hinge the arm hangs on."""
    R_ = Rz(rot); H = R_.inverted() @ Hw; b = Geo(); zm = (z0 + z1) / 2          # built facing -x, then turned
    b.add(box(.16, 1.0, z1 - z0 + .8, zone=Z.dark, bevel=.02, center=(-.08, 0, zm)))
    for z in (z0, z1):
        b.add(box(H.length + .1, .34, .16, zone=Z.grey, bevel=.02), T(H.x / 2, H.y / 2, z) @ Rz(math.degrees(math.atan2(H.y, H.x))))
        b.add(cyl(.30, .22, 24, zone=Z.alu, bevel=.02), T(H.x, H.y, z))
        for y in (-.36, .36): b.add(cyl(.05, .06, 8, zone=Z.steel), T(-.17, y, z) @ Ry(90))
    b.add(tube([(H.x, H.y, z0 - .2), (H.x, H.y, z1 + .2)], .14, 16, zone=Z.steel))
    b.add(tube([(-.1, 0, z0 - .3), (H.x, H.y, zm)], .07, 8, zone=Z.dark)); b.add(tube([(-.1, 0, z1 + .3), (H.x, H.y, zm)], .07, 8, zone=Z.dark)); b.add(box(.5, .5, .7, zone=Z.white, bevel=.03, center=(-.38, .22, z0 + .5)))
    P.mesh('bracket', Geo().add(b, R_), P.det); P.hull_collider('col_bracket', [tuple(R_ @ V((x, y, z))) for x in (0, H.x) for y in (-.5, .5) for z in (z0 - .3, z1 + .3)])

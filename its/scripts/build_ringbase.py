"""Colliders for the engine rings: the rings show SEP's engines, but forty-two sets of engine colliders are far too many.
Three files; each has the colliders and one small mount ring hidden against the thrust plate."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
for nm, (cnt, r, a0) in L.RINGS.items():
    P = start(nm + 'Base')
    R0, R1 = {'ITS_Ring21': (2.62, 3.70), 'ITS_Ring14': (1.72, 2.60), 'ITS_Ring7': (0, 1.55)}[nm]
    n = {'ITS_Ring21': 8, 'ITS_Ring14': 6, 'ITS_Ring7': 1}[nm]
    if n == 1:
        P.hull_collider('col_ring', [tuple(on_cyl(a, z, R1 * k).translation) for a in range(0, 360, 30) for z, k in ((0, .6), (-L.R3_TOP, 1))])
    else:
        for i in range(n):
            P.hull_collider(f'col_ring{i}', [tuple(on_cyl(360 / n * (i + t), z, rr).translation) for t in (0, .5, 1) for rr in (R0, R1 - (.12 if z0 else 0)) for z0, z in ((1, -.1), (0, -L.R3_TOP))] if False else
                            [tuple(on_cyl(360 / n * (i + t), z, rr).translation) for t in (0, .5, 1) for rr in (R0, R1) for z in (-.1, -L.R3_TOP)])
    P.mesh('mount', ring(max(R0, .3), max(R0, .3) + .08, -.03, 0, Z.carbon, 24), P.det)
    finish(P)

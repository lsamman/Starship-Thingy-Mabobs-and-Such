"""Crane hoist: two winches under the boom's crossbeam; a piston lowers the cables. Origin is the top node."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crane import *
P = start('ITS_CargoHoist'); RX = L.CR_RAIL_X
TOP = L.CR_Z['beam'][0]; CT = L.CR_CABLE - TOP; AP = L.CR_DECK + L.CR_APEX - TOP       # own frame
f = Geo(); bar(f, -RX, RX, -.07, .07, -.13, 0, Z.white)
for s in (-1, 1):
    x = s * RX; bar(f, x - .26, x + .26, -.22, .22, -.06, 0, Z.white)
    for q in (-1, 1):
        bar(f, x + q * .24 - .022, x + q * .24 + .022, -.19, .19, CT, -.06, Z.dark)
        f.add(cyl(.17, .025, 24, zone=Z.alu, bevel=.005), T(x + q * .20, 0, -.21) @ Ry(90))
    f.add(cyl(.12, .39, 24, zone=Z.cable), T(x, 0, -.21) @ Ry(90))
    f.add(cyl(.09, .20, 18, zone=Z.grey, bevel=.012), T(x - s * .36, 0, -.21) @ Ry(90))
    bar(f, x - .14, x + .14, -.06, .06, CT, CT + .05, Z.white)
P.mesh('winches', f, P.det, smooth_angle=45)
P.hull_collider('col_winches', [(x, y, z) for x in (-RX - .26, RX + .26) for y in (-.22, .22) for z in (CT, 0)])
sk = Geo(); w = []
for s in (-1, 1):
    x = s * RX
    for q in (-1, 1):
        top, bot = V((x + q * .06, 0, CT)), V((x + q * .06, 0, AP)); n = len(sk.v); sk.add(tube([top, bot], .016, 6, zone=Z.cable))
        w.extend(0.0 if (V(p) - top).length < (V(p) - bot).length else 1.0 for p in sk.v[n:])
    g = box(.24, .12, .16, zone=Z.dark, bevel=.015); n = len(sk.v); sk.add(g, T(x, 0, AP + .03)); w.extend([1.0] * (len(sk.v) - n))
rig('hoist', P, P.det, 'CableAnchor', 'HoistServo', (0, .2, 0), (0, 0, 0), sk, w, (0, 0, AP - L.CR_HOIST - .2))
P.node('top', (0, 0, 0), (0, 0, 1), 3); P.node('platform', (0, 0, AP), (0, 0, -1), 3)
finish(P)

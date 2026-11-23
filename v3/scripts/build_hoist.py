"""Hoist: two winch housings on the boom's crossbeam, with a piston lowering the cables. Origin is the top node."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

out = sys.argv[sys.argv.index('--') + 1]
P, M, Zn = start('SEP_CW_Hoist')
FR, DK, CB, BR = Zn['FRAME'], Zn['DARK'], Zn['CABLE'], Zn['BRIGHT']
Y, TOP = L.CENTRE_Y, L.HOIST_TOP_Z
fixed = Geo()
bar(fixed, -L.RAIL_X, L.RAIL_X, Y - .06, Y + .06, TOP - .12, TOP, FR)
for s in (-1, 1):
    x = s * L.RAIL_X
    bar(fixed, x - .24, x + .24, Y - .20, Y + .20, TOP - .06, TOP, FR)      # saddle
    for q in (-1, 1):
        bar(fixed, x + q * .22 - .02, x + q * .22 + .02, Y - .18, Y + .18, L.CABLE_TOP_Z, TOP - .06, DK)
    fixed.add(cyl(.13, .40, 24, zone=DK, bevel=.01), T(x, Y, TOP - .20) @ Ry(90))
    fixed.add(cyl(.12, .405, 24, zone=BR), T(x, Y, TOP - .20) @ Ry(90))      # wound cable
    bar(fixed, x - .13, x + .13, Y - .05, Y + .05, L.CABLE_TOP_Z, L.CABLE_TOP_Z + .05, FR)
P.mesh('winches', fixed, M, smooth_angle=50)
P.hull_collider('col_winches', [V((x, y, z)) for x in (-L.RAIL_X - .24, L.RAIL_X + .24) for y in (Y - .2, Y + .2) for z in (L.CABLE_TOP_Z, TOP)])

skin = Geo(); w = []
for s in (-1, 1):
    x = s * L.RAIL_X
    for q in (-1, 1):
        top, bot = V((x + q * .05, Y, L.CABLE_TOP_Z)), V((x + q * .05, Y, L.APEX_Z))
        g = tube([top, bot], .014, 6, zone=CB); n = len(skin.v); skin.add(g)
        w.extend(0.0 if (V(p) - top).length < (V(p) - bot).length else 1.0 for p in skin.v[n:])
    g = box(.20, .10, .14, zone=DK, bevel=.012); n = len(skin.v); skin.add(g, T(x, Y, L.APEX_Z + .02)); w.extend([1.0] * (len(skin.v) - n))
far = (0, Y, L.APEX_Z - L.HOIST_TRAVEL - .2)
rig('hoist', P, M, 'CableAnchor', 'HoistServo', (0, Y, TOP), (0, Y, L.APEX_Z), skin, w, far)
P.model.location = -V((0, Y, TOP))
P.export(out); P.save_blend(out)

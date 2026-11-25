"""Boom: fixed rails on the bay ceiling, and a two-stage slide carrying the crossbeam out through the door.
usage: blender -b -P build_boom.py -- outdir. Origin is the ceiling node."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

out = sys.argv[sys.argv.index('--') + 1]
P, M, Zn = start('SEP_CW_Boom')
FR, DK, BR = Zn['FRAME'], Zn['DARK'], Zn['BRIGHT']
O = V((0, 0, L.CEILING_Z))
fixed = Geo()
# mount: flange on the node, spine, two ties across the rails
fixed.add(cyl(.34, .05, 32, zone=DK, bevel=.008), T(0, 0, L.CEILING_Z - .025))
fixed.add(cyl(.20, L.CEILING_Z - .05 - L.TIE_Z[1], 24, zone=FR), T(0, 0, (L.CEILING_Z - .05 + L.TIE_Z[1]) / 2))
bar(fixed, -.08, .08, -1.30, 1.25, L.TIE_Z[0], L.TIE_Z[1], FR)
for y in (-1.30, 1.25):
    bar(fixed, -L.RAIL_X - .12, L.RAIL_X + .12, y - .07, y + .07, L.TIE_Z[0], L.TIE_Z[1], FR)
for s in (-1, 1):
    channel(fixed, s * L.RAIL_X, .24, *L.RAIL_Y, *L.RAIL_Z, FR)
    bar(fixed, s * L.RAIL_X - .15, s * L.RAIL_X + .15, L.RAIL_Y[0] - .012, L.RAIL_Y[0], L.RAIL_Z[0], L.RAIL_Z[1], DK, bevel=.003)
P.mesh('rails', fixed, M, smooth_angle=50)
P.hull_collider('col_mount', [V((x, y, z)) for x in (-L.RAIL_X - .12, L.RAIL_X + .12) for y in (-1.37, 1.32) for z in (L.TIE_Z[0], L.TIE_Z[1])] + [V((x, y, L.CEILING_Z)) for x in (-.34, .34) for y in (-.34, .34)])
for s in (-1, 1):
    P.hull_collider(f'col_rail{s + 1}', [V((s * L.RAIL_X + a * .12, y, z)) for a in (-1, 1) for y in L.RAIL_Y for z in L.RAIL_Z])

skin = Geo(); w = []


def add(g, share):
    n = len(skin.v); skin.add(g); w.extend([share] * (len(skin.v) - n))


for s in (-1, 1):
    g = Geo(); channel(g, s * L.RAIL_X, .17, *L.MID_Y, L.RAIL_Z[0] + .02, L.RAIL_Z[1] - .02, BR); add(g, L.MID_SHARE)
    g = Geo()
    bar(g, s * L.RAIL_X - .05, s * L.RAIL_X + .05, *L.ARM_Y, L.RAIL_Z[0] + .05, L.RAIL_Z[1] - .05, FR)
    bar(g, s * L.RAIL_X - .03, s * L.RAIL_X + .03, L.CENTRE_Y - .08, L.CENTRE_Y + .08, L.BEAM_Z[1] - .02, L.RAIL_Z[0] + .07, DK)
    add(g, 1.0)
g = Geo(); bar(g, -L.RAIL_X - .1, L.RAIL_X + .1, L.CENTRE_Y - .11, L.CENTRE_Y + .11, *L.BEAM_Z, FR); add(g, 1.0)
far = (0, L.CENTRE_Y - L.BOOM_TRAVEL - .2, L.BEAM_Z[0])
rig('boom', P, M, 'BoomAnchor', 'BoomServo', (0, .2, L.CEILING_Z), (0, 0, L.CEILING_Z), skin, w, far)      # the servo at the part's origin
P.model.location = -O
P.export(out); P.save_blend(out)

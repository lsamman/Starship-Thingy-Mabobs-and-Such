"""Crane boom: ceiling rails and a two-stage slide that carries the crossbeam out through the doors."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crane import *
P = start('ITS_CargoBoom')
RX, RY, RZ, TZ, BZ = L.CR_RAIL_X, L.CR_RAIL_Y, L.CR_Z['rail'], L.CR_Z['tie'], L.CR_Z['beam']
f = Geo()
f.add(cyl(.36, .05, 32, zone=Z.steel, bevel=.01), T(0, 0, -.025)); f.add(bolts(12, .31, .018), T(0, 0, -.05) @ Rx(180))
bar(f, -.10, .10, RY[0] + .5, RY[1] - .5, *TZ, Z.white)
for y in (RY[0] + .7, -.2, RY[1] - .6):
    bar(f, -RX - .13, RX + .13, y - .08, y + .08, *TZ, Z.white)
    for s in (-1, 1):
        f.add(strut((s * .12, y, TZ[0] + .05), (s * RX, y + .45, RZ[1] + .02), .03, Z.grey))
for s in (-1, 1):
    channel(f, s * RX, .26, *RY, *RZ, Z.white)
    bar(f, s * RX - .16, s * RX + .16, RY[0] - .014, RY[0], *RZ, Z.dark, .004); bar(f, s * RX - .16, s * RX + .16, RY[1], RY[1] + .014, *RZ, Z.dark, .004)
    f.add(box(.20, .40, .16, zone=Z.grey, bevel=.02), T(s * (RX + .22), RY[1] - .4, RZ[0] + .08))       # drive motors
    f.add(cyl(.07, .34, 16, zone=Z.dark, bevel=.01), T(s * (RX + .22), RY[1] - .75, RZ[0] + .08) @ Rx(90))
    f.add(tube([(s * .3, -.1, -.06), (s * .5, .4, -.06), (s * (RX - .1), RY[1] - .5, -.10), (s * (RX + .2), RY[1] - .3, RZ[0] + .16)], .02, 6, zone=Z.rubber))
P.mesh('rails', f, P.det, smooth_angle=50)
P.hull_collider('col_mount', [(x, y, z) for x in (-RX - .12, RX + .12) for y in (RY[0] + .6, RY[1] - .5) for z in TZ])
for s in (-1, 1):
    P.hull_collider(f'col_rail{s + 1}', [(s * RX + a * .13, y, z) for a in (-1, 1) for y in RY for z in RZ])
skin_ = Geo(); w = []
def add(g, share):
    n = len(skin_.v); skin_.add(g); w.extend([share] * (len(skin_.v) - n))
for s in (-1, 1):
    g = Geo(); channel(g, s * RX, .18, *L.CR_MID_Y, RZ[0] + .022, RZ[1] - .022, Z.alu)
    for y in np.arange(L.CR_MID_Y[0] + .2, L.CR_MID_Y[1], .6):
        bar(g, s * RX - .094, s * RX + .094, y - .02, y + .02, RZ[0] + .02, RZ[1] - .03, Z.dark, .004)
    add(g, L.CR_SHARE)
    g = Geo(); bar(g, s * RX - .055, s * RX + .055, *L.CR_ARM_Y, RZ[0] + .05, RZ[1] - .05, Z.steel)
    bar(g, s * RX - .035, s * RX + .035, L.CR_C - .09, L.CR_C + .09, BZ[1] - .02, RZ[0] + .08, Z.dark)
    add(g, 1.0)
g = Geo(); bar(g, -RX - .12, RX + .12, L.CR_C - .12, L.CR_C + .12, *BZ, Z.white)
bar(g, -RX, RX, L.CR_C - .125, L.CR_C + .125, BZ[0] + .05, BZ[0] + .09, Z.stripe, .003); add(g, 1.0)
rig('boom', P, P.det, 'BoomAnchor', 'BoomServo', (0, .2, 0), (0, 0, 0), skin_, w, (0, L.CR_C - L.CR_TRAVEL - .2, BZ[0]))
P.node('top', (0, 0, 0), (0, 0, 1), 3); P.node('hoist', (0, L.CR_C, BZ[0]), (0, 0, -1), 3)
finish(P)

"""Tanker forward section: closed nose over extra tankage, transfer plates on both flanks."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fwd import *
P = start('ITS_FwdTanker'); M = materials(P)
P.mesh('hull', skin(H.Z_SPLIT, H.Z_TIP, 'fwd', O), M, smooth_angle=32)
det = Geo(); joint(P, det); det.add(ports(P, RCS))
for s in (1, -1):
    h = Geo()                                       # propellant transfer panel with two couplings and guide pins
    h.add(rounded_rect_ring(1.7, 1.2, .14, .06, .03, 5, zone=Z.white))
    h.add(box(1.55, 1.05, .04, zone=Z.grey, bevel=.015))
    for x in (-.40, .40):
        h.add(lathe([(0, .02), (.20, .02), (.24, .05), (.24, .09), (.20, .11), (.17, .07), (0, .06)], 28, zone=Z.steel), T(x, .06, 0))
        h.add(bolts(10, .22, .014), T(x, .06, .09))
    for x, y in ((0, .38), (0, -.30), (-.66, -.38), (.66, -.38)):
        h.add(cyl(.05, .12, 12, zone=Z.alu, bevel=.015, center_z=False), T(x, y, .02))
    for x in (-.5, -.25, 0, .25, .5):
        h.add(cyl(.028, .05, 8, zone=Z.copper, center_z=False), T(x, -.40, .02))
    det.add(stick(h, s * 60, 29.6, O))
    for z in (33.2, 37.4):                          # inspection covers
        h = Geo(); h.add(rounded_rect_ring(.72, .72, .10, .04, .016, 4, zone=Z.white))
        h.add(bolts(16, .30, .012)); det.add(stick(h, s * 46, z, O))
    f = surf(s * 34, 44.6, O)                       # navigation sensors
    det.add(lathe([(0, .05), (.16, .05), (.20, .02), (.22, -.01)][::-1], 20, zone=Z.black), f); det.add(cyl(.10, .06, 18, zone=Z.lamp, center_z=False), f @ T(0, 0, .02))
P.mesh('detail', det, P.det); colliders(P)
P.node('bottom', (0, 0, Z0), (0, 0, -1), 6)
finish(P)

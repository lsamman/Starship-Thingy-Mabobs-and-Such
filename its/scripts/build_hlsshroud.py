"""Jettisonable shroud over a stowed HLS leg. Origin on the hull at the leg's own height, -Y outboard."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_LegShroud'); OFFS = T(0, HL.R, -HL.HINGE[1]); zs = [.26, .30, .36, .46, .62, .8, 1.1, 1.5, 2.0, 2.6, 3.2, 3.7, 4.2, 4.5, 4.75, 4.9, 5.05, 5.2, 5.33, 5.45, 5.5]
for nm, zn in (('shroud_black', Z.black), ('shroud_white', Z.white)): P.mesh(nm, Geo().add(blister(zs, zn), OFFS), P.det, smooth_angle=50)
g = Geo().add(recolor(blister(zs[1:-1], Z.grey, inner=.045, flip=True), Z.grey), OFFS)
for z in (.9, 1.9, 2.9, 3.9):
    h = float(np.interp(z, *zip(*HL.SHELL))); w = float(np.interp(z, *zip(*HL.SHELL_W))); g.add(tube([tuple(OFFS @ V((x, -math.sqrt(HL.R ** 2 - x * x) - (h - .06) * max(0, 1 - abs(x / w) ** 3) ** .6, z))) for x in np.linspace(-w * .9, w * .9, 11)], .025, 6, zone=Z.alu))
P.mesh('inside', g, P.det, smooth_angle=50)
P.hull_collider('col', [tuple(OFFS @ V((x, -math.sqrt(HL.R ** 2 - x * x) - h * k, z))) for x, k in ((-1.0, .1), (-.6, .8), (.6, .8), (1.0, .1)) for z, h in ((.5, .6), (1.4, .72), (4.2, .46), (4.8, .1))])
P.node('mount', (0, 0, 0), (0, 1, 0), 1)
finish(P, ({'shroud_black'}, {'shroud_white'}))

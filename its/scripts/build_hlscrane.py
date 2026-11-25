"""Crane frame for the awning-door cargo section: a level crossbar on a robotic piston, carried by two telescoping legs that FXModuleLookAtConstraint
keeps pointed at each other, so it leans out like the frame in SpaceX's render and the winch under it stays upright. Origin on the bay floor
between the pivots, -Y outboard, +Z up. Authored in."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Crane'); X, ZF, ZT = HL.CR_X, HL.CR_FOOT, HL.CR_BAR; YB = HL.CR_IN - HL.CR_Y
g = Geo()                                                # KSP takes the anchor's and servo's places from the part's origin: both sit there
for s in (-1, 1): g.add(box(.22, .40, .05, zone=Z.grey, bevel=.012), T(s * X, 0, .025)); [g.add(box(.03, .20, ZF, zone=Z.grey, bevel=.008), T(s * X + q * .10, 0, ZF / 2 + .03)) for q in (-1, 1)]; g.add(cyl(.05, .28, 16, zone=Z.steel, bevel=.008), T(s * X, 0, ZF) @ Ry(90))
g.add(box(2 * X, .16, .05, zone=Z.grey, bevel=.012), T(0, 0, .025)); P.mesh('CraneAnchor', g, P.det)
hold = P.empty('craneRest', None, P.model); servo = P.empty('CraneServo', None, hold)
b = Geo(); b.add(box(2 * X + .16, .15, .16, zone=Z.grey, bevel=.02), T(0, YB, ZT))
for x in (-1.0, 1.0): b.add(box(.20, .22, .20, zone=Z.alu, bevel=.02), T(x, YB, ZT)); [b.add(cyl(.085, .05, 18, zone=Z.steel, bevel=.008), T(x, YB + q * .12, ZT) @ Rx(90)) for q in (-1, 1)]
b.add(box(.62, .20, .05, zone=Z.alu, bevel=.012), T(0, YB, ZT - .10)); P.mesh('cranebar', b, P.det, parent=servo)
for s, k in ((-1, 'L'), (1, 'R')):
    ft, tp = V((s * X, 0, ZF)), V((s * X, YB, ZT)); u = (tp - ft).normalized(); ln = (tp - ft).length
    P.empty('craneFoot' + k, T(*ft), P.model); P.empty('craneTip' + k, T(*tp), servo)
    # a rotator looks along Unity's forward, which is local +Y here
    fl = frame_axes(ft, V((1, 0, 0)).cross(u), x=V((1, 0, 0))); fu = frame_axes(tp, V((1, 0, 0)).cross(-u), x=V((1, 0, 0)))
    assert ((fl.to_3x3() @ V((0, 1, 0))) - u).length < 1e-4 and ((fu.to_3x3() @ V((0, 1, 0))) + u).length < 1e-4
    lo = P.empty('craneLow' + k, fl, P.model); hi = P.empty('craneTop' + k, fu, servo)
    a = Geo(); a.add(tube([ft, ft + u * (ln - .42)], .065, 16, zone=Z.grey)); a.add(tube([ft + u * (ln - .54), ft + u * (ln - .40)], .085, 16, zone=Z.alu)); a.add(tube([ft - u * .02, ft + u * .20], .085, 16, zone=Z.alu)); P.mesh('craneLowMesh' + k, a, P.det, parent=lo, frame=fl)
    c = Geo(); c.add(tube([tp - u * (ln - .9), tp], .048, 14, zone=Z.alu)); c.add(tube([tp - u * .16, tp], .075, 14, zone=Z.alu)); P.mesh('craneTopMesh' + k, c, P.det, parent=hi, frame=fu)
P.hull_collider('col_foot', [(x, y, z) for x in (-X - .1, X + .1) for y in (-.1, .1) for z in (0, .05)])
P.hull_collider('col_bar', [(x, YB + y, ZT + z) for x in (-X, X) for y in (-.08, .08) for z in (-.08, .08)], parent=servo)
P.node('mount', (0, 0, 0), (0, 0, -1), 2); P.node('hoist', (0, YB, ZT - .125), (0, 0, -1), 3)
finish(P)

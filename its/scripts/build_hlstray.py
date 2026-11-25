"""Sliding tray: carries a load without wheels from a lowered floor out over the winch platform. Origin under the base, -Y to the door."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Tray'); b = Geo(); YF, YB, XR = -2.0, 1.8, .42; TY = -.9
for s in (-1, 1): b.add(box(.07, YB - YF, .05, zone=Z.grey, bevel=.008), T(s * (XR + .085), (YF + YB) / 2, .04)); b.add(box(.03, YB - YF - .1, .03, zone=Z.steel), T(s * (XR + .04), (YF + YB) / 2, .05)); b.add(box(.16, .20, .08, zone=Z.alu, bevel=.012), T(s * (XR + .06), YF + .12, .05))
for y in (YF + .12, 0, YB - .1): b.add(box(2 * XR + .24, .10, .02, zone=Z.grey, bevel=.005), T(0, y, .010))
for s in (-1, 1):                                        # rollers the carriage runs on, end stops
    for y in np.arange(YF + .2, YB, .4): b.add(cyl(.018, .06, 12, zone=Z.steel), T(s * (XR + .0), float(y), .036) @ Ry(90))
    for y in (YF + .02, YB - .02): b.add(box(.05, .04, .07, zone=Z.rubber, bevel=.006), T(s * (XR + .085), y, .075))
b.add(box(.18, .22, .09, zone=Z.white, bevel=.015), T(.18, YF + .30, .055)); b.add(cyl(.05, .04, 18, zone=Z.dark, bevel=.006), T(.06, YF + .30, .05) @ Ry(90)); b.add(box(.02, YB - YF - .4, .012, zone=Z.rubber), T(.06, (YF + YB) / 2, .022))      # motor, sprocket, chain run
P.mesh('TrayAnchor', b, P.det); hold = P.empty('trayRest', None, P.model); servo = P.empty('TrayServo', None, hold)
c = Geo(); RF, RB = TY - .72, YB + .3
for s in (-1, 1): c.add(box(.06, RB - RF, .055, zone=Z.alu, bevel=.008), T(s * (XR - .02), (RF + RB) / 2, .075))
for y in np.linspace(RF + .1, RB - .1, 5): c.add(box(2 * XR - .05, .06, .03, zone=Z.alu, bevel=.006), T(0, float(y), .08))
c.add(box(1.5, 1.5, .05, zone=Z.white, bevel=.015), T(0, TY, .135)); c.add(box(1.2, 1.2, .006, zone=Z.deck), T(0, TY, .163)); [c.add(box(1.5, .05, .008, zone=Z.stripe), T(0, TY + q * .72, .163)) for q in (-1, 1)]
for q in np.arange(RF + .06, RB - .05, .07): c.add(box(.025, .035, .02, zone=Z.steel), T(.06, float(q), .062))      # rack the sprocket drives
for s in (-1, 1): [c.add(box(.07, .12, .07, zone=Z.dark, bevel=.01), T(s * .62, TY + q, .18)) for q in (-.6, .6)]; [c.add(cyl(.02, .10, 10, zone=Z.steel), T(s * .58, TY + q, .19) @ Ry(90)) for q in (-.6, .6)]      # load latches
c.add(box(.22, .16, .07, zone=Z.dark, bevel=.015), T(0, RB - .2, .10)); P.mesh('traycar', c, P.det, parent=servo)
P.hull_collider('col_base', [(x, y, z) for x in (-.5, .5) for y in (YF, YB) for z in (0, .03)])
P.hull_collider('col_car', [(x, TY + y, z) for x in (-.75, .75) for y in (-.75, .75) for z in (.11, .16)], parent=servo); P.hull_collider('col_rails', [(x, y, z) for x in (-XR, XR) for y in (RF, RB) for z in (.06, .10)], parent=servo)
P.node('mount', (0, 0, 0), (0, 0, -1), 2); P.node('cargo', (0, TY, .166), (0, 0, 1), 2); finish(P)

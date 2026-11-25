"""HLS cable elevator, after the NASA/SpaceX render: an open cage on four cables. Stowed in the airlock; the cageOut clip runs two three-stage
beams and the cage under them out below the raised door, then the piston lowers the cage to the surface. The plugin stretches the cables.
Origin in the airlock at its threshold, -Y outboard, +Z up. Authored out; frame 0 of cageOut is stowed."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_LiftCable'); OUT = 1.20; F = 90; BZ, BX, CZ = 1.185, .42, 1.085
W, DP, UP, YC, TOPZ = .62, .475, .13, -.98, .93                    # cage: half-width, half-depth, deck, centre when out, top ring
def slide(name, parent, d):
    o = P.empty(name, None, parent); l = o.location.copy()
    for f, y in ((0, d), (F, 0)): P.key('cageOut', o, f, location=l + V((0, y, 0)))
    return o
P.mesh('LiftAnchor', box(.5, .03, .05, zone=Z.grey, bevel=.008, center=(0, .9, 1.45)), P.det)
hold = P.empty('liftRest', None, P.model); servo = P.empty('LiftServo', None, hold)
mid, boom, cage = slide('mid', P.model, OUT / 2), slide('boom', P.model, OUT), slide('cage', servo, OUT)
# ---------------- fixed channels under the airlock ceiling
fx = Geo(); mg = Geo(); bg = Geo()
for s in (-1, 1):
    x = s * BX
    for q in (-1, 1): fx.add(box(.014, 1.08, .14, zone=Z.alu, bevel=.004, center=(x + q * .052, .35, BZ)))
    fx.add(box(.118, 1.08, .014, zone=Z.alu, bevel=.004, center=(x, .35, BZ + .077)))
    for y in (-.12, .35, .86): fx.add(box(.09, .07, 1.5 - BZ - .08, zone=Z.white, bevel=.01, center=(x, y, (1.5 + BZ + .08) / 2))); fx.add(box(.20, .13, .02, zone=Z.white, bevel=.005, center=(x, y, 1.488))); [fx.add(cyl(.011, .016, 8, zone=Z.steel), T(x + q * .075, y, 1.474)) for q in (-1, 1)]
    mg.add(box(.074, 1.24, .10, zone=Z.steel, bevel=.006, center=(x, -.26, BZ))); mg.add(box(.094, .05, .12, zone=Z.dark, bevel=.006, center=(x, -.84, BZ)))
    bg.add(box(.048, 1.32, .072, zone=Z.white, bevel=.008, center=(x, -.79, BZ)))
fx.add(box(.70, .24, .20, zone=Z.dark, bevel=.025, center=(0, .72, BZ + .04))); [fx.add(cyl(.09, .10, 20, zone=Z.cable), T(s * .16, .72, BZ + .04) @ Ry(90)) for s in (-1, 1)]; fx.add(box(.60, .05, .08, zone=Z.alu, bevel=.01, center=(0, .86, BZ))); [fx.add(box(.05, .05, .05, zone=Z.alu, center=(s * .355, .72, BZ + .04))) for s in (-1, 1)]
# boom: cross-heads over the cage with a sheave for each cable
for y in (YC - .36, YC + .36):
    bg.add(box(2 * W + .02, .06, .05, zone=Z.white, bevel=.008, center=(0, y, CZ))); [bg.add(box(.03, .05, .07, zone=Z.white, center=(s * BX, y, BZ - .055))) for s in (-1, 1)]
    for s in (-1, 1):
        bg.add(cyl(.052, .030, 20, zone=Z.alu, bevel=.005), T(s * (W - .03), y, CZ - .01) @ Ry(90)); bg.add(cyl(.016, .075, 10, zone=Z.steel), T(s * (W - .03), y, CZ - .01) @ Ry(90)); [bg.add(box(.008, .07, .10, zone=Z.dark, center=(s * (W - .03) + q * .024, y, CZ - .01))) for q in (-1, 1)]
bg.add(box(2 * BX + .1, .05, .06, zone=Z.white, bevel=.008, center=(0, -1.435, BZ))); bg.add(strut((-BX, -1.32, CZ), (BX, -.64, CZ), .012, Z.alu, 8)); bg.add(strut((BX, -1.32, CZ), (-BX, -.64, CZ), .012, Z.alu, 8))
P.mesh('channels', fx, P.det, smooth_angle=40); P.mesh('midmesh', mg, P.det, parent=mid); P.mesh('boommesh', bg, P.det, parent=boom, smooth_angle=40)
# ---------------- cage
g = Geo(); YB_, YF = YC + DP, YC - DP; r = .017
g.add(box(2 * W, 2 * DP, .022, zone=Z.deck, center=(0, YC, UP - .011)))
for y in (YF + .02, YC, YB_ - .02): g.add(box(2 * W, .04, .05, zone=Z.alu, bevel=.008, center=(0, y, UP - .045)))
for s in (-1, 1): g.add(box(.04, 2 * DP, .05, zone=Z.alu, bevel=.008, center=(s * (W - .02), YC, UP - .045)))
g.add(box(2 * W, .04, .010, zone=Z.stripe, center=(0, YF + .02, UP + .004))); g.add(box(2 * W - .3, .05, .010, zone=Z.stripe, center=(0, YB_ - .025, UP + .004)))
X0 = W - .03; post = lambda x, y, z1=TOPZ: g.add(tube([(x, y, UP - .02), (x, y, z1)], r, 8, zone=Z.white))
ys = (YF + .03, YC, YB_ - .03)
for s in (-1, 1):
    for y in ys: post(s * X0, y)
    for z in (TOPZ, UP + .42): g.add(tube([(s * X0, ys[0], z), (s * X0, ys[-1], z)], r, 8, zone=Z.white))
    g.add(strut((s * X0, ys[0], UP + .02), (s * X0, ys[1], UP + .42), .011, Z.white, 6)); g.add(strut((s * X0, ys[2], UP + .02), (s * X0, ys[1], UP + .42), .011, Z.white, 6)); g.add(box(.012, 2 * DP - .06, .10, zone=Z.white, center=(s * X0, YC, UP + .05)))
    # front and back: a fixed panel either side, the middle open; hooped grab rails by the gates
    for y in (ys[0], ys[2]):
        xi = .30; post(s * xi, y, UP + .68); g.add(tube([(s * X0, y, UP + .42), (s * xi, y, UP + .42)], r, 8, zone=Z.white)); g.add(tube([(s * xi, y, UP + .66), (s * (xi + .02), y, UP + .73), (s * (xi + .07), y, UP + .76), (s * X0, y, UP + .76)], r, 8, zone=Z.white)); g.add(strut((s * X0, y, UP + .02), (s * xi, y, UP + .42), .011, Z.white, 6))
    g.add(tube([(s * .27, ys[0] - .0, UP + .06), (s * .27, ys[0] - .02, UP + .62)], .010, 6, zone=Z.copper))
    for y in (YC - .36, YC + .36): g.add(box(.06, .07, .05, zone=Z.dark, bevel=.01, center=(s * X0, y, TOPZ + .02))); g.add(cyl(.02, .07, 10, zone=Z.steel), T(s * X0, y, TOPZ + .045) @ Ry(90))
    for z in (UP - .03, UP + .55): g.add(cyl(.035, .05, 14, zone=Z.rubber, bevel=.008), T(s * .50, YB_ + .02, z) @ Ry(90)); g.add(box(.03, .05, .05, zone=Z.grey, center=(s * .50, YB_ - .015, z)))       # fender rollers toward the hull
g.add(box(.16, .05, .24, zone=Z.dark, bevel=.015, center=(-X0 + .06, YC + .2, UP + .62))); g.add(box(.10, .01, .05, zone=Z.lamp, center=(-X0 + .06, YC + .17, UP + .68)))   # control box
for y in (ys[0], ys[2]): g.add(tube([(-X0, y, TOPZ), (X0, y, TOPZ)], r, 8, zone=Z.white))
P.mesh('cagemesh', g, P.det, parent=cage, smooth_angle=40)
# ---------------- cables: one metre long in the file, stretched by the plugin
k = 0
for s in (-1, 1):
    for y in (YC - .36, YC + .36):
        a, b = V((s * X0, y, CZ - .05)), V((s * X0, y, TOPZ + .045)); t = P.empty(f'cableTop{k}', T(*a), boom); P.empty(f'cableEnd{k}', T(*b), cage)
        P.mesh(f'cable{k}', tube([a, a - V((0, 0, 1))], .009, 6, zone=Z.cable), P.det, parent=t, frame=T(*a)); t.scale = (1, 1, (a - b).length); k += 1
# ---------------- colliders, nodes
P.hull_collider('col_deck', [(x, y, z) for x in (-W, W) for y in (YF, YB_) for z in (UP, UP - .06)], parent=cage)
for s in (-1, 1): P.hull_collider('col_rail%d' % (s > 0), [(s * x, y, z) for x in (W - .05, W - .01) for y in (YF, YB_) for z in (UP, UP + .80)], parent=cage)
P.node('mount', (0, 0, 0), (0, 1, 0), 1); P.node('cargo', (0, YC, UP), (0, 0, 1), 0)
P.bake_clips(0); finish(P)

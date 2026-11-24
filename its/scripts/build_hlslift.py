"""HLS elevator: a carriage in the hull's track with a fold-down deck. The piston runs it from the airlock to the surface.
Origin on the track at the airlock's threshold, -Y outboard, +Z up. Authored with the deck down; frame 0 of deckFold is folded."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Lift'); RR = HL.TRACK_R
Y = lambda r: RR - r                                       # hull radius -> part y
P.mesh('LiftAnchor', box(.5, .03, .05, zone=Z.grey, bevel=.008, center=(0, -.02, -.10)), P.det)
hold = P.empty('liftRest', None, P.model); servo = P.empty('LiftServo', None, hold)
c = Geo()
for s in (-1, 1):
    c.add(box(.05, .05, .98, zone=Z.white, bevel=.01, center=(s * .20, -.135, .40)))
    for z in (0.02, .78): c.add(cyl(.05, .04, 14, zone=Z.rubber, bevel=.008), T(s * .213, -.10, z) @ Ry(90)); c.add(box(.06, .05, .08, zone=Z.steel, center=(s * .19, -.11, z)))
for z in (-.04, .38, .86): c.add(box(.44, .05, .06, zone=Z.white, bevel=.01, center=(0, -.135, z)))
c.add(box(.22, .07, .30, zone=Z.dark, bevel=.015, center=(0, -.12, .62))); c.add(tube([(-.22, -.17, -.02), (.22, -.17, -.02)], .022, 10, zone=Z.steel))
P.mesh('carriage', c, P.det, parent=servo)
HG = V((0, -.17, -.045)); hf = T(*HG); deck = P.empty('deck', hf, servo); DW, DD, ST = 1.46, 1.32, .30       # tongue first: the deck proper starts outside the hull
g = Geo()
for s in (-1, 1): g.add(box(.06, ST + .1, .05, zone=Z.alu, bevel=.01, center=(s * .18, HG.y - ST / 2, -.050)))
g.add(box(.42, ST, .02, zone=Z.deck, center=(0, HG.y - ST / 2, -.028)))
y0, y1 = HG.y - ST, HG.y - ST - DD + .25; yc = (y0 + y1) / 2; dp = y0 - y1
g.add(box(DW, dp, .025, zone=Z.deck, center=(0, yc, -.0125)))
for s in (-1, 1): g.add(box(.05, dp, .07, zone=Z.alu, bevel=.01, center=(s * (DW / 2 - .025), yc, -.045)))
for q in (y0 - .03, yc, y1 + .03): g.add(box(DW, .05, .06, zone=Z.alu, bevel=.01, center=(0, q, -.045)))
g.add(box(DW, .05, .012, zone=Z.stripe, center=(0, y1 + .025, .004)))
for s in (-1, 1):                                          # handrails on both sides, open in front
    x = s * (DW / 2 - .03)
    for q in (y0 - .03, yc, y1 + .06): g.add(tube([(x, q, 0), (x, q, .62)], .018, 8, zone=Z.white))
    for z in (.32, .62): g.add(tube([(x, y0 - .03, z), (x, y1 + .06, z)], .018, 8, zone=Z.white))
P.mesh('deckmesh', g, P.det, parent=deck, frame=hf)
q0 = P.rest_quat(deck); F = 60; fold = Quaternion((1, 0, 0), math.radians(-90))
if (fold @ V((0, -1, 0))).z < 0: fold = Quaternion((1, 0, 0), math.radians(90))
P.key('deckFold', deck, 0, rotation_quaternion=fold); P.key('deckFold', deck, F, rotation_quaternion=q0)
P.hull_collider('col_deck', [(x, y, z) for x in (-DW / 2, DW / 2) for y in (y0, y1) for z in (0, -.07)], parent=deck, frame=hf)
P.hull_collider('col_tongue', [(x, y, z) for x in (-.21, .21) for y in (HG.y, y0) for z in (0, -.05)], parent=deck, frame=hf)
for s in (-1, 1): P.hull_collider('col_rail%d' % (s > 0), [(s * x, y, z) for x in (DW / 2 - .05, DW / 2 - .01) for y in (y0, y1) for z in (0, .64)], parent=deck, frame=hf)
P.node('mount', (0, 0, 0), (0, 1, 0), 1); P.node('cargo', (0, yc, 0), (0, 0, 1), 0)
P.bake_clips(0); finish(P)

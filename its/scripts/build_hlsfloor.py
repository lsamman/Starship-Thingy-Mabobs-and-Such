"""Moving cargo floor for the awning-door cargo section: a deck on a robotic piston between guide columns. Parks over the stowed crane and comes
down onto the bay floor once the load before it has left; the top floor lands on the mid floor. Origin on the bay floor, +Z up, -Y to the door."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
WHICH = globals().get('WHICH', 'Mid'); OY, ZP, ZR, CY, RO = HL.FLOORS[WHICH]; FL = HL.CG_FLOOR; W, DT, (Y0, Y1) = HL.DECK_W, HL.DECK_T, HL.DECK_Y; Y0 = -1.72 if WHICH == 'Top' else Y0
P = start('STMS_HLS_Floor' + WHICH); B = lambda x, y, z: (x, y - OY, z - FL)      # bay frame to part frame
pts = []                                                 # outline: a rectangle clipped to the bay's radius
for k in range(96):
    a = TAU * k / 96; d_ = V((math.sin(a), -math.cos(a))); r = min(RO, W / max(1e-6, abs(d_.x)), (Y1 if d_.y > 0 else -Y0) / max(1e-6, abs(d_.y))); pts.append((d_.x * r, d_.y * r))
g = Geo(); HC = ZP - FL + .04
for s in (-1, 1):
    [g.add(box(.18, .22, .03, zone=Z.grey, bevel=.008), T(*B(s * HL.COL_X, y, FL + .015))) for y in CY]
    for y in CY:
        g.add(box(.09, .10, HC, zone=Z.alu, bevel=.012), T(*B(s * HL.COL_X, y, FL + HC / 2))); g.add(box(.02, .04, HC - .1, zone=Z.steel), T(*B(s * (HL.COL_X - .05), y, FL + HC / 2)))
        for z in np.arange(.5, HC - .2, .9): g.add(box(.05, .12, .05, zone=Z.grey, bevel=.006), T(*B(s * (HL.COL_X + .025), y, FL + float(z))))
    for y in CY:                                         # toothed rack up the inner face, stops, and stays from the column to the hull's hoops
        for z in np.arange(.22, HC - .25, .085): g.add(box(.022, .05, .04, zone=Z.steel), T(*B(s * (HL.COL_X - .068), y, FL + float(z))))
        g.add(box(.07, .13, .06, zone=Z.dark, bevel=.01), T(*B(s * HL.COL_X, y, FL + HC)))
        if WHICH == 'Mid' and y > 1: pass
        for z in ((.6, 2.2, HC - .12)):
            zz = FL + z; xw = math.sqrt(max(.1, (float(np.interp(max(zz, 0), *zip(*HL.OGIVE))) - .16) ** 2 - y * y)); g.add(strut(B(s * (HL.COL_X + .03), y, zz), B(s * xw, y, zz), .024, Z.alu, 8)); g.add(box(.03, .12, .12, zone=Z.alu, bevel=.008), T(*B(s * xw, y, zz)))
for y in CY: g.add(box(2 * HL.COL_X, .10, .03, zone=Z.grey, bevel=.006), T(*B(0, y, FL + .015)))
P.mesh('FloorAnchor', g, P.det)
hold = P.empty('floorRest', None, P.model); servo = P.empty('FloorServo', None, hold)
d = Geo(); top, bot = ZP + DT, ZP
d.add(plate(pts, [], top, Z.deck, up=True), T(0, -OY, -FL)); d.add(plate(pts, [], bot, Z.alu, up=False), T(0, -OY, -FL))
for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
    n = len(d.v); d.v += [B(x0, y0, bot), B(x1, y1, bot), B(x1, y1, top), B(x0, y0, top)]; zn = Z.stripe if (y0 + y1) / 2 < -1.3 else Z.grey; d.face(range(n, n + 4), [zn.uv(*t) for t in ((0, 0), (.1, 0), (.1, .2), (0, .2))])
for s in (-1, 1):
    for y in CY: d.add(box(HL.COL_X - .06 - (W - .12), .16, .09, zone=Z.steel, bevel=.012), T(*B(s * (HL.COL_X - .06 + W - .12) / 2, y, (top + bot) / 2))); [d.add(cyl(.04, .05, 14, zone=Z.rubber, bevel=.006), T(*B(s * (HL.COL_X - .075), y + q * .075, (top + bot) / 2)) @ Ry(90)) for q in (-1, 1)]
    ym = min(1.3, math.sqrt(RO ** 2 - W ** 2)) - .05; d.add(box(.05, 2 * ym, .05, zone=Z.white, bevel=.012), T(*B(s * (W - .05), 0, top + .025)))      # low kerbs
for x in (-.75, .75): d.add(box(.10, 3.0, .006, zone=Z.grey), T(*B(x, -.1, top + .003)))
for s in (-1, 1):                                        # drive: a motor and gearbox under each edge, pinions on the racks, a shaft tying the pair
    zm_ = bot + .045
    for y in CY: d.add(cyl(.055, .06, 18, zone=Z.steel, bevel=.006), T(*B(s * (HL.COL_X - .115), y, zm_)) @ Rx(90)); d.add(cyl(.02, .16, 10, zone=Z.alu), T(*B(s * (HL.COL_X - .115), y, zm_)) @ Rx(90)); d.add(box(.10, .20, .10, zone=Z.dark, bevel=.015), T(*B(s * (HL.COL_X - .185), y, zm_)))
    d.add(tube([B(s * (HL.COL_X - .19), CY[0], zm_), B(s * (HL.COL_X - .19), CY[1], zm_)], .022, 10, zone=Z.steel)); d.add(box(.13, .24, .11, zone=Z.white, bevel=.02), T(*B(s * (HL.COL_X - .20), sum(CY) / 2, zm_)))
    for y in (-1.0, 1.0):                                # latches that lock the deck to the column heads and tie-downs for the load
        for x in (.55, 1.15): d.add(cyl(.045, .012, 14, zone=Z.steel), T(*B(s * x, y, top + .006))); d.add(tube([tuple(V(B(s * x, y, top + .004)) + V((q, 0, zq))) for q, zq in ((-.03, 0), (-.02, .035), (.02, .035), (.03, 0))], .008, 6, zone=Z.alu))
P.mesh('floordeck', d, P.det, parent=servo)
if WHICH == 'Top':                                       # ramped front edge, down to the mid floor it lands on
    w = Geo(); f = [p for p in pts if p[1] < -1.0 and abs(p[0]) < 1.3]; f.sort(); lip = -.17
    for (x0, y0), (x1, y1) in zip(f, f[1:]):
        k0, k1 = [1 + .30 / math.hypot(x, y) for x, y in ((x0, y0), (x1, y1))]; k0, k1 = min(k0, 2.0 / -y0, 2.25 / math.hypot(x0, y0)), min(k1, 2.0 / -y1, 2.25 / math.hypot(x1, y1))
        q = [B(x0, y0, top), B(x0 * k0, y0 * k0, bot), B(x1 * k1, y1 * k1, bot), B(x1, y1, top)]; n = len(w.v); w.v += q; w.face(range(n, n + 4), [Z.stripe.uv(*t) for t in ((0, 0), (0, .2), (.1, .2), (.1, 0))])
    P.mesh('floorlip', w, P.det, parent=servo)
    P.hull_collider('col_lip', [B(x * k, y * k, z) for x, y in f for k, z in ((1, top), (1, bot), (min(1 + .30 / math.hypot(x, y), 2.0 / -y, 2.25 / math.hypot(x, y)), bot))], parent=servo)
half = [p for p in pts]
P.hull_collider('col_deck', [B(x, y, z) for x, y in half[::2] for z in (bot, top)], parent=servo)
for s in (-1, 1): P.hull_collider('col_kerb%d' % (s > 0), [B(s * x, y, z) for x in (W - .075, W - .025) for y in (-ym, ym) for z in (top, top + .05)], parent=servo); [P.hull_collider('col_col%d%d' % (s > 0, k), [B(s * x, y + q, z) for x in (HL.COL_X - .045, HL.COL_X + .045) for q in (-.05, .05) for z in (FL, FL + HC)]) for k, y in enumerate(CY)]
P.node('mount', (0, 0, 0), (0, 0, -1), 2); P.node('cargo', B(0, 0, top), (0, 0, 1), 2)
P.two_sided = True; finish(P)

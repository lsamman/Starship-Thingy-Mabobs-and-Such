"""Crane platform. Origin at the deck centre."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crane import *
P = start('ITS_CargoPlatform'); HW, HD, TH = L.CR_DECK_W / 2, L.CR_DECK_D / 2, .10; RX = L.CR_RAIL_X
d = Geo(); d.add(box(2 * HW, 2 * HD, TH, zone=Z.deck, bevel=.012), T(0, 0, -TH / 2))
P.mesh('deck', d, P.det)
f = Geo()
for y in (-HD + .08, -.42, .42, HD - .08):
    bar(f, -HW, HW, y - .05, y + .05, -TH - .10, -TH, Z.dark)
for y in (-HD + .03, HD - .03):
    bar(f, -HW + .02, HW - .02, y - .03, y + .03, -.02, .012, Z.stripe, .004)
for s in (-1, 1):
    x = s * (HW - .06); bar(f, x - .06, x + .06, -HD, HD, -TH - .10, -TH, Z.dark)
    for y in (-HD + .06, 0, HD - .06):
        bar(f, x - .03, x + .03, y - .03, y + .03, 0, .85, Z.white)
    f.add(tube([(x, -HD + .03, .85), (x, HD - .03, .85)], .032, 10, zone=Z.white))
    for z in (.10, .27, .44, .61):
        bar(f, x - .014, x + .014, -HD + .06, HD - .06, z, z + .08, Z.grey, .003)
    ap = V((s * RX, 0, L.CR_APEX)); bar(f, ap.x - .12, ap.x + .12, -.06, .06, ap.z - .13, ap.z - .05, Z.dark)
    for q in (-1, 1):
        f.add(tube([tuple(ap - V((0, 0, .1))), (x, q * (HD - .06), .85)], .018, 6, zone=Z.cable))
        for z0 in (-TH - .10,):
            f.add(cyl(.09, .05, 14, zone=Z.rubber), T(x, q * (HD - .15), z0 - .02))
P.mesh('frame', f, P.det, smooth_angle=45)
P.hull_collider('col_deck', [(x, y, z) for x in (-HW, HW) for y in (-HD, HD) for z in (0, -TH - .12)])
for s in (-1, 1):
    x = s * (HW - .06); P.hull_collider(f'col_rail{s + 1}', [(x + a * .03, y, z) for a in (-1, 1) for y in (-HD, HD) for z in (0, .87)])
P.node('top', (0, 0, L.CR_APEX), (0, 0, 1), 1); P.node('cargo', (0, 0, 0), (0, 0, 1), 1)
finish(P)

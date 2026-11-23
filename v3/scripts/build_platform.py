"""Platform: what the hoist lowers. Origin at the deck centre, and the deck and colliders move as a normal part."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

out = sys.argv[sys.argv.index('--') + 1]
P, M, Zn = start('SEP_CW_Platform')
FR, DK, DE, CB = Zn['FRAME'], Zn['DARK'], Zn['DECK'], Zn['CABLE']
HW, HD, TH = L.DECK_W / 2, L.DECK_D / 2, .10
deck = Geo(); bar(deck, -HW, HW, -HD, HD, -TH, 0, DE, bevel=.01)
fr = Geo()
for y in (-HD + .08, -.5, .5, HD - .08):
    bar(fr, -HW, HW, y - .05, y + .05, -TH - .09, -TH, DK)
for s in (-1, 1):
    x = s * (HW - .05)
    bar(fr, x - .05, x + .05, -HD, HD, -TH - .09, -TH, DK)
    # side rail and its slatted panel; both ends stay open so a rover can drive off
    for y in (-HD + .05, 0, HD - .05):
        bar(fr, x - .025, x + .025, y - .025, y + .025, 0, .85, FR)
    bar(fr, x - .025, x + .025, -HD + .02, HD - .02, .82, .87, FR)
    for z in (.10, .25, .40, .55):
        bar(fr, x - .012, x + .012, -HD + .05, HD - .05, z, z + .08, DK, bevel=.003)
    # bridles from the apex to the deck corners and the apex block
    apex = V((s * L.RAIL_X, 0, L.APEX_H))
    bar(fr, apex.x - .10, apex.x + .10, -.05, .05, apex.z - .12, apex.z - .05, FR)
    for q in (-1, 1):
        fr.add(tube([apex - V((0, 0, .1)), V((x, q * (HD - .05), .85))], .016, 6, zone=CB))
P.mesh('deck', deck, M); P.mesh('frame', fr, M, smooth_angle=50)
P.hull_collider('col_deck', [V((x, y, z)) for x in (-HW, HW) for y in (-HD, HD) for z in (0, -TH - .09)])
for s in (-1, 1):
    x = s * (HW - .05)
    P.hull_collider(f'col_rail{s + 1}', [V((x + a * .03, y, z)) for a in (-1, 1) for y in (-HD, HD) for z in (0, .87)])
P.export(out); P.save_blend(out)

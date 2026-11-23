"""Cargo winch numbers, in the frame of SEP_26_SHIP_CARGO's model: Blender (x, y, z) = Unity (x, z, y), metres.
The bay opens toward -y. Clearances come from ray casts into SEP_26_SHIP_CARGO.mu, checked by check_fit.py."""
CEILING_Z = 3.97            # node on the bay ceiling, on the part's axis
RAIL_X = 1.25               # the opening is clear to |x| = 1.6 at rail height
RAIL_Y = (-1.70, 1.75)      # back wall is at y = 1.95 here
RAIL_Z = (3.60, 3.80)
TIE_Z = (3.80, 3.90)
ARM_Y = (-0.62, 1.70)
MID_Y = (-0.75, 1.70)
MID_SHARE = 0.6             # the middle stage follows the piston by this share, so all three overlap at full reach
BEAM_Z = (3.38, 3.54)       # crossbeam under the rails; a child part hangs from its underside

CENTRE_Y = -0.5             # platform centre when stowed
BOOM_TRAVEL = 4.4           # takes the platform's back edge to y = -3.4, outside the hull and raceways
HOIST_TOP_Z = BEAM_Z[0]
CABLE_TOP_Z = 3.02
DECK_Z = 0.87               # deck top at full retraction, bridle apex just under the winches; the bay floor is at -2.52
DECK_W, DECK_D = 3.2, 3.0   # stowed it fits inside the closed doors, and it passes between them open
APEX_H = 2.0                # bridle apex above the deck
APEX_Z = DECK_Z + APEX_H
HOIST_TRAVEL = 29.1         # 21.1 m of core under the cargo section, plus legs and a margin, from the raised deck

ATLAS = 1024
Z = dict(FRAME=(0, 0, 512, 512), DARK=(512, 0, 512, 256), CABLE=(512, 256, 512, 64), BRIGHT=(512, 320, 512, 192), DECK=(0, 512, 1024, 512))

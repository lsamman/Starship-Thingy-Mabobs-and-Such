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

# ---------------------------------------------------------------- Block 3 crew nosecones (window kits)
# Frame of SEP_26_SHIP_NOSECONE's model, Blender axes, KSP metres. Azimuth 0 is -y: the leeward, bare-steel side
# (Unity -Z). The heat-shield tiles face +y. Only measured numbers of SEP's mesh live here, nothing of the mesh itself.
# check_nose.py tests NOSE_RINGS, and every window against the real tiles, with SEP_26_SHIP_NOSECONE.mu whenever SEP is
# installed; NOSE_STEEL and NOSE_WELDS record the measured limits the rows were placed by.
NOSE_SIDES = 48             # the steel shell is a 48-sided lathe with its vertices on multiples of 7.5 deg
# Vertex rings of the shell, (z, vertex radius): the barrel (Cylinder) and the ogive (Nose_7_EXT), straight between rings
NOSE_RINGS = ((-3.412, 2.8125), (0.006, 2.8124), (0.840, 2.7892), (1.816, 2.7151), (2.581, 2.6023), (3.360, 2.4546),
              (4.132, 2.2600), (4.640, 2.1174), (5.307, 1.8957), (5.807, 1.7041), (6.2340, 1.5289), (6.4700, 1.4229), (6.7123, 1.3066), (6.9450, 1.1934), (7.1446, 1.0920), (7.2794, 1.0187), (7.4021, 0.9507), (7.5308, 0.8786), (7.6688, 0.8027), (7.7987, 0.7270), (7.9277, 0.6502), (8.0297, 0.5907), (8.1360, 0.5202), (8.2905, 0.4202), (8.3776, 0.3616), (8.4339, 0.3219), (8.4853, 0.2701), (8.5244, 0.2072), (8.5528, 0.0976))
NOSE_WELDS = (-2.282, -1.139, 0.003)   # weld grooves and the barrel-ogive seam: no window crosses them
# Bare steel half-width (deg either side of az 0) by height, the narrower of the two ablative subtypes (39 and 43).
# Above 4.85 the Ablative 43 band and the tip tiles cover it; 0.83-1.34 has two tile patches at +-26..34 deg;
# the flap aerocovers start at +-72.5 deg, and the flap hinges sit at +-70 deg, z 4.25.
NOSE_STEEL = ((-2.7, 70), (-0.9, 70), (-0.7, 63.5), (-0.5, 53), (-0.4, 47.5), (0.8, 47.5), (0.83, 26), (1.34, 26),
              (1.4, 47.5), (2.0, 47.5), (2.5, 64.5), (2.6, 72.5), (4.85, 72.5))
NOSE_FLAP_AZ = 70.0
# The ITS crew section's big window: a geodesic lattice in a half-ellipse, laid on the skin from z0 (straight lower
# edge, half-width ha along the skin) to z1 (top of the arch). ha 2.1 puts the lower corners at +-46 deg, 24 deg short
# of the flap hinges; the arch's rim tops out at 4.66, 0.19 under the Ablative 43 band; below 2.6 the steel narrows.
NOSE_BIG = dict(z0=2.65, z1=4.60, ha=2.1, side=.4875)     # side: the ITS lattice's 0.78 m real
# Small windows under it, as in the ITS crew section's lower rows: (z, count, half-span of the centres in deg).
# Panes are the ITS ones at the same 0.625 scale, 0.50 x 0.42 m real. Rows sit 1.3 apart, clear of the tile patches
# (0.83-1.34) and the welds; each variant takes the first N rows: for two rows on the crew-cargo nose, make its 1 a 2.
SMALL = (.3125, .2625)
NOSE_SMALL_ROWS = ((1.70, 10, 41), (0.40, 9, 40), (-0.90, 11, 48))   # the first row leaves its middle to the EVA hatch
CAP_Z = 7.2794               # the tip above this ring is a hinged cap over the docking seat
EVA_Z, EVA_HW = (.96, 2.04), 6.8   # EVA hatch at az 0: heights, half-width in degrees; the access arm on the tower meets it
NOSE_SMALL_COUNT = {'crew': 3, 'crewcargo': 1}
NOSE_FRAME = .035           # frame border around a pane
NOSE_FRAME_H = .022         # frame height before the sink: 14 mm proud of the hull
NOSE_SINK = .008            # everything laid on the hull is bent onto its facets and sunk this much
NOSE_GLASS_OFF = .004       # glass this far above the hull, under the frame's inner lip
# Crew: the shell holds 184 m3 from the bulkhead at z -2.53 to the tip. Twelve kerbals is 15 m3 each, about 63 m3 a
# person at real scale (the ISS gives its seven about 55). The ITS crew section's density (16 in 447 m3) would allow
# only 6-7 here; that is roomy for KSP, where stock cabins give about 2 m3 a kerbal. The crew-cargo nose's cabin is
# the top deck, z 2.6-5.8, 50 m3: four at 12 m3.
NOSE_CREW = {'crew': 12, 'crewcargo': 4}

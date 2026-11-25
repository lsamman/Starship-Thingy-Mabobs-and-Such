"""Starship HLS numbers, KSP metres. z = 0 is the skirt's bottom edge, azimuth 0 (-y, Unity -Z) is the airlock door.
Proportions come from the NASA/SpaceX renders (11-2024, reissued 10-2025 and 8-2026). The interfaces are SEP's Block 3
ship: hull radius, joint height, engine and docking nodes, as measured numbers, so either half also mates with SEP's."""
R = 2.8125
SIDES = 96                  # facets of the hull
STEP = 360 / SIDES
# ---- SEP_26_SHIP_CORE interface (its z + 12.5993)
Z_SKIN = 20.574             # where the core's skin ends and the nose's begins
Z_TOP = 21.1037             # stack node
Z_SL, R_SL = 1.8916, .5829  # sea-level Raptor nodes, azimuth 0/120/240
Z_VAC, R_VAC = 2.7821, 1.9958   # vacuum Raptor nodes, azimuth 60/180/300
Z_DOCK, R_DOCK = 11.5717 + 3.25, 2.875   # SEP's ship-to-ship docking hardware: raised, so its aft latches clear the stowed legs
DOCK_AZ = 180
# ---- crew nose: rings (z above the joint of barrel and ogive, radius). The ogive is SEP's nose shape, so noses swap.
Z_OGIVE = Z_TOP + 2.895
OGIVE = ((0, 2.8125), (.84, 2.789), (1.82, 2.715), (2.58, 2.602), (3.36, 2.455), (4.13, 2.26), (4.64, 2.117), (5.31, 1.896),
         (5.81, 1.704), (6.23, 1.529), (6.71, 1.307), (7.14, 1.092), (7.40, .951))
CAP = ((7.40, .951), (7.67, .803), (7.93, .65), (8.14, .52), (8.29, .42), (8.38, .362), (8.43, .322), (8.49, .27), (8.52, .207), (8.555, .10), (8.565, 0))
# ---- paint
Z_BLACK = .97               # a ring of vertices; the base itself is white
LEG_AZ = (45, 135, 225, 315)
PANEL_TOP, PANEL_W = 4.75, (.78, .78)    # dark recess behind a leg: top, half-widths at base and top (arc length)
# leg pods, faceted: rows of (z, depth off the hull, half-width at the hull, half-width of the flat face), and the arched opening
POD = ((0, .66, 1.08, .93), (4.95, .86, 1.02, .86), (6.9, .0, .80, .66)); POD_OPEN = (.76, 4.74, .34)      # half-width, top, corner radius
# ---- landing thrusters: six groups of three between the elevator track and the docking side
BAND = (19.24, 20.01)       # thin, right under the cargo door's sill (SpaceX's cargo lander render, April 2024)
GROUPS = (31.875, 91.875, 148.125, 211.875, 268.125, 328.125); PITCH = 11.25   # edges fall on the facet grid
BORE = (.17, .21)         # half-axes of a port in the skin
CANT = 50                   # exhaust axis: degrees below the outward normal
LIGHT_AZ = (61.875, 120, 240, 298.125)
# ---- elevator track and airlock
TRACK = 7.5                 # half-width, degrees
TRACK_R = 2.40               # where the elevator is stowed, inside the airlock; the rails are on the hull, SLIDE further out
SLIDE = R - TRACK_R
DOOR = (21.75, 23.25); DOOR_AZ = 18.75
BAY_BACK = -1.25
# ---- windows
WIN_Z, WIN_N, WIN_SPAN, WIN = 25.48, 10, 36.0, (.31, .74)
# ---- solar bays
SOL_AZ = (56.25, 101.25, 258.75, 303.75); SOL_HW = 18.75; SOL_DP = 1.62; SOL_Z = (22.95, 23.8); SOL_OUT, SOL_HATCH = 1.27, 150     # how far the carriage runs out, how far the hatch swings up
# ---- legs (plane of one leg: r outward, z)
HINGE = (2.87, 4.35); SOLE = -1.0; FOOT_R = 5.35; FOOT_STOW = .52
SHELL = ((.26, .05), (.32, .30), (.46, .58), (.8, .74), (1.4, .80), (2.2, .78), (3.2, .74), (3.9, .72), (4.25, .70), (4.6, .60), (4.9, .42), (5.2, .21), (5.45, .03), (5.5, 0))   # blister over a stowed leg: (z, height off the hull)
SHELL_W = ((.26, 1.18), (.8, 1.34), (1.6, 1.28), (2.6, .92), (4.2, .74), (4.9, .56), (5.3, .28), (5.5, .10))   # and half-width
# the aeroshielded leg for SEP's ship: slimmer, and placed clear of SEP's vent (az 29-47, z 4.7-5.4), docking cone
# (29-44, z 1.9-2.4), camera (51-55, z 2.6-2.9) and flap fairing (80 on)
SHIP_LEG_AZ = (63, 150, 210, 297)
SHIP_SHELL = ((.30, .03), (.36, .34), (.43, .60), (.50, .73), (.8, .77), (1.4, .75), (2.2, .62), (3.2, .56), (4.0, .56), (4.4, .54), (4.75, .42), (5.1, .22), (5.4, .03), (5.45, 0))
SHIP_SHELL_W = ((.30, .56), (.5, .76), (.95, .76), (1.5, .66), (2.1, .42), (2.5, .345), (3.2, .345), (3.9, .42), (4.5, .42), (5.0, .28), (5.45, .06))
COLLAR = .72               # drag strut collar, up the strut from the ankle (deployed)
LIFT_TRAVEL = 22.3
SHEET = {'core': (0.0, Z_SKIN), 'crew': (Z_SKIN, Z_OGIVE + 7.40), 'cargo': (Z_SKIN, Z_OGIVE + 7.40)}
# ---- cargo section, in its own frame (z = 0 at Z_OGIVE): door, bay, crane frame
CG_SILL, CG_HEAD, CG_AZ = -2.70, 2.70, 52.5
CG_FLOOR, CG_CEIL = -2.80, 2.24
CG_SWING = 112
FRAME_X, FRAME_Y, FRAME_Z, FRAME_L, FRAME_OUT, FRAME_LEAN = 1.74, -1.72, -2.45, 4.20, 1.42, 30     # crane frame: pivots, length folded, how far it telescopes, lean
FRAME_TOPX = 1.74
WINCH_DZ = CG_CEIL - 3.97
PAD = .003

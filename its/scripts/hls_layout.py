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
Z_BLACK = .97               # black base
LEG_AZ = (45, 135, 225, 315)
PANEL_TOP, PANEL_W = 4.85, (1.02, .62)   # black leg panels: top, half-widths at base and top (arc length)
# ---- landing thrusters: six groups of three between the elevator track and the docking side
BAND = (19.0, 20.25)
GROUPS = (31.875, 91.875, 148.125, 211.875, 268.125, 328.125); PITCH = 11.25   # edges fall on the facet grid
BORE = (.262, .415)         # half-axes of a port in the skin
CANT = 50                   # exhaust axis: degrees below the outward normal
LIGHT_AZ = (61.875, 120, 240, 298.125)
# ---- elevator track and airlock
TRACK = 7.5                 # half-width, degrees
TRACK_R = 2.40
DOOR = (21.75, 23.25); DOOR_AZ = 18.75
BAY_BACK = -1.25
# ---- windows
WIN_Z, WIN_N, WIN_SPAN, WIN = 25.48, 10, 36.0, (.31, .74)
# ---- solar bays
SOL_AZ = (48.75, 311.25); SOL_HW = 18.75; SOL_Z = (22.95, 23.8)
# ---- legs (plane of one leg: r outward, z)
HINGE = (2.87, 4.35); SOLE = -1.0; FOOT_R = 5.35; FOOT_STOW = .52
COLLAR = 1.15               # drag strut collar, up the strut from the ankle (deployed)
LIFT_TRAVEL = 22.3
SHEET = {'core': (0.0, Z_SKIN), 'crew': (Z_SKIN, Z_OGIVE + 7.40)}
PAD = .003

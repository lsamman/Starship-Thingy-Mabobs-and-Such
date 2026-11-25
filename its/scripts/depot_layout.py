"""Storage depot numbers, KSP metres; z = 0 at the joint's stack node on SEP's Block 3 core."""
import hls_layout as HL
STRETCH = 7.6                # the chart's depot stands 1.23 times as tall as the tanker beside it
ZB = HL.Z_SKIN - HL.Z_TOP; ZJ = HL.Z_OGIVE - HL.Z_TOP + STRETCH; RING = 1.1427      # skin's lower edge; barrel-ogive joint; ring height (SEP's weld spacing)
SEC = [(21.35, 2.805), (21.2, 2.846), (20.8, 2.92), (19.9, 2.982), (18.7, 3.026), (17.3, 3.048), (15.9, 3.046), (14.5, 3.019), (13.4, 2.971), (12.6, 2.906), (12.3, 2.832), (12.2, 2.805)]      # raceway: azimuth, radius
C, R0, ZE = 16.75, 2.80, ZJ - .75
RINGS = [(0, 1, 1), (.18, 1, 1), (.26, .92, .93), (.33, .80, .82), (.41, .73, .70), (.46, .67, .56), (.505, .60, .38), (.535, .54, .20), (.55, .50, .02)]
UNITS = 50000                # about 330 m3, at the density of SEP's own tanks less room for coolers and ends

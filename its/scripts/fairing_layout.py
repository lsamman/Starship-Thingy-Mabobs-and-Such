"""Payload plate and fairing for the expendable Block 3 core. KSP metres; z = 0 is the core's top node, its skin ends 0.53 below."""
R = 2.8125
SKIRT = -.5297              # where SEP's core skin ends
Z0 = .45                    # fairing starts
WB, WALL, CONE, CAPR = 2.2, 2.5, 6.6, .62          # wall base, wall segment, ogive heights; radius where the cap sits
CAPH = .42
SEGS = 4
def ogive(t):               # t 0..1 up the cone: tangent ogive from R to CAPR
    import math
    L, dr = CONE, R - CAPR; rho = (L * L + dr * dr) / (2 * dr); z = t * L
    return R - rho + math.sqrt(rho * rho - z * z)
# one 2048 sheet, half a fairing wide: pixel rows (from the top) of each piece
ROWS = dict(cone=(0, 1120), wall=(1120, 1520), base=(1520, 1880), cap=(1160, 1260))

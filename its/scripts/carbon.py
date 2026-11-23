"""Bare-carbon livery for the hull sheets (tex_ship.py, tex_booster.py; B9 subtype Carbon in make_cfg.py).

Near-black composite in the repo's carbon tone (the details atlas' carbon zone). The fibre-placement
pattern lives in the gloss channel: plies laid at +-45 degrees in courses that cross in a diamond
pattern, the tows in each diamond running one way or the other, so it reads as a faint weave. DXT5
colour is 5:6:5, so at this albedo any RGB pattern would band; the alpha channel has the precision.
The sheets share the white livery's normal maps: seams and fasteners keep their relief.
x, s: circumferential and meridional distance on the hull, real metres."""
import numpy as np
from texcommon import hash2

RGB = (.075, .076, .080)
GLOSS = .46
COURSE = .30          # width of a fibre-placement course
TOW = .05             # visible tow spacing inside a course


def base(c, x, s, cloud, fine, period=None):
    """period: the sheet repeats every `period` metres of x (the booster's 120 degrees), so the pattern must too."""
    n = round(period / COURSE) if period else 0
    course = period / n if n else COURSE; tow = course / round(COURSE / TOW)
    p, m = x + s, x - s
    a, b = np.floor(p / course), np.floor(m / course)
    plus = ((a + b) % 2).astype(np.float32)                     # which ply is on top in this diamond
    tows = plus * np.cos(2 * np.pi * p / tow) + (1 - plus) * np.cos(2 * np.pi * m / tow)
    if n:
        a, b = a % n, b % n
    c.albedo[:] = np.array(RGB, np.float32)
    c.gloss[:] = (GLOSS + .014 * cloud + .008 * fine + .016 * (hash2(a, b, 9) - .5) + .012 * (plus - .5) + .010 * tows).astype(np.float32)


def seam(c, k):
    """Panel line: a matte resin line, a touch darker."""
    c.albedo *= (1 - .30 * k)[..., None]; c.gloss -= .16 * k


def strap(c, m):
    """Bonded joint strap: slightly greyer and satin."""
    c.albedo *= (1 + .10 * m)[..., None]; c.gloss -= .05 * m


def fastener(c, dot):
    """Flush titanium fastener heads show light against the carbon."""
    c.albedo[:] = c.albedo * (1 - .75 * dot[..., None]) + np.array((.30, .30, .31), np.float32) * (.75 * dot[..., None]); c.gloss += .06 * dot

"""Bay steel for the awning-door cargo section: bright rolled sheet with faint straw and blue heat tint, one 4 m repeat."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl
W = 1024; c = tl.Canvas(W, W, albedo=(.79, .79, .795), gloss=.74); f = lambda s, b: np.asarray(tl._fbm(W, W, s, base=b, octaves=4))
t = f(33, 3); t = t / (np.abs(t).max() + 1e-6); n = f(34, 24); straw, blue = np.clip(t, 0, 1), np.clip(-t, 0, 1)
c.albedo *= np.dstack([1 - .02 * straw - .07 * blue, 1 - .06 * straw - .035 * blue, 1 - .17 * straw + .01 * blue]) * (1 + .012 * n)[..., None]
c.gloss += .03 * t + .02 * n; c.height[:] = 0; c.save('stms_bay', nstrength=.2)

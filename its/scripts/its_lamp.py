"""Emissive masks over the detail atlas: only its 'lamp' zone glows."""
import numpy as np, tl, layout as L
x, y, w, h = L.DET['lamp']
for n, c in (('hls_lamp_emit', (255, 246, 225)), ('hls_green_emit', (60, 220, 255)), ('hls_red_emit', (255, 70, 60))):
    a = np.zeros((256, 256, 3), np.uint8); a[y // 8:(y + h) // 8, x // 8:(x + w) // 8] = c; tl.write_emissive(a, n)

"""Flat placeholder sheets, for geometry checks before the real textures exist."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, tl, hull as H, layout as L
def put(name, rgb, gloss, w=1024, h=None):
    h = h or w
    if os.path.exists(os.path.join(tl.OUT, name + '_diff.dds')): return
    c = tl.Canvas(w, h); c.albedo[:] = rgb; c.gloss[:] = gloss; c.save(name)
def hull(name, sheet):
    if os.path.exists(os.path.join(tl.OUT, name + '_diff.dds')): return
    az, z = H.grid(1024, 1024, sheet); c = tl.Canvas(1024)
    b = H.paint_d(az, z) < 0; c.albedo[:] = (.8, .8, .8); c.albedo[b] = (.05, .05, .055); c.gloss[:] = np.where(b, .3, .4); c.save(name)
hull('its_fwd', 'fwd'); hull('its_aft', 'aft')
if not os.path.exists(os.path.join(tl.OUT, 'its_det_diff.dds')):
    c = tl.Canvas(2048)
    col = dict(white=.8, grey=.5, carbon=.09, steel=.6, dark=.15, alu=.62, black=.04, invar=.55, wall=.45, deck=.4, stripe=.6, hatch=.7, pica=.05, dome=.4, copper=.5, rubber=.06, cable=.1, lamp=.9, label=.8)
    for k, (x, y, w, h) in L.DET.items(): c.albedo[y:y+h, x:x+w] = col[k]
    c.save('its_det')
put('its_glass', (.03, .04, .05), .9, 512)
if not os.path.exists(os.path.join(tl.OUT, 'its_glass_emit.dds')): tl.write_emissive(np.zeros((512, 512, 3), np.uint8) + np.array([255, 220, 160], np.uint8), 'its_glass_emit')
put('its_booster', (.78, .78, .78), .4, 1024)
put('its_solar', (.05, .05, .12), .6, 512)

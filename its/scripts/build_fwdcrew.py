"""Crew forward section: geodesic nose window, four window rows, two side hatches."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fwd import *
P = start('ITS_FwdCrew'); M = materials(P)
MG = P.material('its_glass', shader='KSP/Emissive/Bumped Specular', spec=(1, 1, 1), shininess=.8, emissive='its_glass_emit')
P.mesh('hull', skin(H.Z_SPLIT, H.Z_TIP, 'fwd', O), M, smooth_angle=32)
glass, frame, det = Geo(), Geo(), Geo()
nose_window(P, glass, frame); windows(P, glass, frame)
P.mesh('glass', glass, MG, smooth_angle=60)
joint(P, det); det.add(frame); det.add(ports(P, RCS))
# side hatches at az 62: frame, hinges, handrails
for s in (1, -1):
    h = Geo()
    h.add(rounded_rect_ring(1.86, 1.86, .26, .05, .022, 5, zone=Z.white))
    for yy in (-.55, 0, .55):
        h.add(box(.10, .22, .05, zone=Z.grey, bevel=.012, center=(.95, yy, .02)))
        h.add(cyl(.025, .2, 8, zone=Z.steel), T(.95, yy, .05) @ Rx(90))
    h.add(cyl(.11, .03, 20, zone=Z.grey, bevel=.008, center_z=False), T(-.62, 0, .0))
    h.add(box(.04, .2, .03, zone=Z.steel, bevel=.006, center=(-.62, 0, .04)))
    for sx in (-1.13, 1.16):
        h.add(tube([(sx, -.75, -.01), (sx, -.72, .07), (sx, .72, .07), (sx, .75, -.01)], .016, 6, zone=Z.steel))
    det.add(stick(h, s * 60, 28.75, O))
    p = surf(s * 60, 28.75, O, .35)
    out = Vector((math.sin(math.radians(s * 60)), -math.cos(math.radians(s * 60)), 0))
    P.box_trigger('airlock%d' % (s > 0), climb_frame(p.translation, out), (.9, .6, 1.2), 'Airlock')
    P.box_trigger('ladder%d' % (s > 0), climb_frame(surf(s * 60, 28.6, O, .12).translation, out), (1.0, .25, 1.9), 'Ladder')
P.mesh('detail', det, P.det)
colliders(P)
P.node('bottom', (0, 0, Z0), (0, 0, -1), 6)
finish(P)

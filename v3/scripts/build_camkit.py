"""Hull cameras for RasterPropMonitor on SEP's Block 3 ship, after the ship views of SpaceX's flight livestreams, as extra MODELs
the camera patch (its/patches/STMS_Cameras.cfg) adds to SEP's parts and ours. Our geometry only: small pods and camera transforms
placed from measured numbers (SEP's flap nodes and its own camera housings, Cam_EXT, where the livestream flap views come from).
Camera IDs are fixed across the mod (its/scripts/make_cameras_cfg.py), so the displays' camera pages always mean the same view;
SEP's own cameras give 1-7 (engine bay, aft and forward flaps, the camera low on the nose). Ours: 8, the nose looking forward.
Camera transforms: +Y looks, +Z is the picture's up.
usage: blender -b -P build_camkit.py -- <build/mu>"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from sl import *
import layout as L, nose as N

out = sys.argv[sys.argv.index('--') + 1]
enable_addon()
V = Vector


def frame(p, look, up):
    y = V(look).normalized(); z = V(up); z = (z - z.dot(y) * y).normalized(); m = Matrix((y.cross(z), y, z)).transposed().to_4x4(); m.translation = V(p); return m


def kit(name, cams):
    """cams: (id, position, look, up, pod frame); a pod is a small housing with a lens, the camera just in front of it."""
    clean_scene(); P = Part(name); MF = P.material('stms_b3_kit', spec=(.5, .5, .52), shininess=.4); ZN = Zone(0, 0, 256, 256, atlas=256); pods = Geo()
    for cid, p, look, up, pod in cams:
        P.empty(f'stms_cam{cid}', frame(p, look, up), P.model)
        pods.add(box(.11, .15, .08, zone=ZN, bevel=.014, center=(0, 0, .04)), pod)
        pods.add(cyl(.032, .05, 14, zone=ZN), frame(p, look, up) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
    P.mesh('stms_campods', pods, MF, smooth_angle=40)
    P.two_sided = True; P.export(out)


def surf_pod(az, z, look):
    """A pod on the nose's surface at (az, z) and its camera, looking 'down' or 'up' the hull: (position, look, up, pod frame)."""
    n = N.normal(az, z); upz = V((0, 0, 1)); tg = (upz - upz.dot(n) * n).normalized()
    m = Matrix((tg.cross(n), tg, n)).transposed().to_4x4(); m.translation = N.point(az, z, -L.NOSE_SINK)
    return m @ V((0, -.085 if look == 'down' else .085, .045)), (-tg if look == 'down' else tg), n, m      # the camera at the housing's front face


# ---- the nose (SEP's nosecone, cargo and Pez sections and our two crew noses share its frame). SEP has its own forward flap cameras
# (LFWDCAMERA, RFWDCAMERA) and the camera low on the leeward side (Cam_PLDoor, on every nose): the camera patch uses those. Ours:
# a pod looking forward up the nose. The ship core has nothing of ours: SEP's engine bay and aft flap cameras cover it.
p8, l8, u8, f8 = surf_pod(58, 3.2, 'up'); kit('STMS_Cams_B3Nose', [(8, p8, l8, u8, f8)])

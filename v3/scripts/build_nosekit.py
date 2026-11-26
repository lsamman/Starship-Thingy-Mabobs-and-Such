"""Window kit for SEP's Block 3 nosecone: frames and glass, in the nosecone model's own frame,
for a second MODEL on the STMS_B3_Nose* copies of SEP_26_SHIP_NOSECONE. Our geometry and textures only; it is laid
on the nose's surface rebuilt from measured numbers (layout.py), so it builds without SEP installed.
usage: blender -b -P build_nosekit.py -- <build/mu> crew|crewcargo"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from sl import *
from facing import fix_facing
import layout as L, nose as N

out, variant = sys.argv[sys.argv.index('--') + 1:][:2]
NAME = {'crew': 'STMS_B3_WindowsCrew', 'crewcargo': 'STMS_B3_WindowsCrewCargo'}[variant]
enable_addon(); clean_scene()
P = Part(NAME)
MF = P.material('stms_b3_kit', spec=(.5, .5, .52), shininess=.4)
MG = P.material('stms_b3_glass', shader='KSP/Emissive/Bumped Specular', spec=(1, 1, 1), shininess=.8, emissive='stms_b3_glass_emit')
# names are unique to us: SEP's modules look transforms up by name across the whole part
frames, glass, spots, fs, gs, ss = N.windows(variant, Zone(0, 0, 256, 256, atlas=256))
P.mesh('stms_b3_frames', frames, MF, smooth_angle=40)
P.mesh('stms_b3_glass', glass, MG, smooth_angle=60)
# the windows under the side docking door, in a group the door switch shows when the door is elsewhere; the exporter drops
# Blender's .001, so this glass is a second 'stms_b3_glass' and the cabin lights find it too
win = P.empty('stms_b3_winS', None, P.model)
P.mesh('stms_b3_frames', fs, MF, parent=win, smooth_angle=40)
P.mesh('stms_b3_glass', gs, MG, parent=win, smooth_angle=60)
spots += ss
# hull cameras for RasterPropMonitor's camera pages (JSIExternalCameraSelector, added by the Avionics patch): +Y looks, +Z is up
cams = Geo()
for nm, az, z, look in (('stms_cam_down', -30, -2.2, 'down'), ('stms_cam_out', 0, 2.36, 'out'), ('stms_cam_up', 58, 3.2, 'up')):
    n = N.normal(az, z); upz = Vector((0, 0, 1)); tg = (upz - upz.dot(n) * n).normalized()
    y_, z_ = {'down': (-tg, n), 'up': (tg, n), 'out': (n, tg)}[look]; Fc = Matrix((y_.cross(z_), y_, z_)).transposed().to_4x4(); Fc.translation = N.point(az, z, .07)
    P.empty(nm, Fc, P.model); Fh = Matrix((tg.cross(n), tg, n)).transposed().to_4x4(); Fh.translation = N.point(az, z, -L.NOSE_SINK)
    cams.add(box(.10, .14, .07, zone=Zone(0, 0, 256, 256, atlas=256), bevel=.012, center=(0, 0, .035)), Fh); cams.add(cyl(.028, .03, 12, zone=Zone(0, 0, 256, 256, atlas=256)), Fc @ Matrix.Rotation(math.pi / 2, 4, 'X') @ Matrix.Translation((0, 0, .0)))
P.mesh('stms_b3_cams', cams, MF, smooth_angle=40)

# KSP draws front faces only. Judge which side of each piece shows against a stand-in of SEP's shell
# (from the same measured rings, 1 mm under it), then drop the stand-in so none of it is exported.
rings = [(0.0, L.NOSE_RINGS[0][0])] + [(r - .001, z) for z, r in L.NOSE_RINGS] + [(0.0, L.NOSE_RINGS[-1][0])]
vs, fs = [], []
for r, zz in rings:
    vs += [(r * math.sin(math.radians(N.STEP * k)), -r * math.cos(math.radians(N.STEP * k)), zz) for k in range(L.NOSE_SIDES)]
for j in range(len(rings) - 1):
    for k in range(L.NOSE_SIDES):
        k2 = (k + 1) % L.NOSE_SIDES; a, b = j * L.NOSE_SIDES, (j + 1) * L.NOSE_SIDES
        fs.append((a + k, a + k2, b + k2, b + k))
me = bpy.data.meshes.new('proxy'); me.from_pydata(vs, [], fs); me.update()
proxy = bpy.data.objects.new('proxy', me); P.coll.objects.link(proxy)
fix_facing([o for o in P.coll.objects], [0])
bpy.data.objects.remove(proxy)
P.two_sided = True
P.meta['windows'] = len(spots)
P.export(out); P.save_blend(out)
print(f'KIT {NAME}: big window + {len(spots)} small')

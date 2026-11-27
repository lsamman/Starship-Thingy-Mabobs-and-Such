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
# (the hull cameras are in build_camkit.py's models, which the camera patch adds)

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

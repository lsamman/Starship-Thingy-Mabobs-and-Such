"""The windward half of the Block 3 core's external stringers, for the expendable core. SEP models the stringer rows only on
the leeward half (az -90..90), since the tiles hid the rest; with the tiles off, the rows stopped halfway round. This takes
SEP's own stringer mesh from the player's install and turns a copy 180 degrees about the axis, so the rows close the ring.
The result is SEP's art, so it is not covered by this repo's licence (see LICENSE).
usage: blender -b -P derive_stringers.py -- <SEP assets> <its/build/mu>   (into the ITS parts, beside the stand-in textures)"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from sl import *
SEP, out = sys.argv[sys.argv.index('--') + 1:][:2]
enable_addon(); clean_scene()
old = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=os.path.join(SEP, 'SEP_26_SHIP_CORE.mu')); bpy.context.view_layer.update()
src = [o for o in bpy.data.objects if o not in old and o.type == 'MESH' and o.name.startswith('External Stringers')]
assert len(src) == 1, [o.name for o in bpy.data.objects if o not in old]
o = src[0]; me = o.data.copy(); me.calc_normals_split()
R = Matrix.Rotation(math.pi, 4, 'Z') @ o.matrix_world
nrm = [tuple((R.to_3x3() @ l.normal).normalized()) for l in me.loops]
me.transform(R); me.use_auto_smooth = True; me.normals_split_custom_set(nrm)
for c_ in list(me.color_attributes): me.color_attributes.remove(c_)
mat = o.material_slots[0].material
print('MATERIAL', mat.name, mat.mumatprop.shaderName if hasattr(mat, 'mumatprop') else '',
      sorted({t.name for t in bpy.data.textures} | {i.name for i in bpy.data.images}))
for x in [x for x in bpy.data.objects if x not in old]: bpy.data.objects.remove(x)
P = Part('STMS_B3_Stringers')
s = bpy.data.objects.new('stms_stringers', me); P.coll.objects.link(s); P.place(s, Matrix(), P.model)
P.meta['tris'] = {'stms_stringers': sum(len(p.vertices) - 2 for p in me.polygons)}
P.two_sided = True                                       # SEP's faces are right already
P.export(out)

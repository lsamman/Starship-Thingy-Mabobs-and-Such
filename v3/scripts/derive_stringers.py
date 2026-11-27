"""The windward half of the Block 3 core's external stringers, for the expendable core. SEP models the stringer rows only on
the leeward half (az -80..80 on the forward rows, -95..95 on the aft ones), since the tiles hid the rest; with the tiles off,
the rows stopped short. Every stringer element is a small quad on a regular angular lattice, so this takes SEP's own elements
from the player's install and lays copies round the windward side:
  forward rows: a clean stretch of SEP's lattice (az 25..80, past the raceway's bare band) repeated by whole lattice periods
                over az 80..280, so the slots carry on round with SEP's spacing and no bare bands at +-90;
  aft rows:     SEP's half turned 180 degrees (they already overlap at +-90).
The result is SEP's art, so it is not covered by this repo's licence (see LICENSE).
usage: blender -b -P derive_stringers.py -- <SEP assets> <its/build/mu>   (into the ITS parts, beside the stand-in textures)"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from sl import *
SEP, out = sys.argv[sys.argv.index('--') + 1:][:2]
enable_addon(); clean_scene()
old = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=os.path.join(SEP, 'SEP_26_SHIP_CORE.mu')); bpy.context.view_layer.update()
src = [o for o in bpy.data.objects if o not in old and o.type == 'MESH' and o.name.startswith('External Stringers')]
assert len(src) == 1, [o.name for o in bpy.data.objects if o not in old]
o = src[0]; me = o.data; me.calc_normals_split(); W = o.matrix_world; W3 = W.to_3x3()
mat = o.material_slots[0].material
print('MATERIAL', mat.name, mat.mumatprop.shaderName if hasattr(mat, 'mumatprop') else '')
V = np.array([tuple(W @ v.co) for v in me.vertices]); uvl = me.uv_layers.active.data
# ---- elements: polygons joined by shared vertices
par = list(range(len(V)))
def root(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
for p in me.polygons:
    for a in p.vertices[1:]: par[root(a)] = root(p.vertices[0])
el = {}
for p in me.polygons: el.setdefault(root(p.vertices[0]), []).append(p)
azof = lambda c: (math.degrees(math.atan2(c[0], -c[1])) + 360) % 360
E = []
for ps in el.values():
    vi = sorted({v for p in ps for v in p.vertices}); c = V[vi].mean(0)
    E.append(dict(ps=ps, az=azof(c), z0=round(float(V[vi, 2].min()), 2), z1=round(float(V[vi, 2].max()), 2)))
rows = {}
for e in E: rows.setdefault((e['z0'], e['z1']), []).append(e)
key = lambda az, r: (int(round((az % 360) / .05)) % 7200, r)
taken = {key(e['az'], (e['z0'], e['z1'])) for e in E}
# ---- the copies: (element, rotation in degrees about the axis)
copies = []
for r, es in sorted(rows.items()):
    if r[1] < 0:                                         # aft rows: SEP's half turned round
        copies += [(e, 180.0) for e in es if key(e['az'] + 180, r) not in taken]; continue
    band = sorted(e['az'] for e in es if 25 <= e['az'] < 80)
    bn = np.array(band)                                  # the lattice: the period 360/N that lands the most elements on others
    score = lambda P: sum(int((np.abs(bn[:, None] + k * P - bn[None, :]).min(1) < .004).sum()) for k in (1, 2, 3))
    P = max((360 / N for N in range(60, 401)), key=score); S = P * math.floor(55 / P)     # whole periods, no wider than the band
    for j in range(1, 6):
        for e in es:
            if not 25 <= e['az'] < 80: continue
            a = (e['az'] + j * S) % 360
            if 80 <= a < 280 and key(a, r) not in taken: taken.add(key(a, r)); copies.append((e, j * S))
    print(f'row z {r}: {len(es)} of SEP\'s, lattice {P:.4f} deg (N {round(360 / P)}), step {S:.3f}, copies so far {len(copies)}')
# ---- one mesh from the copies, with SEP's UVs and its split normals turned with each copy
vs, fs, uvs, ns = [], [], [], []
for e, deg in copies:
    R = Matrix.Rotation(math.radians(deg), 3, 'Z')
    for p in e['ps']:
        f = []
        for li in p.loop_indices:
            l = me.loops[li]; vs.append(tuple(R @ Vector(V[l.vertex_index]))); f.append(len(vs) - 1); uvs.append(tuple(uvl[li].uv)); ns.append(tuple((R @ (W3 @ l.normal)).normalized()))
        fs.append(f)
m2 = bpy.data.meshes.new('stms_stringers'); m2.from_pydata(vs, [], fs); m2.update()
uv = m2.uv_layers.new(name='UVMap')
for i, l in enumerate(m2.loops): uv.data[i].uv = uvs[i]
m2.use_auto_smooth = True; m2.normals_split_custom_set(ns); m2.materials.append(mat)
for x in [x for x in bpy.data.objects if x not in old]: bpy.data.objects.remove(x)
P_ = Part('STMS_B3_Stringers')
s = bpy.data.objects.new('stms_stringers', m2); P_.coll.objects.link(s); P_.place(s, Matrix(), P_.model)
P_.meta['tris'] = {'stms_stringers': sum(len(p.vertices) - 2 for p in m2.polygons)}
P_.two_sided = True                                       # SEP's faces are right already
P_.export(out)

"""Clearances between SEP's real Raptor meshes at the ring, ship and gimbal positions."""
import bpy, sys, math, os, addon_utils, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
import layout as L
addon_utils.enable('io_object_mu', default_set=True)
SEP = os.path.expanduser('~/.local/share/Steam/steamapps/common/Kerbal Space Program Modded SOL/GameData/StarshipExpansionProject/Assets/BL3/SEP_26_RAPTOR_3.mu')
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_object.ksp_mu(filepath=SEP); bpy.context.view_layer.update()
def under(o, names):
    while o:
        if o.name.split('∧')[0].split('.')[0] in names: return True
        o = o.parent
    return False
def mesh(skip):
    V = []; F = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or not o.data.polygons or 'COLLIDER' in o.name or under(o, skip): continue
        n = len(V); V += [o.matrix_world @ v.co for v in o.data.vertices]; F += [[n + i for i in p.vertices] for p in o.data.polygons]
    return np.array(V), F
def tree(m, M):
    V, F = m; a = (np.c_[V, np.ones(len(V))] @ np.array(M).T)[:, :3]
    return BVHTree.FromPolygons([tuple(p) for p in a], F), a
def at(r, az, top, s=1.0, tilt=(0, 0)):
    a = math.radians(az)
    piv = Matrix.Translation((r * math.sin(a), -r * math.cos(a), top))
    return piv @ Matrix.Rotation(math.radians(tilt[0]), 4, 'X') @ Matrix.Rotation(math.radians(tilt[1]), 4, 'Y') @ Matrix.Rotation(math.radians(az + 180), 4, 'Z') @ Matrix.Scale(s, 4) @ Matrix.Translation((0, 0, -L.R3_TOP))
B = mesh({'R3Vac_Stuff', 'R3C_Stuff', 'R3_Gimballing_Stuff'})      # fixed booster engine
C = mesh({'R3Vac_Stuff'})                                           # center engine
VA = mesh({'R3_SL_Stuff', 'R3C_Stuff', 'R3_Gimballing_Stuff'})     # vacuum engine
bad = 0
def pair(name, a, b):
    global bad
    ta, pa = a; tb, pb = b
    hit = ta.overlap(tb)
    d = min(tb.find_nearest(Vector(p))[3] for p in pa[::7])
    print(f'{name}: clearance {d:.3f} m, {len(hit)} overlapping tris'); bad += bool(hit)
n21, r21, _ = L.RINGS['ITS_Ring21']; n14, r14, a14 = L.RINGS['ITS_Ring14']; n7, r7, _ = L.RINGS['ITS_Ring7']
o0 = tree(B, at(r21, 0, 0)); pair('outer-outer', o0, tree(B, at(r21, 360 / n21, 0)))
i0 = tree(B, at(r14, a14, 0)); pair('inner-inner', i0, tree(B, at(r14, a14 + 360 / n14, 0)))
for k in range(2): pair(f'outer{k}-inner', tree(B, at(r21, k * 360 / n21, 0)), i0)
pair('center-center', tree(C, at(r7, 0, 0)), tree(C, at(0, 0, 0))); pair('center-center2', tree(C, at(r7, 0, 0)), tree(C, at(r7, 60, 0)))
for t in ((-7, 0), (7, 0), (0, 7), (5, 5)):
    g = tree(C, at(r7, 0, 0, tilt=t))
    for k in (0, 13): pair(f'center tilt {t} - inner{k}', g, tree(B, at(r14, a14 + k * 360 / 14, 0)))
mx = max(math.hypot(*p[:2]) for p in o0[1]); print('outer ring max radius', round(mx, 3), 'hull', L.BR * L.K)
v = [tree(VA, at(L.VAC_R, a, L.VAC_Z, L.RV_SCALE)) for a in L.VAC_AZ[:2]]
pair('vac-vac', *v); print('vac max radius', round(max(math.hypot(*p[:2]) for p in v[0][1]), 3))
for t in ((0, 0), (9, 0), (-9, 0), (0, 9)):
    s = tree(C, at(L.SL_R, 0, L.SL_Z, tilt=t)); pair(f'SL tilt {t} - vac', s, v[0])
pair('SL-SL', tree(C, at(L.SL_R, 0, L.SL_Z)), tree(C, at(L.SL_R, 120, L.SL_Z)))
print('FAIL' if bad else 'PASS', bad)

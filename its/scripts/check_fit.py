"""Clearances of the moving parts: crane against the cargo bay, doors, hull and leg; leg and fan against the ship.
usage: blender -b -P check_fit.py -- build/mu"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, addon_utils
from mathutils import Matrix, Vector as V
from mathutils.bvhtree import BVHTree
import layout as L, hull as H
addon_utils.enable('io_object_mu', default_set=True)
mu = sys.argv[sys.argv.index('--') + 1]; K = L.K
for o in list(bpy.data.objects): bpy.data.objects.remove(o)


def mesh(part, frac=None, skip=()):
    """World-space triangles of a part with its clip at a fraction of its length."""
    before = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=os.path.join(mu, part + '.mu'))
    new = [o for o in bpy.data.objects if o not in before]
    if frac is not None:
        for o in new:
            ad = o.animation_data
            if ad:
                for tr in ad.nla_tracks:
                    for s in tr.strips: ad.action = s.action; end = s.action.frame_range[1]
                    tr.mute = True
        bpy.context.scene.frame_set(int(round(end * frac)))
    bpy.context.view_layer.update()
    v, f = [], []
    for o in new:
        if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.data.polygons and not any(k in o.name for k in skip):
            n = len(v); v += [tuple(o.matrix_world @ x.co) for x in o.data.vertices]; f += [[n + i for i in p.vertices] for p in o.data.polygons]
    for o in new: bpy.data.objects.remove(o)
    return np.array(v), f


def tree(m, M=Matrix()):
    a = (np.c_[m[0], np.ones(len(m[0]))] @ np.array(M).T)[:, :3]
    return BVHTree.FromPolygons([tuple(p) for p in a], m[1]), a


bad = 0
def test(name, A, B, allow=0):
    global bad
    n = len(A[0].overlap(B[0])); d = min((B[0].find_nearest(V(p))[3] or 99) for p in A[1][::max(1, len(A[1]) // 600)])
    print(f'{"ok " if n <= allow else "HIT"} {name}: {n} overlaps, nearest {d:.3f} m'); bad += n > allow


fwd0, fwd1 = tree(mesh('ITS_FwdCargo', 0)), tree(mesh('ITS_FwdCargo', 1))
C = Matrix.Translation((0, 0, (L.BAY_TOP - H.O_FWD) * K)) @ Matrix.Rotation(math.radians(L.CR_AZ), 4, 'Z')
boom, hoist, plat = mesh('ITS_CargoBoom'), mesh('ITS_CargoHoist'), mesh('ITS_CargoPlatform')
rails = (boom[0], boom[1])
at = lambda m, y, z: tree(m, C @ Matrix.Translation((0, y, z)))
ZB = L.CR_Z['beam'][0]
test('hoist stowed, doors shut', at(hoist, L.CR_C, ZB), fwd0)
test('platform stowed, doors shut', at(plat, L.CR_C, L.CR_DECK), fwd0)
test('boom in bay, doors shut', at(boom, 0, 0), fwd0, 300)     # the flange is bolted to the plate
for t in np.linspace(.1, 1, 7):
    test(f'platform out {t:.2f}', at(plat, L.CR_C - L.CR_TRAVEL * t, L.CR_DECK), fwd1)
    test(f'hoist out {t:.2f}', at(hoist, L.CR_C - L.CR_TRAVEL * t, ZB), fwd1)
aft = mesh('ITS_ShipAft'); AM = Matrix.Translation((0, 0, (H.O_AFT - H.O_FWD) * K)); AT = tree(aft, AM)
legM = lambda az: AM @ Matrix.Rotation(math.radians(az), 4, 'Z') @ Matrix.Translation((0, -L.LEG_H[0] * K, (L.LEG_H[1] - H.O_AFT) * K))
leg1, leg0 = mesh('ITS_Leg', 1), mesh('ITS_Leg', 0)
LT = [tree(leg1, legM(a)) for a in L.LEG_AZ]
for dz in np.linspace(0, L.CR_HOIST - 1.2, 9):
    p = at(plat, L.CR_C - L.CR_TRAVEL, L.CR_DECK - dz)
    test(f'platform down {dz:.1f} / hull', p, AT); test(f'platform down {dz:.1f} / leg', p, LT[0])
low = (L.BAY_TOP - H.O_FWD) * K + L.CR_DECK - L.CR_HOIST; gnd = (L.LEG_SOLE - H.O_FWD) * K
print(f'platform lowest {low:.2f}, ground {gnd:.2f}, margin {gnd - low:.2f}')
bst = mesh('ITS_Booster'); BM = AM @ Matrix.Translation((0, 0, L.AFT_BOT - (L.BZ_TOP - L.B_ORIGIN) * K)); BT = tree(bst, BM)
for a in L.LEG_AZ: test(f'leg {a} stowed / booster', tree(leg0, legM(a)), BT)
fan0 = mesh('ITS_FanArray', 0); fanM = lambda az: AM @ Matrix.Rotation(math.radians(az), 4, 'Z') @ Matrix.Translation((0, -L.FAN_P[0] * K, (L.FAN_P[1] - H.O_AFT) * K))
test('fan stowed / booster', tree(fan0, fanM(60)), BT)
test('fan stowed / aft', tree(fan0, fanM(60)), AT, 1900)   # its rails are bolted to the skirt frames
for fr in (.1, .2, .3, .5, .75, 1):
    m = mesh('ITS_FanArray', fr, ('base',)); t = tree(m, fanM(60)); test(f'fan {fr} / legs', t, LT[0]); test(f'fan {fr} / leg120', t, LT[1])
# vacuum engine beside the fan: SEP's real mesh
SEP = os.path.expanduser('~/.local/share/Steam/steamapps/common/Kerbal Space Program Modded SOL/GameData/StarshipExpansionProject/Assets/BL3/SEP_26_RAPTOR_3.mu')
if os.path.exists(SEP):
    bpy.ops.import_object.ksp_mu(filepath=SEP); bpy.context.view_layer.update(); v, f = [], []
    def under(o):
        while o:
            if o.name.split('∧')[0].split('.')[0] in ('R3_SL_Stuff', 'R3C_Stuff', 'R3_Gimballing_Stuff'): return True
            o = o.parent
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.data.polygons and 'COLLIDER' not in o.name and not under(o):
            n = len(v); v += [tuple(o.matrix_world @ x.co) for x in o.data.vertices]; f += [[n + i for i in p.vertices] for p in o.data.polygons]
    a = math.radians(30); e = tree((np.array(v), f), AM @ Matrix.Translation((L.VAC_R * math.sin(a), -L.VAC_R * math.cos(a), L.VAC_Z - L.R3_TOP * L.RV_SCALE)) @ Matrix.Scale(L.RV_SCALE, 4))
    for fr in (0, .1, .2, .25, .3, .4):
        test(f'fan {fr} / vac engine', tree(mesh('ITS_FanArray', fr), fanM(60)), e)
print('FIT', 'PASS' if not bad else f'{bad} FAILURES')

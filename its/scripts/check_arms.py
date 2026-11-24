"""The tower arms against SEP's booster, ship and our crew nose, through their whole retraction.
usage: blender -b -P check_arms.py -- build/mu <SEP assets>"""
import bpy, sys, os, math, addon_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
from mathutils.bvhtree import BVHTree
import tower_layout as T
addon_utils.enable('io_object_mu', default_set=True); MU, SEP = sys.argv[sys.argv.index('--') + 1:][:2]; sc = bpy.context.scene; bad = 0
base = lambda o: o.name.split('\u2227')[0].split('.')[0]
def imp(p): old = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=p); bpy.context.view_layer.update(); return [o for o in bpy.data.objects if o not in old]
def mesh(objs, skip=()): return [o for o in objs if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.data.polygons and not base(o).startswith('atmofx') and base(o) not in skip]
def tree(objs, M): 
    v, f = [], []
    for o in objs: n = len(v); m = M @ o.matrix_world; v += [m @ q.co for q in o.data.vertices]; f += [[n + i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(v, f)
S = lambda z: Matrix.Translation((T.SHIP[0], T.SHIP[1], z)) @ Matrix.Rotation(math.pi / 2, 4, 'Z'); targets = {}
for nm, p, z in (('booster', SEP + '/SEP_26_BOOSTER_CORE.mu', T.BOOST_Z), ('ship', SEP + '/SEP_26_SHIP_CORE.mu', T.CORE_Z), ('nose', MU + '/STMS_B3_HullCrew.mu', T.NOSE_Z)):
    o = imp(p); targets[nm] = tree(mesh(o, ('TestTiles',)), S(z)); [bpy.data.objects.remove(q) for q in o]
for part, clip, pos in (('STMS_QDArm', 'qdArm', (T.QD[0], T.QD[1], T.QD_Z)), ('STMS_CrewArm', 'crewArm', (T.CREW[0], T.CREW[1], T.EVA_Z))):
    obs = imp(f'{MU}/{part}.mu'); end = 0
    for o in obs:
        ad = o.animation_data
        for tr in list(ad.nla_tracks) if ad else []:
            tr.mute = True; act = tr.strips[0].action
            if act.name.split('.')[0] == clip or tr.name.split('.')[0] == clip: ad.action = act; end = max(end, int(act.frame_range[1]))
    M = Matrix.Translation(pos); worst = {}
    for f in range(0, end + 1, 4):
        sc.frame_set(f); bpy.context.view_layer.update()
        for o in mesh(obs):
            t = tree([o], M)
            for nm, tt in targets.items():
                n = len(t.overlap(tt))
                if n: worst.setdefault((base(o), nm), []).append((f, n))
    print(part, 'end frame', end)
    for k, v in sorted(worst.items()): print('   touches', k, 'frames', v[0][0], 'to', v[-1][0], 'max', max(n for _, n in v)); bad += v[-1][0] > 12
    [bpy.data.objects.remove(o) for o in obs]
print('check_arms:', bad, 'contacts after the arm has let go')

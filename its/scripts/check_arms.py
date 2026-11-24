"""The tower arms through their whole retraction, against SEP's booster, ship and our crew nose, SLE's tower and the chopstick
carriage at every height. usage: blender -b -P check_arms.py -- build/mu <SEP assets> <SLE SSPads>"""
import bpy, sys, os, math, addon_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
from mathutils.bvhtree import BVHTree
import tower_layout as T
addon_utils.enable('io_object_mu', default_set=True); MU, SEP, SLE = sys.argv[sys.argv.index('--') + 1:][:3]; sc = bpy.context.scene; bad = 0
base = lambda o: o.name.split('∧')[0].split('.')[0]
def imp(p): old = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=p); bpy.context.view_layer.update(); return [o for o in bpy.data.objects if o not in old]
def mesh(objs, skip=()): return [o for o in objs if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.data.polygons and not base(o).startswith('atmofx') and base(o) not in skip]
def tree(objs, M):
    v, f = [], []
    for o in objs: n = len(v); m = M @ o.matrix_world; v += [m @ q.co for q in o.data.vertices]; f += [[n + i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(v, f), v
S = lambda z: Matrix.Translation((T.SHIP[0], T.SHIP[1], z)) @ Matrix.Rotation(math.pi / 2, 4, 'Z'); K = Matrix.Scale(T.SCALE, 4); targets = {}
for nm, p, M, skip in (('booster', SEP + '/SEP_26_BOOSTER_CORE.mu', S(T.BOOST_Z), ()), ('ship', SEP + '/SEP_26_SHIP_CORE.mu', S(T.CORE_Z), ('TestTiles',)), ('nose', MU + '/STMS_B3_HullCrew.mu', S(T.NOSE_Z), ()), ('tower', SLE + '/SLE_SS_OLIT_Core.mu', K, ())):
    o = imp(p); targets[nm] = tree(mesh(o, skip), M)[0]; [bpy.data.objects.remove(q) for q in o]
o = imp(SLE + '/SLE_SS_OLIT_Top.mu'); targets['tower top'] = tree(mesh(o), Matrix.Translation((0, 0, 72.63)) @ K)[0]; [bpy.data.objects.remove(q) for q in o]
o = imp(SLE + '/SLE_SS_OLIT_MZ.mu'); cw = [q for q in o if base(q) == 'ClawStructure' and q.type == 'MESH' and q.data.polygons]; _, cv = tree(cw, K); cv = [(p.x + T.MZ[0], p.y + T.MZ[1]) for p in cv]; [bpy.data.objects.remove(q) for q in o]
import mathutils
kd = mathutils.kdtree.KDTree(len(cv)); [kd.insert((x, y, 0), i) for i, (x, y) in enumerate(cv)]; kd.balance()       # the carriage's plan, any height
hv = [V((x, y)) for x, y in cv]; idx = mathutils.geometry.convex_hull_2d(hv)
for part, clip, M in (('STMS_QDArm', 'qdArm', Matrix.Translation(T.NODE)), ('STMS_CrewArm', 'crewArm', Matrix.Translation((T.NODE[0], T.NODE[1], T.EVA_Z)) @ Matrix.Rotation(math.atan2(T.NODE_N[1], T.NODE_N[0]), 4, 'Z'))):
    obs = imp(f'{MU}/{part}.mu'); end = 0
    for o in obs:
        ad = o.animation_data
        for tr in list(ad.nla_tracks) if ad else []:
            tr.mute = True; act = tr.strips[0].action
            if act.name.split('.')[0] == clip or tr.name.split('.')[0] == clip: ad.action = act; end = max(end, int(act.frame_range[1]))
    worst = {}; near = (99, 0, '')
    for f in range(0, end + 1, 4):
        sc.frame_set(f); bpy.context.view_layer.update()
        for o in mesh(obs):
            if base(o) == 'hinge' and f: continue
            t, vs = tree([o], M)
            for nm, tt in targets.items():
                n = len(t.overlap(tt))
                if n and not (base(o) == 'hinge' and nm == 'tower'): worst.setdefault((base(o), nm), []).append((f, n))
            for p in vs[::5]:
                d = kd.find((p.x, p.y, 0))[2]
                if d < near[0]: near = (d, f, base(o))
    print(part, 'end frame', end, '| nearest to the chopstick carriage in plan: %.2f m (%s, frame %d)' % (near[0], near[2], near[1])); bad += near[0] < .3
    for k, v in sorted(worst.items()): print('   touches', k, 'frames', v[0][0], 'to', v[-1][0], 'max', max(n for _, n in v)); bad += v[-1][0] > 44
    [bpy.data.objects.remove(o) for o in obs]
print('check_arms:', bad, 'problems')

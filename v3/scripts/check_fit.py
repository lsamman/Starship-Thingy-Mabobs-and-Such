"""Tests the winch against SEP's real meshes: stowed behind closed doors, then across the boom's and hoist's travel.
Also poses the skinned stages and reports where the bones end up. Writes renders to the given prefix.
usage: blender -b -P check_fit.py -- <SEP dir> <build/mu> <render prefix>"""
import bpy, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import addon_utils
import numpy as np
from mathutils import Matrix, Vector as V
from mathutils.bvhtree import BVHTree
import layout as L
addon_utils.enable('io_object_mu', default_set=True)
sep, mu, pref = sys.argv[sys.argv.index('--') + 1:]
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
CORE_DZ = -2.895 - 32.022 * 0 - 8.504  # cargo bottom node meets the core's top node (0.625 x 13.607 above its origin)


def imp(path):
    before = set(bpy.data.objects)
    bpy.ops.import_object.ksp_mu(filepath=path)
    bpy.context.view_layer.update()
    new = [o for o in bpy.data.objects if o not in before]
    return new, [o for o in new if o.parent is None][0]


def vis(objs, skip=('atmofx',)):
    return [o for o in objs if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.data.materials and not o.name.startswith(skip)]


def bvh(objs):
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    vs, fs = [], []
    for o in objs:
        e = o.evaluated_get(dg); me = e.to_mesh(); m = e.matrix_world; n = len(vs)
        vs += [tuple(m @ v.co) for v in me.vertices]; fs += [tuple(n + i for i in p.vertices) for p in me.polygons]
        e.to_mesh_clear()
    return BVHTree.FromPolygons(vs, fs, all_triangles=False), np.array(vs)


cargo, _ = imp(f'{sep}/Assets/BL3/SEP_26_SHIP_CARGO.mu')
core, core_root = imp(f'{sep}/Assets/BL3/SEP_26_SHIP_CORE.mu')
core_root.location.z += CORE_DZ
# the core's own node_top height gives the real offset
top = [o for o in core if o.name.startswith('node_top')]
if top:
    bpy.context.view_layer.update(); core_root.location.z += -2.895 - top[0].matrix_world.translation.z
bpy.context.view_layer.update()
print('core top node at z', [round(o.matrix_world.translation.z, 3) for o in top], 'core mesh z range', bvh(vis(core))[1][:, 2].min().round(2), bvh(vis(core))[1][:, 2].max().round(2))
parts = {}
for n, off in (('Boom', (0, 0, L.CEILING_Z)), ('Hoist', (0, L.CENTRE_Y, L.HOIST_TOP_Z)), ('Platform', (0, L.CENTRE_Y, L.DECK_Z))):
    objs, root = imp(f'{mu}/SEP_CW_{n}.mu')
    root.location = off
    parts[n] = (objs, root)
    print(n, 'objects', len(objs), [o.name.split('∧')[0] for o in objs if o.type == 'ARMATURE'])
bpy.context.view_layer.update()
for o in bpy.data.objects:
    if o.type == 'ARMATURE':
        print('armature', o.name, {b.name: tuple(round(x, 3) for x in o.matrix_world @ b.head_local) for b in o.data.bones})


def pose(boom, hoist):
    # the hoist and platform are children of the boom's and hoist's servos, so they just translate
    parts['Hoist'][1].location = (0, L.CENTRE_Y - boom, L.HOIST_TOP_Z)
    parts['Platform'][1].location = (0, L.CENTRE_Y - boom, L.DECK_Z - hoist)
    for o in parts['Boom'][0] + parts['Hoist'][0]:
        if o.type == 'ARMATURE':
            for b in o.pose.bones:
                b.matrix_basis = Matrix()
                if b.name == 'BoomServo':
                    w = o.matrix_world.to_3x3().inverted() @ V((0, -boom, 0))
                    b.location = b.bone.matrix_local.to_3x3().inverted() @ w
                if b.name == 'HoistServo':
                    w = o.matrix_world.to_3x3().inverted() @ V((0, 0, -hoist))
                    b.location = b.bone.matrix_local.to_3x3().inverted() @ w
    bpy.context.view_layer.update()


def doors(frame):
    sc.frame_set(frame); bpy.context.view_layer.update()


mine = sum((vis(parts[k][0]) for k in parts), [])
cm, co = vis(cargo), vis(core)
def under(o, n):
    while o:
        if o.name.startswith(n):
            return True
        o = o.parent
    return False
# the zero-area bounds triangles and hull-embedded mounts aside, report real overlaps by part
def clashes(label, env):
    tree, _ = bvh(env)
    res = {}
    for k in parts:
        t, v = bvh(vis(parts[k][0]))
        res[k] = len(tree.overlap(t))
    print(f'{label}: overlaps', res)
    return res
doors(0); pose(0, 0); clashes('stowed, doors closed', cm)
print('  stowed part extents y/z', {k: (bvh(vis(parts[k][0]))[1].min(0).round(2).tolist(), bvh(vis(parts[k][0]))[1].max(0).round(2).tolist()) for k in parts})
doors(53); clashes('stowed, doors open', cm)
for e in (1, 2, 3, 4, L.BOOM_TRAVEL):
    pose(e, 0); clashes(f'boom {e}', cm)
pose(L.BOOM_TRAVEL, 0)
_, v = bvh(vis(parts['Platform'][0])); print('platform at full reach: y range', v[:, 1].min().round(2), v[:, 1].max().round(2))
# only the deck edge nearest the hull matters on the way down
for h in (1, 3, 6, 10, 15, 20, L.HOIST_TRAVEL):
    pose(L.BOOM_TRAVEL, h); tr, _ = bvh(cm + co); t, v = bvh(vis(parts['Platform'][0]))
    print(f'hoist {h}: platform clashes {len(tr.overlap(t))}, deck z {v[:, 2].max().round(2)}..{v[:, 2].min().round(2)}')
_, v = bvh(co); print('core bottom z', v[:, 2].min().round(2))
# renders
sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.color_type = 'OBJECT'; sc.display.shading.light = 'STUDIO'; sc.display.shading.show_cavity = True; sc.display.shading.show_backface_culling = False
sc.render.resolution_x = 800; sc.render.resolution_y = 1000
for o in bpy.data.objects:
    if o.type == 'MESH' and o not in cm + co + mine:
        o.hide_render = True
    elif o.type == 'MESH':
        o.color = (.62, .62, .65, 1) if o in cm + co else ((.95, .55, .1, 1) if o in vis(parts['Boom'][0]) else ((.1, .6, .95, 1) if o in vis(parts['Hoist'][0]) else (.2, .85, .3, 1)))
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'; cd.clip_end = 300; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
for tag, (e, h, fr, ctr, scale, dirs) in dict(stow=(0, 0, 53, (0, -1, 1), 11, {'lee': (0, -1, 0), 'side': (1, 0, 0)}),
                                               out=(L.BOOM_TRAVEL, 0, 53, (0, -2.5, 1), 13, {'quart': (.8, -.9, .35), 'side': (1, 0, 0)}),
                                               low=(L.BOOM_TRAVEL, 16, 53, (0, -2, -9), 30, {'side': (1, 0, 0), 'quart': (.8, -.9, .3)})).items():
    pose(e, h); doors(fr)
    for n, d in dirs.items():
        d = V(d).normalized(); cd.ortho_scale = scale; cam.location = V(ctr) + d * 60; cam.rotation_euler = (-d).to_track_quat('-Z', 'Z').to_euler()
        sc.render.filepath = f'{pref}{tag}_{n}.png'; bpy.ops.render.render(write_still=True)

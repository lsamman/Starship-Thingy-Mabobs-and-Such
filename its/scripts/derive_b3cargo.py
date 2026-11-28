"""Block 3 Cargo Section (Awning Door): SEP's Block 3 cargo section with the HLS awning section's bay, door and ramp in SEP's door
opening (az +-44.8, the leeward bare steel). SEP's clamshell doors go; their skin, cut at the HLS door's hinge line (HL.CG_HEAD),
becomes the awning door below it and fixed hull above it, and the barrel's sill is cut down to the HLS sill so the ramp clears it.
Cut at build time from the player's own SEP install, like the crew noses; the result is SEP's art, so it is not covered by this
repo's licence (see LICENSE). The part is a ModuleManager copy of SEP_26_SHIP_CARGO (its/patches/STMS_B3_CargoAwning.cfg).
usage: blender -b -P derive_b3cargo.py -- <its/build/mu> <SEP assets>"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh, math
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc
import hls_layout as HL
SEP = sys.argv[sys.argv.index('--') + 2]
OPEN = 44.8                                                  # SEP's door edges; the bay's jambs are on the facet line at 45
az_of = lambda p: math.degrees(math.atan2(p.x, -p.y))
ORIG = {}


def grab(f, want):
    """Import one SEP model and keep the wanted meshes (by importer name) in world space: {name: (bmesh, material, source)}."""
    old = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=os.path.join(SEP, f)); bpy.context.view_layer.update(); got = {}
    for o in [o for o in bpy.data.objects if o not in old]:
        if o.type == 'MESH' and o.name in want:
            me = o.data.copy(); me.transform(o.matrix_world); me.calc_normals_split(); me.calc_loop_triangles()
            ORIG[o.name] = (BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(t.vertices) for t in me.loop_triangles]),
                            [([me.vertices[i].co.copy() for i in t.vertices], [me.loops[l].normal.copy() for l in t.loops]) for t in me.loop_triangles])
            bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
            if o.matrix_world.determinant() < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
            got[o.name] = (bm, o.material_slots[0].material, o.name)
    for o in [o for o in bpy.data.objects if o not in old]: bpy.data.objects.remove(o)
    assert set(got) == set(want), set(want) - set(got)
    return got


def part_of(bm, test):
    b = bm.copy(); bmesh.ops.delete(b, geom=[f for f in b.faces if not test(f.calc_center_median())], context='FACES'); return b


def cut(bm, co, no, test=None):
    fs = [f for f in bm.faces if test is None or test(f)]; geom = set(fs) | {e for f in fs for e in f.edges} | {v for f in fs for v in f.verts}
    bmesh.ops.bisect_plane(bm, geom=list(geom), plane_co=co, plane_no=no, dist=1e-5)


def mend_tiles(bm):
    """SEP's tile mesh steps at every ring seam, and all corners of a step share one UV on the pale grout (see derive_nose.py)."""
    L = bm.loops.layers.uv.active; U, W, S_ = 0.404297, 0.467773, 4 / 4096
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    for f in bm.faces:
        u = [l[L].uv for l in f.loops]
        if abs((u[1] - u[0]).cross(u[2] - u[0])) > 2e-8: continue
        for l, (du, dv) in zip(f.loops, ((-1, -1), (1, -1), (0, 1))): l[L].uv = (U + du * S_, W + dv * S_)


def add(P, nm, bm, mat, src, parent=None, frame=None):
    """A piece of SEP's mesh as one of ours, with SEP's own normals carried over (so the cut edges shade as before)."""
    if not bm.faces: return None
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4]); bm.normal_update(); fr = frame or Matrix(); tr, tris = ORIG[src]; nrm = []
    for f in bm.faces:
        c = f.calc_center_median()
        for l in f.loops:
            h = tr.find_nearest(l.vert.co.lerp(c, .02)); co, ns = tris[h[2]]; w = poly_3d_calc(co, h[0]); nrm.append(sum((n * k for n, k in zip(ns, w)), V()).normalized())
    bm.transform(fr.inverted()); me = bpy.data.meshes.new(nm); bm.to_mesh(me); me.materials.append(mat)
    if me.uv_layers: me.uv_layers[0].active = True; me.uv_layers[0].active_render = True
    for c_ in list(me.color_attributes): me.color_attributes.remove(c_)
    me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(35); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.normals_split_custom_set([tuple(fr.to_3x3().inverted() @ n) for n in nrm])
    o = bpy.data.objects.new(nm, me); P.coll.objects.link(o); P.place(o, fr, parent or P.model); P.meta.setdefault('tris', {})[nm] = sum(len(p.vertices) - 2 for p in me.polygons)
    return o


def hook(P, door, hf):
    S0, H0 = HL.CG_SILL, HL.CG_HEAD
    src = grab('SEP_26_SHIP_CARGO.mu', ['Cylinder∧', 'Cylinder∧.003', 'Cylinder∧.005', 'Cylinder∧.006', 'Nose_7_EXT∧', 'Nose_7_EXT∧.001', 'Nose_7_EXT∧.002', 'Tiles∧', 'Tiles∧.001', 'Tiles∧.002'])
    # the barrel (its name also covers SEP's door and pin pieces, so the patch hides them all): the sill cut down to the HLS sill,
    # the strip above it riding on the door
    bm, m, sn = src['Cylinder∧']; insill = lambda p: abs(az_of(p)) < OPEN + .1 and p.y < 0 and S0 < p.z < 0
    cut(bm, (0, 0, S0), (0, 0, 1), lambda f: abs(az_of(f.calc_center_median())) < OPEN + 4 and f.calc_center_median().y < 0)
    add(P, 'stms_b3barrel', part_of(bm, lambda p: not insill(p)), m, sn); add(P, 'stms_b3doorsill', part_of(bm, insill), m, sn, door, hf)
    bm, m, sn = src['Cylinder∧.006']; add(P, 'stms_b3pin', bm, m, sn)
    for k, s in (('Cylinder∧.003', 'L'), ('Cylinder∧.005', 'R')): bm, m, sn = src[k]; add(P, 'stms_b3doorbarrel' + s, bm, m, sn, door, hf)
    # SEP's door skin up the ogive: below the hinge line it is the door, above it fixed hull
    for k, s in (('Nose_7_EXT∧', 'L'), ('Nose_7_EXT∧.001', 'R')):
        bm, m, sn = src[k]; cut(bm, (0, 0, H0), (0, 0, 1))
        add(P, 'stms_b3doorogive' + s, part_of(bm, lambda p: p.z < H0), m, sn, door, hf); add(P, 'stms_b3noseup' + s, part_of(bm, lambda p: p.z > H0), m, sn)
    for k, s in (('Tiles∧', 'L'), ('Tiles∧.001', 'R')): bm, m, sn = src[k]; mend_tiles(bm); add(P, 'stms_b3doortiles' + s, bm, m, sn, door, hf)
    # SEP's faces are right already: its pieces only block the facing check's rays, with the rest of SEP's skin, which stays in
    # SEP's model, standing in for the white hull of the HLS section while the check runs
    for o in P.coll.objects:
        if o.name.startswith('stms_b3'): o['facing_ok'] = True
    stand = []
    for k in ('Nose_7_EXT∧.002', 'Tiles∧.002'):
        bm, m, sn = src[k]; me = bpy.data.meshes.new('blk'); bm.to_mesh(me); o = bpy.data.objects.new('blk_' + k, me); o['facing_ok'] = True; stand.append(o)
    import facing
    _f = facing.fix_facing
    def fix(objs, *a, **k):
        for o in stand: P.coll.objects.link(o)
        try: _f(list(objs) + stand, *a, **k)
        finally:
            for o in stand: bpy.data.objects.remove(o)
    facing.fix_facing = fix


B3 = dict(name='STMS_B3_CargoAwning', az=45.0, clip='stmsAwning', hook=hook)
exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_hlscargo.py')).read(), 'build_hlscargo.py', 'exec'))

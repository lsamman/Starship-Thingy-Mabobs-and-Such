"""Pieces of SEP's Block 3 nosecone with openings cut in them: the tip as a hinged cap, an EVA hatch, and for the
crew-cargo nose the cargo section's lower barrel with clamshell doors. Cut at build time from the player's own SEP
install, like the expendable masks; the result is SEP's art, so it is never committed (build/ and GameData/ are ignored).
usage: blender -b -P derive_nose.py -- <SEP assets> <build/mu> crew|crewcargo"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from sl import *
from facing import fix_facing
import layout as L, nose as N
V = Vector; SEP, out, variant = sys.argv[sys.argv.index('--') + 1:][:3]; CARGO = variant == 'crewcargo'
NAME = {'crew': 'STMS_B3_HullCrew', 'crewcargo': 'STMS_B3_HullCrewCargo'}[variant]
enable_addon(); clean_scene()


def grab(f, want):
    """Import one SEP model and keep the wanted meshes (by importer name) in world space: {name: (bmesh, material)}."""
    old = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=os.path.join(SEP, f)); bpy.context.view_layer.update(); got = {}
    for o in [o for o in bpy.data.objects if o not in old]:
        if o.type == 'MESH' and o.name in want:
            bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
            if o.matrix_world.determinant() < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
            got[o.name] = (bm, o.material_slots[0].material)
    for o in [o for o in bpy.data.objects if o not in old]: bpy.data.objects.remove(o)
    assert set(got) == set(want), set(want) - set(got)
    return got


def part_of(bm, test):
    b = bm.copy(); bmesh.ops.delete(b, geom=[f for f in b.faces if not test(f.calc_center_median())], context='FACES'); return b
def cut(bm, co, no, test=None):
    fs = [f for f in bm.faces if test is None or test(f)]; geom = set(fs) | {e for f in fs for e in f.edges} | {v for f in fs for v in f.verts}
    bmesh.ops.bisect_plane(bm, geom=list(geom), plane_co=co, plane_no=no, dist=1e-5)
az_of = lambda p: math.degrees(math.atan2(p.x, -p.y))


src = grab('SEP_26_SHIP_NOSECONE.mu', ['Nose_7_EXT∧', 'Tiles∧', 'Tiles∧.001'] + (['Cylinder∧.002'] if CARGO else []))
if CARGO: car = grab('SEP_26_SHIP_CARGO.mu', ['Cylinder∧', 'Cylinder∧.001', 'Cylinder∧.002', 'Cylinder∧.003', 'Cylinder∧.004', 'Cylinder∧.005'])
P = Part(NAME); ANIM = {}
def add(nm, bm, mat, parent=None, frame=None):
    if not bm.faces: return None
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4]); bm.normal_update(); fr = frame or Matrix(); bm.transform(fr.inverted())
    me = bpy.data.meshes.new(nm); bm.to_mesh(me); me.materials.append(mat)
    if me.uv_layers: me.uv_layers[0].active = True; me.uv_layers[0].active_render = True
    for c_ in list(me.color_attributes): me.color_attributes.remove(c_)
    me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(35); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    o = bpy.data.objects.new(nm, me); P.coll.objects.link(o); P.place(o, fr, parent or P.model); P.meta.setdefault('tris', {})[nm] = sum(len(p.vertices) - 2 for p in me.polygons); return o


def climb_frame(pos, out):
    z = V((0, 0, 1)); y = -V(out).normalized(); m = Matrix((y.cross(z), y, z)).transposed().to_4x4(); m.translation = V(pos); return m


ZC = L.CAP_Z; hz0, hz1 = L.EVA_Z; ha = L.EVA_HW
nose, mnose = src['Nose_7_EXT∧']; cut(nose, (0, 0, ZC), (0, 0, 1))
front = lambda f: f.calc_center_median().y < -1.5 and 0 < f.calc_center_median().z < 2.6
for a in (-ha, ha): t = math.radians(a); cut(nose, (0, 0, 0), (math.cos(t), math.sin(t), 0), front)
for z in (hz0, hz1): cut(nose, (0, 0, z), (0, 0, 1), front)
indoor = lambda p: p.y < 0 and abs(az_of(p)) < ha and hz0 < p.z < hz1
add('stms_nose', part_of(nose, lambda p: p.z < ZC and not indoor(p)), mnose)
R0 = N.ring_r(ZC); hinge = T(0, R0 + .02, ZC); cap = P.empty('stms_cap', hinge, P.model); add('stms_capskin', part_of(nose, lambda p: p.z > ZC), mnose, cap, hinge)
for k in ('Tiles∧', 'Tiles∧.001'):
    bm, m = src[k]
    if k == 'Tiles∧.001': cut(bm, (0, 0, ZC), (0, 0, 1))
    else:                                                # the two small patches stay clear of the hatch
        assert min(abs(az_of(v.co)) for v in bm.verts) > ha + 1
    n_ = 'B' if k[-1] == '1' else 'A'; add('stms_tiles' + n_, part_of(bm, lambda p: p.z < ZC), m); add('stms_captiles' + n_, part_of(bm, lambda p: p.z > ZC), m, cap, hinge)
# EVA hatch: pulled out a touch and swung aside on two arms
hx = math.sin(math.radians(ha)) * N.ring_r(sum(L.EVA_Z) / 2); hh = T(hx + .04, -N.ring_r(sum(L.EVA_Z) / 2) * math.cos(math.radians(ha)) - .03, sum(L.EVA_Z) / 2); door = P.empty('stms_evahatch', hh, P.model)
add('stms_evaskin', part_of(nose, indoor), mnose, door, hh)
MD = P.material('its_det', spec=(.8, .8, .8), shininess=.45); 
DET = dict(white=(0, 0, 512, 512), grey=(512, 0, 512, 512), steel=(1536, 0, 512, 512), dark=(0, 512, 512, 512), alu=(512, 512, 512, 512), black=(1024, 512, 512, 512), wall=(0, 1024, 1024, 512), deck=(1024, 1024, 512, 512), hatch=(1536, 1280, 512, 256), stripe=(1536, 1024, 512, 256), lamp=(1024, 1920, 256, 128))
Z = {k: Zone(*v, atlas=2048, ppm=170) for k, v in DET.items()}
def quad(g, pts, zn, toward):
    n = len(g.v); g.v += [tuple(p) for p in pts]; a, b, c = [V(p) for p in pts[:3]]; nrm = (b - a).cross(c - a); cen = sum((V(p) for p in pts), V()) / 4; idx = list(range(n, n + 4)); uv = [zn.uv(*t) for t in ((0, 0), (1, 0), (1, 1), (0, 1))]
    if nrm.dot(V(toward) - cen) < 0: idx, uv = idx[::-1], uv[::-1]
    g.face(idx, uv)
# ---------------- seat for a docking port under the cap
d = Geo(); d.add(lathe([(R0 - .004, ZC), (R0 - .05, ZC), (R0 - .055, ZC - .03), (.40, ZC - .03)], 64, zone=Z['grey'])); d.add(lathe([(.40, ZC - .03), (.385, ZC - .022), (0, ZC - .022)], 48, zone=Z['alu'])); d.add(box(.34, .10, .07, zone=Z['dark'], bevel=.015), T(0, R0 - .10, ZC - .005))
bl = cyl(.016, .014, 6, zone=Z['steel'], center_z=False); [d.add(bl, T(.62 * math.cos(TAU * k / 24), .62 * math.sin(TAU * k / 24), ZC - .03)) for k in range(24)]
ci = Geo(); ci.add(lathe([(R0 - .006, ZC + .004), (R0 - .06, ZC + .004), (R0 - .10, ZC + .06), (.72, ZC + .34), (.48, ZC + .72), (.2, ZC + 1.0), (0, ZC + 1.05)], 48, zone=Z['wall'], flip=True)); ci.add(box(.5, .10, .09, zone=Z['dark'], bevel=.015), T(0, R0 - .05, ZC + .05)); P.mesh('stms_capin', ci, MD, parent=cap, frame=hinge)
P.node('port', (0, 0, ZC - .022), (0, 0, 1), 1)
# ---------------- EVA airlock: a real recess with an inner hatch
yf = -N.ring_r(hz0) + .02; yb = -1.95; X = math.sin(math.radians(ha)) * 2.70; zm = (hz0 + hz1) / 2
for (z, tw) in ((hz0, 9), (hz1, -9)): quad(d, [(-X, yf - .04, z), (X, yf - .04, z), (X, yb, z), (-X, yb, z)], Z['deck'] if tw > 0 else Z['white'], (0, yb, z + tw))
for s in (-1, 1): quad(d, [(s * X, yf - .04, hz0), (s * X, yf - .04, hz1), (s * X, yb, hz1), (s * X, yb, hz0)], Z['white'], (0, yf, zm))
quad(d, [(-X, yb, hz0), (X, yb, hz0), (X, yb, hz1), (-X, yb, hz1)], Z['white'], (0, -9, zm))
BF = Matrix(((1, 0, 0, 0), (0, 0, -1, yb), (0, 1, 0, zm), (0, 0, 0, 1))); d.add(rounded_rect_ring(.56, .98, .14, .06, .05, 6, zone=Z['alu']), BF); d.add(quad_patch(.46, .88, Z['hatch']), BF @ T(0, 0, .02)); d.add(tube([tuple(BF @ V((.10 * math.cos(t), .10 * math.sin(t), .05))) for t in np.linspace(0, TAU, 21)], .012, 6, zone=Z['steel']))
d.add(rounded_rect_ring(2 * X + .10, hz1 - hz0 + .10, .03, .05, .03, 2, zone=Z['alu']), Matrix(((1, 0, 0, 0), (0, 0, -1, yf + .02), (0, 1, 0, zm), (0, 0, 0, 1))))
di = Geo(); fr_ = [N.point(a, z, -.05) for z in (hz0 + .02, hz1 - .02) for a in (-ha + .3, ha - .3)]; quad(di, [fr_[0], fr_[1], fr_[3], fr_[2]], Z['white'], (0, 0, zm)); di.add(box(.10, .05, .9, zone=Z['alu'], bevel=.01), T(hx - .06, -2.62, zm)); [di.add(box(.16, .06, .06, zone=Z['dark'], bevel=.01), T(hx - .02, -2.66, zm + q)) for q in (-.35, .35)]; di.add(tube([tuple(N.point(-ha + 1.2, zm + q, .03)) for q in (-.12, 0, .12)], .014, 6, zone=Z['black'])); di.add(tube([tuple(N.point(0, zm - .25, .035)), tuple(N.point(0, zm + .05, .035))], .012, 6, zone=Z['black']))
P.mesh('stms_evain', di, MD, parent=door, frame=hh)
q0, q1 = P.rest_quat(cap), P.rest_quat(door)
for f, a in ((0, 0), (90, -125)): P.key('stmsCap', cap, f, rotation_quaternion=q0 @ Quaternion((1, 0, 0), math.radians(a)))
for f, a in ((0, 0), (60, 130)): P.key('stmsEva', door, f, rotation_quaternion=q1 @ Quaternion((0, 0, 1), math.radians(a)))
P.box_trigger('stms_airlock', climb_frame((0, yb - .22, zm), (0, -1, 0)), (.5, .4, .9), 'Airlock').muproperties.layer = 21
# ---------------- cargo bay: the cargo section's barrel and lower clamshells
if CARGO:
    for nm, k in (('stms_barrel', 'Cylinder∧'), ('stms_barrelin', 'Cylinder∧.001')): bm, m = car[k]; add(nm, bm, m)
    bm, m = src['Cylinder∧.002']; add('stms_pin', bm, m)
    for s, ks in ((-1, ('Cylinder∧.002', 'Cylinder∧.003')), (1, ('Cylinder∧.004', 'Cylinder∧.005'))):
        xh = s * 1.989; fr = T(xh, -1.989, -1.28); dr = P.empty('stms_door%d' % (s > 0), fr, P.model)
        for j, k in enumerate(ks): bm, m = car[k]; add('stms_door%d_%d' % (s > 0, j), bm, m, dr, fr)
        g = Geo()                                        # stiffeners, and the top edge the cargo section's upper door used to close
        for z in (-2.3, -1.7, -1.1, -.5): g.add(tube([(2.70 * math.sin(t), -2.70 * math.cos(t), z) for t in np.linspace(s * .03, s * .76, 14)], .035, 6, zone=Z['alu']))
        g.add(lathe([(2.80, 0), (2.60, 0), (2.60, -.06)], 12, *((1, 44) if s > 0 else (-44, -1)), zone=Z['alu'], flip=True)); P.mesh('stms_doorrib%d' % (s > 0), g, MD, parent=dr, frame=fr)
        q = P.rest_quat(dr)
        for f, a in ((0, 0), (120, 118 * s)): P.key('stmsDoors', dr, f, rotation_quaternion=q @ Quaternion((0, 0, 1), math.radians(a)))
        P.hull_collider('col_door%d' % (s > 0), [(r * math.sin(t), -r * math.cos(t), z) for r in (2.72, 2.81) for t in (s * .02, s * .26, s * .5, s * .76) for z in (-2.5, -.02)], parent=dr, frame=fr)
    d.add(lathe([(2.76, -.03), (2.76, -.10), (2.4, -.13), (0, -.13)], 72, zone=Z['wall'], flip=True))      # bulkhead under the cabin
    for a in range(60, 301, 20): d.add(box(.06, .10, 2.35, zone=Z['alu'], bevel=.01), on_cyl(a, -1.28, 2.70) @ Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1))))
    for z in (-2.2, -1.3, -.4): d.add(lathe([(2.76, z - .03), (2.66, z - .03), (2.66, z + .03), (2.76, z + .03)], 60, 48, 312, zone=Z['alu'], flip=True))
    d.add(lathe([(2.74, -2.5), (2.74, -.1)], 72, 47, 313, zone=Z['wall'], flip=True))
    for s in (-1, 1): d.add(box(.6, .10, .03, zone=Z['lamp']), T(s * .9, 0, -.15)); add_spot(P, 'stms_baylight', (s * .9, 0, -.18), (0, 0, -1), power=260, angle=120, reach=6)
    P.node('cargo', (0, 0, -2.5159), (0, 0, 1), 3); P.node('cargotop', (0, 0, -.15), (0, 0, -1), 2)
P.mesh('stms_details', d, MD, smooth_angle=35)
# ---------------- colliders in place of SEP's, which would close the openings
def rp(z, a0, a1, n, r=None): return [(rr * math.sin(math.radians(a)), -rr * math.cos(math.radians(a)), z) for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)] for rr in ([r] if r else [N.ring_r(z)])]
zlo = 0.0 if CARGO else -3.412
for j, (a0, a1) in enumerate(((ha, 60), (60, 120), (120, 180), (180, 240), (240, 300), (300, 360 - ha))):
    for i, (z0, z1) in enumerate(((zlo, 1.0), (1.0, 2.581)) if zlo > -1 else ((zlo, 0.0), (0.0, 2.581))): P.hull_collider(f'col_{j}{i}', [p for z in (z0, z1) for p in rp(z, a0, a1, 4) + rp(z, a0, a1, 4, 1.9)])
P.hull_collider('col_sill', [p for z in (zlo, hz0) for p in rp(z, -ha, ha, 2) + rp(z, -ha, ha, 2, 1.9)]); P.hull_collider('col_lintel', [p for z in (hz1, 2.581) for p in rp(z, -ha, ha, 2) + rp(z, -ha, ha, 2, 1.9)]); P.hull_collider('col_back', [(x, y, z) for x in (-X, X) for y in (yb, yb + .1) for z in (hz0, hz1)])
for i, (z0, z1) in enumerate(((2.581, 4.132), (4.132, 5.307), (5.307, 6.234), (6.234, ZC - .03))): P.hull_collider(f'col_n{i}', rp(z0, 0, 345, 23) + rp(z1, 0, 345, 23))
P.hull_collider('col_cap', [p for z in (ZC + .02, 7.93, 8.4) for p in rp(z, 0, 330, 11)] + [(0, 0, 8.55)], parent=cap, frame=hinge); P.hull_collider('col_evahatch', [tuple(N.point(a, z, o)) for a in (-ha, ha) for z in (hz0, hz1) for o in (0, -.05)], parent=door, frame=hh)
if CARGO:
    for j in range(5):
        a0, a1 = 46 + 53.6 * j, 46 + 53.6 * (j + 1); P.hull_collider(f'col_b{j}', [p for z in (-3.412, 0) for p in rp(z, a0, a1, 4, 2.8125) + rp(z, a0, a1, 4, 2.70)])
    P.hull_collider('col_floor', rp(-3.412, 0, 345, 23, 2.8) + rp(-2.53, 0, 345, 23, 2.7)); P.hull_collider('col_roof', rp(-.13, 0, 345, 23, 2.75) + rp(0, 0, 345, 23, 2.75))
else: P.hull_collider('col_floor', rp(-3.412, 0, 345, 23, 2.8) + rp(-2.53, 0, 345, 23, 2.7))
P.bake_clips(0); ours = [o for o in P.coll.objects if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.material_slots and o.material_slots[0].material == MD]
fix_facing(ours, [0, 120]); P.two_sided = True
import facing; _f = facing.fix_facing; facing.fix_facing = lambda *a, **k: None      # SEP's own faces are right already
P.export(out); facing.fix_facing = _f; P.save_blend(out)

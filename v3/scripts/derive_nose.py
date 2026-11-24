"""Pieces of SEP's Block 3 nosecone with openings cut in them: a side docking bay with a sliding door, an EVA hatch, and for the
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


ORIG = {}
def remember(nm, o):
    me = o.data.copy(); me.transform(o.matrix_world); me.calc_normals_split(); me.calc_loop_triangles()
    tri = [tuple(t.vertices) for t in me.loop_triangles]; from mathutils.bvhtree import BVHTree
    ORIG[nm] = (BVHTree.FromPolygons([v.co.copy() for v in me.vertices], tri), [([me.vertices[i].co.copy() for i in t.vertices], [me.loops[l].normal.copy() for l in t.loops]) for t in me.loop_triangles])


def grab(f, want):
    """Import one SEP model and keep the wanted meshes (by importer name) in world space: {name: (bmesh, material)}."""
    old = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=os.path.join(SEP, f)); bpy.context.view_layer.update(); got = {}
    for o in [o for o in bpy.data.objects if o not in old]:
        if o.type == 'MESH' and o.name in want:
            remember(f[:14] + o.name, o)
            bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
            if o.matrix_world.determinant() < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
            got[o.name] = (bm, o.material_slots[0].material, f[:14] + o.name)
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
def add(nm, bm, mat, parent=None, frame=None, src_=None, move=None):
    if not bm.faces: return None
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4]); bm.normal_update(); fr = frame or Matrix(); nrm = None
    if src_:
        from mathutils.interpolate import poly_3d_calc
        tr, tris = ORIG[src_]; nrm = []
        for f in bm.faces:
            c = f.calc_center_median()
            for l in f.loops:
                h = tr.find_nearest(l.vert.co.lerp(c, .02))          # a hair inside the face, so a seam picks its own side
                co, ns = tris[h[2]]; w = poly_3d_calc(co, h[0]); nrm.append(sum((n * k for n, k in zip(ns, w)), V()).normalized())
    if move:
        for v in bm.verts: v.co = move(v.co.copy())
    bm.transform(fr.inverted())
    me = bpy.data.meshes.new(nm); bm.to_mesh(me); me.materials.append(mat)
    if me.uv_layers: me.uv_layers[0].active = True; me.uv_layers[0].active_render = True
    for c_ in list(me.color_attributes): me.color_attributes.remove(c_)
    me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(35); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    if nrm: me.normals_split_custom_set([tuple(fr.to_3x3().inverted() @ n) for n in nrm])
    o = bpy.data.objects.new(nm, me); P.coll.objects.link(o); P.place(o, fr, parent or P.model); P.meta.setdefault('tris', {})[nm] = sum(len(p.vertices) - 2 for p in me.polygons); return o


def climb_frame(pos, out):
    z = V((0, 0, 1)); y = -V(out).normalized(); m = Matrix((y.cross(z), y, z)).transposed().to_4x4(); m.translation = V(pos); return m


hz0, hz1 = L.EVA_Z; ha = L.EVA_HW; D = L.DOCK; da, dw = D['az'], D['hw']; dz0, dz1 = D['z']; dzm = (dz0 + dz1) / 2
nose, mnose, snose = src['Nose_7_EXT∧']
def box_cut(a0, a1, z0, z1):
    def near(f): c = f.calc_center_median(); return c.y < 0 and z0 - 1.0 < c.z < z1 + 1.0 and a0 - 4.5 < az_of(c) < a1 + 4.5
    for a in (a0, a1): t = math.radians(a); cut(nose, (0, 0, 0), (math.cos(t), math.sin(t), 0), near)
    for z in (z0, z1): cut(nose, (0, 0, z), (0, 0, 1), near)
box_cut(-ha, ha, hz0, hz1); box_cut(da - dw, da + dw, dz0, dz1)
indoor = lambda p: p.y < 0 and abs(az_of(p)) < ha and hz0 < p.z < hz1
indock = lambda p: p.y < 0 and abs(az_of(p) - da) < dw and dz0 < p.z < dz1
add('stms_nose', part_of(nose, lambda p: not indoor(p) and not indock(p)), mnose, src_=snose)
for k in ('Tiles∧', 'Tiles∧.001'):                          # the small patch that would sit on the docking door goes
    bm, m, sn = src[k]; add('stms_tiles' + ('B' if k[-1] == '1' else 'A'), bm if k[-1] == '1' else part_of(bm, lambda p: p.x < 0), m, src_=sn)
# EVA hatch: swung aside on its arms
hx = math.sin(math.radians(ha)) * N.ring_r(sum(L.EVA_Z) / 2); hh = T(hx + .04, -N.ring_r(sum(L.EVA_Z) / 2) * math.cos(math.radians(ha)) - .03, sum(L.EVA_Z) / 2); door = P.empty('stms_evahatch', hh, P.model)
add('stms_evaskin', part_of(nose, indoor), mnose, door, hh, src_=snose)
# docking door: the skin itself, pressed outward over the port so the port fits behind it; it moves out, then slides round the hull
DF = N.surf(da, dzm); out_ = V((math.sin(math.radians(da)), -math.cos(math.radians(da)), 0)); tan_ = V((math.cos(math.radians(da)), math.sin(math.radians(da)), 0)); HWm = 2.755 * math.sin(math.radians(dw)); HHm = (dz1 - dz0) / 2
sm = lambda t: max(0, min(1, t)) ** 2 * (3 - 2 * max(0, min(1, t)))
bump = lambda p: D['bulge'] * sm((HWm - abs(p.dot(tan_))) / .20) * sm((HHm - abs(p.z - dzm)) / .20)
press = lambda p: p + out_ * bump(p); dslide = P.empty('stms_dockturn', None, P.model); dpanel = P.empty('stms_dockdoor', None, dslide)
dk = part_of(nose, indock)
for a in [da - dw + 2 * dw * k / 12 for k in range(1, 12)]: t = math.radians(a); cut(dk, (0, 0, 0), (math.cos(t), math.sin(t), 0))
for k in range(1, 12): cut(dk, (0, 0, dz0 + (dz1 - dz0) * k / 12), (0, 0, 1))
add('stms_dockskin', dk, mnose, dpanel, src_=None, move=press)
MD = P.material('its_det', spec=(.8, .8, .8), shininess=.45); 
DET = dict(white=(0, 0, 512, 512), grey=(512, 0, 512, 512), steel=(1536, 0, 512, 512), dark=(0, 512, 512, 512), alu=(512, 512, 512, 512), black=(1024, 512, 512, 512), wall=(0, 1024, 1024, 512), deck=(1024, 1024, 512, 512), hatch=(1536, 1280, 512, 256), stripe=(1536, 1024, 512, 256), lamp=(1024, 1920, 256, 128))
Z = {k: Zone(*v, atlas=2048, ppm=170) for k, v in DET.items()}
def quad(g, pts, zn, toward):
    n = len(g.v); g.v += [tuple(p) for p in pts]; a, b, c = [V(p) for p in pts[:3]]; nrm = (b - a).cross(c - a); cen = sum((V(p) for p in pts), V()) / 4; idx = list(range(n, n + 4)); uv = [zn.uv(*t) for t in ((0, 0), (1, 0), (1, 1), (0, 1))]
    if nrm.dot(V(toward) - cen) < 0: idx, uv = idx[::-1], uv[::-1]
    g.face(idx, uv)
# ---------------- docking bay: a lined recess with a flat seat and a node
d = Geo(); RP = D['plate']; SF = Matrix((tan_, V((0, 0, 1)), out_)).transposed().to_4x4(); SF.translation = out_ * RP + V((0, 0, dzm))      # +X along the hull, +Y up, +Z out
PX, PY = .66, HHm
edge = [(da - dw + 2 * dw * k / 8, dz0) for k in range(9)] + [(da + dw, dz0 + (dz1 - dz0) * k / 4) for k in range(1, 4)] + [(da + dw - 2 * dw * k / 8, dz1) for k in range(9)] + [(da - dw, dz1 - (dz1 - dz0) * k / 4) for k in range(1, 4)]
for (a0, z0), (a1, z1) in zip(edge, edge[1:] + edge[:1]):
    p, q = N.point(a0, z0, -.006), N.point(a1, z1, -.006); fl = lambda v: SF @ V((max(-PX, min(PX, (SF.inverted() @ v).x)), (SF.inverted() @ v).y, 0)); quad(d, [p, q, fl(q), fl(p)], Z['grey'], out_ * 2.7 + V((0, 0, dzm)))
quad(d, [SF @ V((x, y, 0)) for x, y in ((-PX, -PY), (PX, -PY), (PX, PY), (-PX, PY))], Z['grey'], out_ * 9)
d.add(lathe([(.62, -.002), (.60, .016), (.50, .016), (.48, .006), (0, .006)][::-1], 56, zone=Z['alu'], flip=True), SF)
bl = cyl(.014, .012, 6, zone=Z['steel'], center_z=False); [d.add(bl, SF @ T(.55 * math.cos(TAU * k / 24), .55 * math.sin(TAU * k / 24), .015)) for k in range(24)]
for sx in (-1, 1):
    for sy in (-1, 1): d.add(box(.12, .10, .06, zone=Z['dark'], bevel=.012), SF @ T(sx * .56, sy * .56, .03)); d.add(box(.07, .05, .02, zone=Z['lamp']), SF @ T(sx * .56, sy * .56, .065))
for z in (dz0 + .06, dz1 - .06):                            # tracks the door rides on
    d.add(tube([tuple(N.point(a, z, .012)) for a in np.linspace(da + dw + .6, da + dw * 3 + .4, 16)], .016, 6, zone=Z['dark']))
fr_e = [N.point(a, z, .008) for a, z in edge]; d.add(tube([tuple(p) for p in fr_e], .020, 6, zone=Z['alu'], closed=True, caps=False))
di2 = Geo(); gx, gy = 12, 12; grid = {}
for i_ in range(gx + 1):
    for j_ in range(gy + 1): p = N.point(da - dw + .25 + (2 * dw - .5) * i_ / gx, dz0 + .01 + (dz1 - dz0 - .02) * j_ / gy, 0); grid[i_, j_] = len(di2.v); di2.v.append(tuple(press(p) - out_ * .045))
for i_ in range(gx):
    for j_ in range(gy): di2.face([grid[i_, j_], grid[i_, j_ + 1], grid[i_ + 1, j_ + 1], grid[i_ + 1, j_]], [Z['white'].uv(u / gx, v / gy) for u, v in ((i_, j_), (i_, j_ + 1), (i_ + 1, j_ + 1), (i_ + 1, j_))])
rim_i = [(i_, 0) for i_ in range(gx)] + [(gx, j_) for j_ in range(gy)] + [(i_, gy) for i_ in range(gx, 0, -1)] + [(0, j_) for j_ in range(gy, 0, -1)]
rp_ = lambda i_, j_: N.point(da - dw + 2 * dw * i_ / gx, dz0 + (dz1 - dz0) * j_ / gy, 0)
for (a_, b_), (c_, e_) in zip(rim_i, rim_i[1:] + rim_i[:1]): quad(di2, [rp_(a_, b_), rp_(c_, e_), V(di2.v[grid[c_, e_]]), V(di2.v[grid[a_, b_]])], Z['alu'], (rp_(a_, b_) - out_ * .02) * 2 - (out_ * 2.7 + V((0, 0, dzm))))
P.mesh('stms_dockin', di2, MD, parent=dpanel)
NP_ = SF @ V((0, 0, .016)); P.node('port', NP_, out_, 1); print('NODE %.4f %.4f %.4f dir %.4f %.4f %.4f' % (NP_.x, NP_.z, NP_.y, out_.x, out_.z, out_.y))
# ---------------- EVA airlock: a real recess with an inner hatch
zm_ = 0; yf = -N.ring_r(hz0) + .02; yb = -1.95; X = math.sin(math.radians(ha)) * 2.70; zm = (hz0 + hz1) / 2
for (z, tw) in ((hz0, 9), (hz1, -9)): quad(d, [(-X, yf - .04, z), (X, yf - .04, z), (X, yb, z), (-X, yb, z)], Z['deck'] if tw > 0 else Z['white'], (0, yb, z + tw))
for s in (-1, 1): quad(d, [(s * X, yf - .04, hz0), (s * X, yf - .04, hz1), (s * X, yb, hz1), (s * X, yb, hz0)], Z['white'], (0, yf, zm))
quad(d, [(-X, yb, hz0), (X, yb, hz0), (X, yb, hz1), (-X, yb, hz1)], Z['white'], (0, -9, zm))
BF = Matrix(((1, 0, 0, 0), (0, 0, -1, yb), (0, 1, 0, zm), (0, 0, 0, 1))); d.add(rounded_rect_ring(.56, .98, .14, .06, .05, 6, zone=Z['alu']), BF); d.add(quad_patch(.46, .88, Z['hatch']), BF @ T(0, 0, .02)); d.add(tube([tuple(BF @ V((.10 * math.cos(t), .10 * math.sin(t), .05))) for t in np.linspace(0, TAU, 21)], .012, 6, zone=Z['steel']))
d.add(rounded_rect_ring(2 * X + .10, hz1 - hz0 + .10, .03, .05, .03, 2, zone=Z['alu']), Matrix(((1, 0, 0, 0), (0, 0, -1, yf + .02), (0, 1, 0, zm), (0, 0, 0, 1))))
di = Geo(); ea = [(-ha, hz0), (ha, hz0), (ha, hz1), (-ha, hz1)]; nE = 6; ring_ = []
for (a0, z0), (a1, z1) in zip(ea, ea[1:] + ea[:1]): ring_ += [(a0 + (a1 - a0) * k / nE, z0 + (z1 - z0) * k / nE) for k in range(nE)]
cI = N.point(0, zm, -.09)
for p, q in zip(ring_, ring_[1:] + ring_[:1]):              # rim and back of the door
    A_, B_ = N.point(*p), N.point(*q); C_, E_ = [N.point(a * .94, zm + (z - zm) * .97, -.09) for a, z in (q, p)]; quad(di, [A_, B_, C_, E_], Z['white'], (A_ - N.point(0, zm, -.04)) * 3 + N.point(0, zm, -.04)); n = len(di.v); di.v += [tuple(E_), tuple(C_), tuple(cI)]; di.face([n, n + 1, n + 2] if (C_ - E_).cross(cI - E_).y > 0 else [n + 1, n, n + 2], [Z['white'].uv(*t) for t in ((0, 0), (.1, 0), (.05, .1))])
for q in (-.36, .36): di.add(box(.15, .09, .07, zone=Z['dark'], bevel=.012), T(hx - .01, -2.695, zm + q))
di.add(tube([tuple(N.point(-ha + 1.3, zm + q, .03)) for q in (-.12, 0, .12)], .014, 6, zone=Z['black'])); di.add(tube([(.10 * math.cos(t), cI.y + .012, zm + .10 * math.sin(t)) for t in np.linspace(0, TAU, 21)], .012, 6, zone=Z['steel']))
P.mesh('stms_evain', di, MD, parent=door, frame=hh)
q1, q2 = P.rest_quat(door), P.rest_quat(dslide); END = 100
for f, a in ((0, 0), (60, 130)): P.key('stmsEva', door, f, rotation_quaternion=q1 @ Quaternion((0, 0, 1), math.radians(a)))
for f, l in ((0, V()), (30, out_ * .15), (END, out_ * .15)): P.key('stmsDock', dpanel, f, location=l)
for f, a in ((0, 0), (30, 0), (END, 2 * dw + 1.2)): P.key('stmsDock', dslide, f, rotation_quaternion=q2 @ Quaternion((0, 0, 1), math.radians(a)))
P.box_trigger('stms_airlock', climb_frame((0, yb - .22, zm), (0, -1, 0)), (.5, .4, .9), 'Airlock').muproperties.layer = 21
# ---------------- cargo bay: the cargo section's barrel and lower clamshells
if CARGO:
    for nm, k in (('stms_barrel', 'Cylinder∧'), ('stms_barrelin', 'Cylinder∧.001')): bm, m, sn = car[k]; add(nm, bm, m, src_=sn)
    bm, m, sn = src['Cylinder∧.002']; add('stms_pin', bm, m, src_=sn)
    for s, ks in ((-1, ('Cylinder∧.002', 'Cylinder∧.003')), (1, ('Cylinder∧.004', 'Cylinder∧.005'))):
        xh = s * 1.989; fr = T(xh, -1.989, -1.28); dr = P.empty('stms_door%d' % (s > 0), fr, P.model)
        for j, k in enumerate(ks): bm, m, sn = car[k]; add('stms_door%d_%d' % (s > 0, j), bm, m, dr, fr, src_=sn)
        g = Geo()                                        # stiffeners, and the top edge the cargo section's upper door used to close
        for z in (-2.3, -1.7, -1.1, -.5): g.add(tube([(2.765 * math.sin(t), -2.765 * math.cos(t), z) for t in np.linspace(s * .03, s * .76, 14)], .03, 6, zone=Z['alu']))
        P.mesh('stms_doorrib%d' % (s > 0), g, MD, parent=dr, frame=fr)
        q = P.rest_quat(dr)
        for f, a in ((0, 0), (120, 118 * s)): P.key('stmsDoors', dr, f, rotation_quaternion=q @ Quaternion((0, 0, 1), math.radians(a)))
        P.hull_collider('col_door%d' % (s > 0), [(r * math.sin(t), -r * math.cos(t), z) for r in (2.72, 2.81) for t in (s * .02, s * .26, s * .5, s * .76) for z in (-2.5, -.02)], parent=dr, frame=fr)
    d.add(lathe([(2.806, .01), (2.806, -.02), (2.74, -.02), (2.74, -.10), (2.4, -.13), (0, -.13)], 96, zone=Z['wall'], flip=True))      # bulkhead under the cabin
    for a in range(60, 301, 20): d.add(box(.06, .10, 2.35, zone=Z['alu'], bevel=.01), on_cyl(a, -1.28, 2.738) @ Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1))))
    for z in (-2.2, -1.3, -.4): d.add(lathe([(2.785, z - .03), (2.69, z - .03), (2.69, z + .03), (2.785, z + .03)], 60, 48, 312, zone=Z['alu'], flip=True))
    for s in (-1, 1): d.add(box(.6, .10, .03, zone=Z['lamp']), T(s * .9, 0, -.15)); add_spot(P, 'stms_baylight', (s * .9, 0, -.18), (0, 0, -1), power=260, angle=120, reach=6)
    P.node('cargo', (0, 0, -2.5159), (0, 0, 1), 3); P.node('cargotop', (0, 0, -.15), (0, 0, -1), 2)
P.mesh('stms_details', d, MD, smooth_angle=35)
# ---------------- colliders in place of SEP's, which would close the openings
def rp(z, a0, a1, n, r=None): return [(rr * math.sin(math.radians(a)), -rr * math.cos(math.radians(a)), z) for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)] for rr in ([r] if r else [N.ring_r(z)])]
zlo = 0.0 if CARGO else -3.412
A0, A1 = da - dw, da + dw
for j, (a0, a1) in enumerate(((ha, A0), (A1, 90), (90, 140), (140, 190), (190, 240), (240, 300), (300, 360 - ha))):
    for i, (z0, z1) in enumerate(((zlo, dz0), (dz0, dz1), (dz1, 2.581))): P.hull_collider(f'col_{j}{i}', [p for z in (z0, z1) for p in rp(z, a0, a1, 4) + rp(z, a0, a1, 4, 1.9)])
for i, (z0, z1) in enumerate(((zlo, dz0), (dz1, 2.581))): P.hull_collider(f'col_dock{i}', [p for z in (z0, z1) for p in rp(z, A0, A1, 4) + rp(z, A0, A1, 4, 1.9)])
P.hull_collider('col_seat', [tuple(SF @ V((x, y, z))) for x in (-PX, PX) for y in (-PY, PY) for z in (0, -.12)]); P.hull_collider('col_dockdoor', [tuple(press(N.point(a, z, 0)) - out_ * o) for a in (A0, da - 4, da + 4, A1) for z in (dz0, dzm - .25, dzm + .25, dz1) for o in (0, .045)], parent=dpanel)
P.hull_collider('col_sill', [p for z in (zlo, hz0) for p in rp(z, -ha, ha, 2) + rp(z, -ha, ha, 2, 1.9)]); P.hull_collider('col_lintel', [p for z in (hz1, 2.581) for p in rp(z, -ha, ha, 2) + rp(z, -ha, ha, 2, 1.9)]); P.hull_collider('col_back', [(x, y, z) for x in (-X, X) for y in (yb, yb + .1) for z in (hz0, hz1)])
for i, (z0, z1) in enumerate(((2.581, 4.132), (4.132, 5.307), (5.307, 6.234), (6.234, 7.2794), (7.2794, 8.5528))): P.hull_collider(f'col_n{i}', rp(z0, 0, 345, 23) + rp(z1, 0, 345, 23))
P.hull_collider('col_evahatch', [tuple(N.point(a, z, o)) for a in (-ha, ha) for z in (hz0, hz1) for o in (0, -.05)], parent=door, frame=hh)
if CARGO:
    for j in range(5):
        a0, a1 = 46 + 53.6 * j, 46 + 53.6 * (j + 1); P.hull_collider(f'col_b{j}', [p for z in (-3.412, 0) for p in rp(z, a0, a1, 4, 2.8125) + rp(z, a0, a1, 4, 2.70)])
    P.hull_collider('col_floor', rp(-3.412, 0, 345, 23, 2.8) + rp(-2.53, 0, 345, 23, 2.7)); P.hull_collider('col_roof', rp(-.13, 0, 345, 23, 2.75) + rp(0, 0, 345, 23, 2.75))
else: P.hull_collider('col_floor', rp(-3.412, 0, 345, 23, 2.8) + rp(-2.53, 0, 345, 23, 2.7))
P.bake_clips(0); ours = [o for o in P.coll.objects if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.material_slots and o.material_slots[0].material == MD]
fix_facing(ours, [0, 120]); P.two_sided = True
import facing; _f = facing.fix_facing; facing.fix_facing = lambda *a, **k: None      # SEP's own faces are right already
P.export(out); facing.fix_facing = _f; P.save_blend(out)

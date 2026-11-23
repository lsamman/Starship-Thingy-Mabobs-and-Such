"""HLS clearances on the built models: legs stowed and out, the elevator folded behind the shut door and along its travel,
solar packages behind their hatches, the nose port clear of the rim. usage: blender -b -P check_hls.py -- build/mu [SEP assets]"""
import bpy, sys, os, math, addon_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
import hls_layout as HL
addon_utils.enable('io_object_mu', default_set=True)
MU = sys.argv[sys.argv.index('--') + 1]; SEP = (sys.argv[sys.argv.index('--') + 2:] + [''])[0]; sc = bpy.context.scene; bad = 0
def ok(c, m):
    global bad; bad += not c; print('ok   ' if c else 'FAIL ', m)
base = lambda o: o.name.split('∧')[0].split('.')[0]
def load(p, clip=None, end=False):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    for a in list(bpy.data.actions): bpy.data.actions.remove(a)
    bpy.ops.import_object.ksp_mu(filepath=p); fr = 0
    for o in bpy.data.objects:
        ad = o.animation_data
        for t in list(ad.nla_tracks) if ad else []:
            act = t.strips[0].action; t.mute = True
            if clip and act.name.split('.')[0] == clip or clip and t.name.split('.')[0] == clip:
                ad.action = act; fr = max(fr, act.frame_range[1])
    sc.frame_set(int(fr) if end else 0); bpy.context.view_layer.update(); out = {}
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.data.polygons:
            out.setdefault(base(o), []).append(([o.matrix_world @ v.co for v in o.data.vertices], [list(p.vertices) for p in o.data.polygons]))
    return out
def tree(d, names=None, M=Matrix()):
    v, f = [], []
    for n, l in d.items():
        if names and n not in names: continue
        for a, b in l: k = len(v); v += [M @ p for p in a]; f += [[i + k for i in q] for q in b]
    return BVHTree.FromPolygons(v, f), v
mu = lambda n: os.path.join(MU, n + '.mu'); Tz = lambda z: Matrix.Translation((0, 0, z))
leg0, leg1 = load(mu('STMS_HLS_Leg'), 'legDeploy'), load(mu('STMS_HLS_Leg'), 'legDeploy', True)
W = Matrix.Translation((0, -HL.R, HL.HINGE[1])); mov = [n for n in leg0 if n != 'bracket']
t, v = tree(leg0, mov, W); ok(min(p.z for p in v) > .02, 'stowed leg lowest point %.3f above the skirt edge' % min(p.z for p in v))
gap = min(math.hypot(p.x, p.y) for p in v) - HL.R; print('      by piece', {n: round(min(math.hypot(p.x, p.y) for p in tree(leg0, (n,), W)[1]) - HL.R, 3) for n in mov}); ok(gap > -.03, 'stowed leg innermost %.3f m off the hull radius' % gap); print('      stowed leg reaches r %.2f' % max(math.hypot(p.x, p.y) for p in v))
half = max(abs(math.degrees(math.atan2(p.x, -p.y))) for p in v if p.y < 0); ok(half < 37.5, 'stowed leg half-width %.1f deg (track starts 37.5 away)' % half)
t, v = tree(leg1, None, W); ok(abs(min(p.z for p in v) - HL.SOLE) < .06, 'deployed sole at %.3f (want %.2f)' % (min(p.z for p in v), HL.SOLE))
core = load(mu('STMS_HLS_Core')); crew = load(mu('STMS_HLS_Crew')); tc, _ = tree(core); tw, _ = tree(crew, None, Tz(HL.Z_TOP)); td, _ = tree(crew, ('doorskin', 'doorframe', 'flag'), Tz(HL.Z_TOP)); tb, _ = tree(crew, ('hull', 'windows', 'details'), Tz(HL.Z_TOP))
th, _ = tree(crew, ['sol%dhatch%s' % (i, k) for i in (1, 2) for k in ('skin', 'in')]); sp = [n for n in crew if n.startswith('sol') and 'hatch' not in n]; ts, vs = tree(crew, sp)
ok(not ts.overlap(th), 'solar packages clear of their shut hatches (%d hits)' % len(ts.overlap(th))); thull, _ = tree(crew, ('hull',)); ok(not ts.overlap(thull), 'solar packages inside the hull (%d hits)' % len(ts.overlap(thull)))
L0 = Matrix.Translation((0, -HL.TRACK_R, HL.DOOR[0])); l0, l1 = load(mu('STMS_HLS_Lift'), 'deckFold'), load(mu('STMS_HLS_Lift'), 'deckFold', True)
t, v = tree(l0, ('carriage', 'deckmesh'), L0); ok(not t.overlap(td), 'folded elevator clear of the shut door (%d hits)' % len(t.overlap(td))); ok(not t.overlap(tb), 'folded elevator clear of the bay (%d hits)' % len(t.overlap(tb)))
hit = {}
for k in range(0, int(HL.LIFT_TRAVEL * 4) + 1):
    t, v = tree(l1, ('carriage', 'deckmesh'), L0 @ Tz(-k / 4))
    for nm, o in (('core', tc), ('crew', tb)):
        n = len(t.overlap(o))
        if n and len(hit.get(nm, [])) < 3: print('      ', nm, k / 4, [q for q in (core if nm == 'core' else crew) if t.overlap(tree(core if nm == 'core' else crew, (q,), Matrix() if nm == 'core' else Tz(HL.Z_TOP))[0])])
        if n: hit.setdefault(nm, []).append((k / 4, n))
ok(not hit, 'elevator clear along its travel ' + str({k: (len(x), x[:4]) for k, x in hit.items()}))
for i, az in enumerate(HL.LEG_AZ):
    t2, _ = tree(leg1, None, Matrix.Rotation(math.radians(az), 4, 'Z') @ W)
    for k in (HL.LIFT_TRAVEL, HL.LIFT_TRAVEL - 1, HL.LIFT_TRAVEL - 2, HL.LIFT_TRAVEL - 3): ok(not tree(l1, ('carriage', 'deckmesh'), L0 @ Tz(-k))[0].overlap(t2), f'elevator {HL.LIFT_TRAVEL - k:.0f} m up clear of leg {az}') if az in (45, 315) else None
v = tree(l1, ('carriage', 'deckmesh'), L0 @ Tz(-HL.LIFT_TRAVEL))[1]; lo = min(p.z for p in v); ok(.2 < lo - HL.SOLE < .6, 'lowered deck underside %.2f m above the soles' % (lo - HL.SOLE))
if SEP and os.path.exists(SEP):
    r = load(os.path.join(SEP, 'SEP_26_RAPTOR_3.mu')); R0 = 1.8125
    sl = [n for n in ('Powerhead', 'Nozzle_SL', 'Pipes_Common', 'Shield_BOX') if n in r]; vc = [n for n in ('Powerhead', 'Nozzle_VAC', 'Nozzle_VAC_Extension', 'Pipes_Common') if n in r]
    for a in (0, 120, 240):
        s, c = math.sin(math.radians(a)), math.cos(math.radians(a)); t, v = tree(r, sl, Matrix.Translation((HL.R_SL * s, -HL.R_SL * c, HL.Z_SL - R0)))
        q = [p for p in v if p.z < HL.Z_SL - .02]; ok(max(math.hypot(p.x, p.y) for p in q) < 2.3, 'SL Raptor %d inside the bay' % a)
    for a in (60, 180, 300):
        s, c = math.sin(math.radians(a)), math.cos(math.radians(a)); t, v = tree(r, vc, Matrix.Translation((HL.R_VAC * s, -HL.R_VAC * c, HL.Z_VAC - R0)))
        h = t.overlap(tc); lim = max(math.hypot(p.x, p.y) for p in v); ok(not h, 'vacuum Raptor %d: r max %.3f, exit z %.3f, %d hits' % (a, lim, min(p.z for p in v), len(h)))
load(mu('STMS_HLS_Core'))
tt = [o.matrix_world.copy() for o in bpy.data.objects if base(o) == 'landingThrust']
ok(len(tt) == 18 and len({tuple(round(x, 2) for x in m.translation) for m in tt}) == 18, '%d distinct landing thrust transforms' % len(tt))
f = [(m.translation, (m.to_3x3() @ V((0, 1, 0))).normalized()) for m in tt]
ok(all(HL.BAND[0] < p.z < HL.BAND[1] and d.z < -.7 and d.x * p.x + d.y * p.y > 0 for p, d in f), 'exhaust down and outward, z %.3f' % max(d.z for _, d in f)); s = sum((d for _, d in f), V()); ok(abs(s.x) + abs(s.y) < .01, 'sideways thrust cancels')
for pn, tn in (('STMS_HLS_Core', 'RCSthruster'), ('STMS_HLS_Crew', 'RCSthruster')):
    load(mu(pn)); q = [((o.matrix_world.to_3x3() @ V((0, 0, 1))).normalized(), o.matrix_world.translation.copy()) for o in bpy.data.objects if base(o) == tn]
    ok(len(q) == 16 and all(d.x * p.x + d.y * p.y > 0 for d, p in q), f'{pn}: {len(q)} RCS, all outward')
if SEP and os.path.exists(SEP):
    h = load(os.path.join(SEP, 'SEP_26_SHIP_DOCKING_HARDWARE.mu')); N0 = V((0, -2.875, -1.0276))
    M = Matrix.Translation((0, HL.R_DOCK, HL.Z_DOCK)) @ Matrix.Rotation(math.pi, 4, 'Z') @ Matrix.Translation(-N0)
    for n in h:
        t, v = tree(h, (n,), M); c = [k for k, o in (('core', tc), ('crew', tw)) if t.overlap(o)]
        print('      dock', n, 'z %.2f..%.2f' % (min(p.z for p in v), max(p.z for p in v)), 'r %.2f..%.2f' % (min(math.hypot(p.x, p.y) for p in v), max(math.hypot(p.x, p.y) for p in v)), 'touches', c)
        for az in HL.LEG_AZ: ok(not t.overlap(tree(leg0, None, Matrix.Rotation(math.radians(az), 4, 'Z') @ W)[0]), f'{n} clear of stowed leg {az}') if t.overlap(tree(leg0, None, Matrix.Rotation(math.radians(az), 4, 'Z') @ W)[0]) else None
print('check_hls:', bad, 'failures')

"""HLS clearances on the built models: legs stowed and out, the elevator folded behind the shut door and along its travel,
solar packages behind their hatches, the nose port clear of the rim. usage: blender -b -P check_hls.py -- build/mu [SEP assets]"""
import bpy, sys, os, math, addon_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
import hls_layout as HL
addon_utils.enable('io_object_mu', default_set=True)
CREW = os.environ.get('HLS_CREW', 'STMS_HLS_Crew'); MU = sys.argv[sys.argv.index('--') + 1]; SEP = (sys.argv[sys.argv.index('--') + 2:] + [''])[0]; sc = bpy.context.scene; bad = 0
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
core = load(mu('STMS_HLS_Core')); core_o = {k: v for k, v in core.items() if k not in ('hull', 'bells', 'ducts', 'legpods', 'legpods_in')}; ok(not any(tree(core_o, None)[0].overlap(tree(leg1, ('foot', 'strut2', 'strut3'), Matrix.Rotation(math.radians(a), 4, 'Z') @ W)[0]) for a in HL.LEG_AZ), 'original style: deployed legs clear of the hull'); crew = load(mu(CREW)); tc, _ = tree(core); tw, _ = tree(crew, None, Tz(HL.Z_TOP)); td, _ = tree(crew, ('doorskin', 'doorframe', 'flag'), Tz(HL.Z_TOP)); tb, _ = tree(crew, ('hull', 'windows', 'details'), Tz(HL.Z_TOP))
lf0 = load(mu('STMS_HLS_LegFaired'), 'legDeploy'); cv = load(mu('STMS_HLS_PodCover')); pods = {k: v for k, v in core.items() if k in ('legpods', 'legpods_in', 'hull')}
MP = lambda a, out=0: Matrix.Rotation(math.radians(a), 4, 'Z') @ W @ Matrix.Translation((0, -out, 0)); t = tree(cv, None, MP(45))[0]
ok(not t.overlap(tree(lf0, None, MP(45))[0]), 'pod cover clear of the stowed faired leg %d' % len(t.overlap(tree(lf0, None, MP(45))[0]))); ok(not t.overlap(tree(pods)[0]), 'pod cover clear of the pod %d' % len(t.overlap(tree(pods)[0])))
for o_ in (.1, .3, .6): ok(not tree(cv, None, MP(45, o_))[0].overlap(tree(pods)[0]) and not tree(cv, None, MP(45, o_))[0].overlap(tree(lf0, None, MP(45))[0]), f'pod cover clear {o_} m off')
so = load(mu('STMS_HLS_Solar'), 'solarDeploy'); so1 = load(mu('STMS_HLS_Solar'), 'solarDeploy', True); ZS = sum(HL.SOL_Z) / 2
for az in HL.SOL_AZ:
    MS = Matrix.Rotation(math.radians(az), 4, 'Z') @ Matrix.Translation((0, -HL.R, ZS)); hh = ('hatchskin', 'hatchin'); tp, _ = tree(so, [n for n in so if n not in hh + ('rails',)], MS); t2, _ = tree(so, hh, MS); t3, _ = tree(so1, [n for n in so1 if n not in ('rails',)], MS)
    pv = tree(so, None, MS)[1]; ok(not any(abs(q.x) < .93 and q.y < -1.2 and HL.DOOR[0] - .05 < q.z < HL.DOOR[1] + .05 for q in pv), f'solar {az}: nothing in the airlock bay'); ok(all(abs(math.degrees(math.atan2(q.x, -q.y)) - (az if az < 180 else az - 360)) < HL.SOL_HW + .4 for q in pv if math.hypot(q.x, q.y) < 2.7), f'solar {az}: inside its pocket')
    ok(not tp.overlap(t2), f'solar {az}: package clear of the shut hatch'); n = {k: len(tp.overlap(tree(crew, (k,), Tz(HL.Z_TOP))[0])) for k in crew}; print('      package touches', {k: c for k, c in n.items() if c}); n = {k: len(t3.overlap(tree(crew, (k,), Tz(HL.Z_TOP))[0])) for k in crew}; print('      deployed touches', {k: c for k, c in n.items() if c})
# arrays hanging down: the panels, hub and pivot turned about the tilt axis, every 15 degrees, against hull, hatches, each other, legs and pods
PN = [n for n in so1 if n.startswith('panel') or n == 'hub']; PIVR = HL.SOL_DP + .06 + .24 + HL.SOL_OUT; allcore, _ = tree(core); hangs = {}
for az in HL.SOL_AZ:
    MS = Matrix.Rotation(math.radians(az), 4, 'Z') @ Matrix.Translation((0, -HL.R, ZS)); ax = Matrix.Translation((0, HL.R - PIVR, 0))
    for deg in range(0, 91, 15):
        TM = MS @ ax @ Matrix.Rotation(math.radians(deg), 4, 'X') @ ax.inverted(); t, v = tree(so1, PN, TM); rest, _ = tree(so1, ('hatchskin', 'hatchin', 'rails', 'armmesh'), MS)
        h = [n for n, o in (('core', allcore), ('crew', tw), ('own hatch', rest)) if t.overlap(o)]; h += ['leg %d' % a for a in HL.LEG_AZ if t.overlap(tree(leg1, None, Matrix.Rotation(math.radians(a), 4, 'Z') @ W)[0])]
        if deg in (0, 90) or h: ok(not h, f'array {az} turned {deg} clear {h}; z {min(p.z for p in v):.2f}, innermost {min(math.hypot(p.x, p.y) for p in v) - HL.R:.3f} m off the hull')
    hangs[az] = t
    for q in range(0, 360, 15):
        TM = MS @ ax @ Matrix.Rotation(math.radians(q), 4, 'Y') @ ax.inverted(); t, _ = tree(so1, PN, TM); h = [n for n, o in (('core', allcore), ('crew', tw), ('own hatch', rest)) if t.overlap(o)]; ok(not h, f'array {az} tracking at {q} clear {h}') if h else None
for i, a in enumerate(HL.SOL_AZ):
    for b in HL.SOL_AZ[i + 1:]: ok(not hangs[a].overlap(hangs[b]), f'hanging arrays {a} and {b} apart') if hangs[a].overlap(hangs[b]) else None
L0 = Matrix.Translation((0, -HL.TRACK_R, HL.DOOR[0])); l0, l1 = load(mu('STMS_HLS_Lift'), 'deckFold'), load(mu('STMS_HLS_Lift'), 'deckFold', True)
t, v = tree(l0, ('carriage', 'deckmesh'), L0); ok(not t.overlap(td), 'folded elevator clear of the shut door (%d hits)' % len(t.overlap(td))); ok(not t.overlap(tb), 'folded elevator clear of the bay (%d hits)' % len(t.overlap(tb)))
crew1 = load(mu(CREW), 'doorOpen', True); DM = ('strutcyl', 'strutrod', 'doorhinge', 'doorlug', 'doorskin', 'doorframe'); to_ = tree(crew1, DM, Tz(HL.Z_TOP))[0]; tst = tree(crew, DM, Tz(HL.Z_TOP))[0]
ok(not tree(l0, None, L0)[0].overlap(tst), 'stowed elevator and guide clear of the shut door, its hinges and struts'); ok(not tree(l1, None, L0)[0].overlap(to_), 'extended elevator clear of the open door and struts')
gs, ge = tree(l0, ('guidemesh',), L0)[0], tree(l1, ('guidemesh',), L0)[0]; wheels = ('carriage', 'deckmesh')
ok(not gs.overlap(tb) and not ge.overlap(tb) and not ge.overlap(tc), 'guide clear of bay, sill and rails, in and out %d %d %d' % (len(gs.overlap(tb)), len(ge.overlap(tb)), len(ge.overlap(tc))))
for k in range(0, 25): h_ = ge.overlap(tree(l1, wheels, L0 @ Tz(-k / 10))[0]); ok(not h_, f'carriage {k / 10} m down clear of the guide ({len(h_)})') if h_ else None
ok(not gs.overlap(tree(l0, wheels, L0)[0]), 'carriage clear of the guide stowed')
hit = {}
for k in range(0, int(HL.LIFT_TRAVEL * 4) + 1):
    t, v = tree(l1, ('carriage', 'deckmesh'), L0 @ Tz(-k / 4))
    for nm, o in (('core', tc), ('crew', tb)):
        n = len(t.overlap(o))
        if n and len(hit.get(nm, [])) < 3: print('      ', nm, k / 4, [q for q in (core if nm == 'core' else crew) if t.overlap(tree(core if nm == 'core' else crew, (q,), Matrix() if nm == 'core' else Tz(HL.Z_TOP))[0])])
        if n: hit.setdefault(nm, []).append((k / 4, n))
for az in HL.SOL_AZ: n = [k / 2 for k in range(0, int(HL.LIFT_TRAVEL * 2)) if tree(l1, ('carriage', 'deckmesh'), L0 @ Tz(-k / 2))[0].overlap(hangs[az])]; ok(not n, f'elevator clear of hanging array {az} {n[:3]}')
c0, c1 = load(mu('STMS_HLS_LiftCable'), 'cageOut'), load(mu('STMS_HLS_LiftCable'), 'cageOut', True); CM = ('cagemesh', 'boommesh', 'midmesh'); bayT = tree({k: v for k, v in crew.items() if k in ('hull', 'details', 'windows')}, None, Tz(HL.Z_TOP))[0]
core_n = {k: v for k, v in core.items() if k != 'track'}; tcn = tree(core_n)[0]
for q_ in CM + ('channels',): h_ = {k: len(tree(crew, (k,), Tz(HL.Z_TOP))[0].overlap(tree(c0, (q_,), L0)[0])) for k in crew}; ok(q_ == 'channels' or not any(h_.values()), f'cable elevator stowed, {q_}: ' + str({k: c for k, c in h_.items() if c}))
for q_ in CM: h_ = {k: len(tree(crew1, (k,), Tz(HL.Z_TOP))[0].overlap(tree(c1, (q_,), L0)[0])) for k in crew1 if k != 'crewtrack'}; ok(not any(h_.values()), f'cable elevator out, {q_}: ' + str({k: c for k, c in h_.items() if c}))
ok(not tree(c0, ('cagemesh',))[0].overlap(tree(c0, ('boommesh', 'midmesh', 'channels'))[0]) and not tree(c1, ('cagemesh',))[0].overlap(tree(c1, ('boommesh',))[0]), 'cage clear of its beams'); ok(not tree(c0, ('boommesh',))[0].overlap(tree(c0, ('channels',))[0]), 'beam inside beam stowed %d' % len(tree(c0, ('boommesh',))[0].overlap(tree(c0, ('channels',))[0])))
for k in range(0, int(HL.LIFT_TRAVEL * 2) + 1): t_ = tree(c1, ('cagemesh',), L0 @ Tz(-k / 2))[0]; ok(not t_.overlap(tcn) and not any(t_.overlap(hangs[a_]) for a_ in HL.SOL_AZ), f'cage {k / 2} m down') if t_.overlap(tcn) or any(t_.overlap(hangs[a_]) for a_ in HL.SOL_AZ) else None
for i, az in enumerate(HL.LEG_AZ):
    for nm_, l_ in (('', leg1), ('faired ', load(mu('STMS_HLS_LegFaired'), 'legDeploy', True))):
        for k in range(0, 5): t_ = tree(c1, ('cagemesh',), L0 @ Tz(-HL.LIFT_TRAVEL + k))[0]; ok(not t_.overlap(tree(l_, None, Matrix.Rotation(math.radians(az), 4, 'Z') @ W)[0]), f'cage clear of {nm_}leg {az}') if t_.overlap(tree(l_, None, Matrix.Rotation(math.radians(az), 4, 'Z') @ W)[0]) else None
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
for pn, tn in (('STMS_HLS_Core', 'RCSthruster'), (CREW, 'RCSthruster')):
    load(mu(pn)); q = [((o.matrix_world.to_3x3() @ V((0, 0, 1))).normalized(), o.matrix_world.translation.copy()) for o in bpy.data.objects if base(o) == tn]
    ok(len(q) == 16 and all(d.x * p.x + d.y * p.y > 0 for d, p in q), f'{pn}: {len(q)} RCS, all outward')
if SEP and os.path.exists(SEP):
    h = load(os.path.join(SEP, 'SEP_26_SHIP_DOCKING_HARDWARE.mu')); N0 = V((0, -2.875, -1.0276))
    M = Matrix.Translation((0, HL.R_DOCK, HL.Z_DOCK)) @ Matrix.Rotation(math.pi, 4, 'Z') @ Matrix.Translation(-N0)
    for n in h:
        t, v = tree(h, (n,), M); c = [k for k, o in (('core', tc), ('crew', tw)) if t.overlap(o)]
        print('      dock', n, 'z %.2f..%.2f' % (min(p.z for p in v), max(p.z for p in v)), 'r %.2f..%.2f' % (min(math.hypot(p.x, p.y) for p in v), max(math.hypot(p.x, p.y) for p in v)), 'touches', c)
        for az in HL.LEG_AZ: ok(not t.overlap(tree(leg0, None, Matrix.Rotation(math.radians(az), 4, 'Z') @ W)[0]), f'{n} clear of stowed leg {az}') if t.overlap(tree(leg0, None, Matrix.Rotation(math.radians(az), 4, 'Z') @ W)[0]) else None
sh, _ = tree(load(mu('STMS_HLS_LegShroud')), ('shroud_black', 'inside'), W)
for n in leg0: ok(not sh.overlap(tree(leg0, (n,), W)[0]) or n == 'bracket', 'shroud over stowed leg: ' + n) if sh.overlap(tree(leg0, (n,), W)[0]) else None
q0, q1 = load(mu('STMS_Ship_Leg'), 'legDeploy'), load(mu('STMS_Ship_Leg'), 'legDeploy', True)
if SEP and os.path.exists(SEP):
    co = load(os.path.join(SEP, 'SEP_26_SHIP_CORE.mu')); M0 = Tz(12.5993)
    dh = load(os.path.join(SEP, 'SEP_26_SHIP_DOCKING_HARDWARE.mu'))
    for az in HL.SHIP_LEG_AZ:
        for tag, q in (('stowed', q0), ('deployed', q1)):
            tt_, _ = tree(q, [n for n in q if n not in ('bracket', 'nose_steel', 'nose_tile')], Matrix.Rotation(math.radians(az), 4, 'Z') @ W); h = {n: len(tt_.overlap(tree(co, (n,), M0)[0])) for n in co if n != 'atmofx_envelope'}; h = {n: c for n, c in h.items() if c}; bad_ = [n for n in h if n in ('Hatch', 'Cam_EXT', 'Vent', 'Flap Pipes', 'Cube', 'raceways', 'QD ')]; ok(not bad_ and not any(tt_.overlap(tree(dh, (n,), M0)[0]) for n in dh), f'ship leg {az} {tag} clear of vents, camera, flap fairing and docking hardware {bad_}'); print('      ship leg', az, tag, 'on SEP core touches', h)
print('check_hls:', bad, 'failures')

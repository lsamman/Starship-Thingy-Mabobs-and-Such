"""HLS cargo section on the built models: door shut and along its swing, crane frame, the winch stowed and along its travel, the solar kit.
usage: blender -b -P check_cargo.py -- build/mu ../v3/build/mu"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
A = sys.argv[sys.argv.index('--') + 1:]; V3 = A[1]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'check_hls.py')).read().split("leg0, leg1 =")[0]; exec(compile(src, 'check_hls', 'exec'))
SEP = ''
def posed(clips):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    bpy.ops.import_object.ksp_mu(filepath=mu('STMS_HLS_CargoAwning')); acts = {}
    for o in bpy.data.objects:
        ad = o.animation_data
        for t in list(ad.nla_tracks) if ad else []:
            t.mute = True; n = t.name.split('.')[0]; n = n if n in clips else t.strips[0].action.name.split('.')[0]
            if n in clips: acts.setdefault(o, []).append((t.strips[0].action, clips[n]))
    for o, l in acts.items():
        for act, k in l:
            o.animation_data.action = act; sc.frame_set(int(round(act.frame_range[1] * k))); m = o.matrix_basis.copy(); o.animation_data.action = None; o.animation_data_clear(); o.matrix_basis = m
    bpy.context.view_layer.update(); out = {}
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.data.polygons: out.setdefault(base(o), []).append(([o.matrix_world @ v.co for v in o.data.vertices], [list(p.vertices) for p in o.data.polygons]))
    return out
rad_ = lambda z: float(__import__('numpy').interp(z, *zip(*HL.OGIVE)))
DOOR = ('doorskin', 'doorframe', 'doorbay'); FR = ('crane',)
CR = load(mu('STMS_HLS_Crane')); YB = HL.CR_IN - HL.CR_Y; CO = V((0, HL.CR_Y, HL.CG_FLOOR))
def crane(b):
    out = []; tip = V((0, YB - b, HL.CR_BAR)); foot = V((0, 0, HL.CR_FOOT)); t0 = V((0, YB, HL.CR_BAR))
    a0, a1 = [math.atan2(q.z, q.y) for q in (t0 - foot, tip - foot)]; R_ = Matrix.Rotation(a1 - a0, 4, 'X')
    for n, l in CR.items():
        for vs, fs in l:
            if n.startswith('craneLowMesh'): w = [foot + R_ @ (q - foot) for q in vs]
            elif n.startswith('craneTopMesh'): w = [tip + R_ @ (q - t0) for q in vs]
            elif n == 'cranebar': w = [q + V((0, -b, 0)) for q in vs]
            else: w = vs
            out.append(([q + CO for q in w], fs))
    return out
_posed = posed
def posed(c):
    d_ = _posed({'CargoDoor': c['CargoDoor']}); d_['crane'] = crane(4.4 * c['craneFrameOut']); return d_
p = posed({'CargoDoor': 0, 'craneFrameOut': 0}); st = [n for n in p if n not in DOOR + FR + ('winchmount',)]; print('      meshes', list(p))
body = tree(p, st)[0]; print('      shut door touches', [n for n in st if tree(p, DOOR)[0].overlap(tree(p, (n,))[0])])
ok(not tree(p, FR)[0].overlap(tree(p, DOOR)[0]), 'stowed frame clear of the shut door'); ok(not tree(p, FR)[0].overlap(tree(p, ('hull',))[0]), 'stowed frame clear of the hull')
dv = tree(p, DOOR)[1]; print('      door reaches r %.3f' % max(math.hypot(q.x, q.y) for q in dv))
for k in (.02, .05, .1, .2, .35, .5, .65, .8, .9, 1):
    q = posed({'CargoDoor': k, 'craneFrameOut': 0}); n = {}
    for dm in DOOR:
        t, v = tree(q, (dm,)); vp, fp = [], []
        for a, b in q[dm]: o_ = len(vp); vp += a; fp += [[i + o_ for i in f] for f in b]
        for m in st:
            for x, y in t.overlap(tree(q, (m,))[0]):
                c = sum((vp[i] for i in fp[x]), V()) / len(fp[x]); dist = min(math.hypot(vp[i].y + rad_(HL.CG_HEAD) - .02, vp[i].z - HL.CG_HEAD + .03) if abs(vp[i].x) < .75 else 9 for i in fp[x]); dist = min(dist, math.hypot(c.y + rad_(HL.CG_HEAD), c.z - HL.CG_HEAD))
                if dist > .24: n.setdefault((dm, m), []).append(tuple(round(e, 2) for e in c))          # the hinge itself may touch its frame
    ok(not n, 'door at %.2f clear of the section away from its hinge %s' % (k, {a: (len(b), b[:3]) for a, b in n.items()})); t = tree(q, DOOR)[0]; ok(not t.overlap(tree(q, FR)[0]), 'door at %.2f clear of the stowed frame' % k) if t.overlap(tree(q, FR)[0]) else None
W = {}
for nm, off in (('Boom', (0, 0, HL.CG_CEIL)), ('Hoist', (0, -.5, 3.38 + HL.WINCH_DZ)), ('Platform', (0, -.5, .87 + HL.WINCH_DZ))):
    g = load(os.path.join(V3, 'SEP_CW_%s.mu' % nm))
    ar = lambda a, f: (a[f[1]] - a[f[0]]).cross(a[f[2]] - a[f[0]]).length          # without the zero-area triangles that hold the bounds open
    W[nm] = ({k: [(a, [f for f in b if ar(a, f) > 1e-7]) for a, b in l] for k, l in g.items()}, Matrix.Translation(off))
def winch(b, h):
    # the moving stages of boom and hoist are skinned, so here: boom rails as a swept copy, platform moved as a whole
    r = {'Platform': tree(W['Platform'][0], None, Matrix.Translation((0, -b, -h)) @ W['Platform'][1]), 'Hoist': tree(W['Hoist'][0], None, Matrix.Translation((0, -b, 0)) @ W['Hoist'][1])}
    for t in (0, .5, 1): r['Boom%g' % t] = tree(W['Boom'][0], None, Matrix.Translation((0, -b * t, 0)) @ W['Boom'][1])
    return r
shut = posed({'CargoDoor': 0, 'craneFrameOut': 0}); ts = tree(shut)[0]
for n, (t, v) in winch(0, 0).items():
    h = [m for m in shut if t.overlap(tree(shut, (m,))[0])]; print('      stowed', n, 'z %.2f..%.2f y %.2f..%.2f x %.2f' % (min(q.z for q in v), max(q.z for q in v), min(q.y for q in v), max(q.y for q in v), max(abs(q.x) for q in v)), h); ok(not set(h) & set(DOOR + ('hull',)), 'winch stowed, door shut: ' + n)
HD = HL.CG_FLOOR + HL.CR_BAR - .125 - 3.38
for e in range(0, 45, 4):                                 # the winch on the crane's crossbar: in behind the shut door, then out with it
    q = posed({'CargoDoor': 0 if e == 0 else 1, 'craneFrameOut': e / 44}); b = e / 10
    for n, o_ in (('Hoist', 0), ('Platform', 0)):
        t, v = tree(W[n][0], None, Matrix.Translation((0, -.5 - b, (3.38 if n == 'Hoist' else .87) + HD))); h = [m for m in q if t.overlap(tree(q, (m,))[0]) and not (n == 'Hoist' and m == 'crane')]; ok(not h, 'crane %.1f: %s %s z %.2f..%.2f' % (b, n, h, min(x.z for x in v), max(x.z for x in v)))
    w_ = [m for m in DOOR + ('hull',) if tree(q, FR)[0].overlap(tree(q, (m,))[0])]; ok(not w_, 'crane out %.1f clear of door and hull %s' % (b, w_))
CT = posed({'CargoDoor': 1, 'craneFrameOut': 1})
out = _posed({'CargoDoor': 1})
for b in (0, 1, 2, 3, 4, 4.4):
    for n, (t, v) in winch(b, 0).items():
        if n in ('Boom0.5', 'Boom0') and b: continue
        h = [m for m in out if t.overlap(tree(out, (m,))[0])]; h = [m for m in h if not (n.startswith('Boom') and m == 'details' and b < 5)]
        ok(not h, 'boom %.1f: %s %s' % (b, n, h))
core = load(mu('STMS_HLS_Core')); tc = tree(core, [n for n in core if n != 'track'], Matrix.Translation((0, 0, -HL.Z_OGIVE)))[0]; leg = load(mu('STMS_HLS_LegFaired'), 'legDeploy', True); LW = Matrix.Translation((0, 0, -HL.Z_OGIVE))
tl = [tree(leg, None, LW @ Matrix.Rotation(math.radians(a), 4, 'Z') @ Matrix.Translation((0, -HL.R, HL.HINGE[1])))[0] for a in HL.LEG_AZ]
for h in (.5, 1, 2, 4, 8, 12, 16, 20, 22, 23, 24):
    t, v = winch(4.4, h)['Platform']; ok(not (t.overlap(tree(out)[0]) or t.overlap(tc) or any(t.overlap(x) for x in tl)), 'platform %.1f down, underside %.2f above the soles' % (h, min(q.z for q in v) + HL.Z_OGIVE - HL.SOLE))
t, v = tree(p, st); tk = load(mu('STMS_HLS_CargoKit')); k = tree(tk)[0]; print('      kit touches', [m for m in p if k.overlap(tree(p, (m,))[0])]); ok(not k.overlap(tree(out, DOOR)[0]), 'solar kit clear of door')
leg0 = load(mu('STMS_HLS_LegFaired'), 'legDeploy'); pods = ('legpods', 'legpods_in')
for i in range(0, 121, 8):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    bpy.ops.import_object.ksp_mu(filepath=mu('STMS_HLS_LegFaired'))
    for o in bpy.data.objects:
        ad = o.animation_data
        for t_ in list(ad.nla_tracks) if ad else []: t_.mute = True; ad.action = t_.strips[0].action
    sc.frame_set(i); bpy.context.view_layer.update(); l = {}
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.data.polygons: l.setdefault(base(o), []).append(([o.matrix_world @ v.co for v in o.data.vertices], [list(f.vertices) for f in o.data.polygons]))
    M = Matrix.Rotation(math.radians(45), 4, 'Z') @ Matrix.Translation((0, -HL.R, HL.HINGE[1])); hits = {n: [m for m in pods if tree(l, (n,), M)[0].overlap(tree(core, (m,))[0])] for n in l}; hits = {a: b for a, b in hits.items() if b}
    if hits or i in (0, 120): ok(not hits, 'leg frame %d clear of its pod %s' % (i, hits))
print('check_cargo:', bad, 'failures')

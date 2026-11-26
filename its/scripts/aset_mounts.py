"""Builds its/data/aset_mounts.json for avionics.py from an install with ALCOR and ASET Props/Avionics: for each prop the panels use,
how ALCOR mounts it on a panel (rotation in the board frame, snapped to whole quarter turns; height of its origin over the panel;
scale) and its footprint on the board from its model. Mounts derive from ALCOR's cockpit (alexustas, JonnyOThan; CC BY-NC-SA 3.0).
usage: blender -b -P aset_mounts.py -- <GameData> <out.json>"""
import bpy, sys, os, re, glob, json, math, collections, addon_utils
import numpy as np
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
addon_utils.enable('io_object_mu', default_set=True)
GD, out = sys.argv[sys.argv.index('--') + 1:][:2]
import importlib.util
sp = importlib.util.spec_from_file_location('av', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'avionics.py'))
src = open(sp.origin).read().replace("MOUNTS = json.load", "MOUNTS = {} and json.load"); av = type(sys)('av'); exec(src, av.__dict__)
RIVA = np.array([[-1, 0, 0], [0, 0, -1], [0, -1, 0]], float)


def qm(x, y, z, w):
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


# ---- ALCOR's props in its part frame (as ivalib's: internal Unity = -(part Blender)); prop columns: x, -up, out
t = open(os.path.join(GD, 'ASET/ALCOR/Spaces/ALCORInternals3/ALCORInternals3.cfg'), errors='replace').read()
items = []
for m in re.finditer(r'^\s*PROP\s*\{\s*name\s*=\s*(\S+)\s*position\s*=\s*([^\n]+)\s*rotation\s*=\s*([^\n]+)\s*scale\s*=\s*([^\n]+)', t, re.M):
    X, Y, Z, W = [float(v) for v in m.group(3).split(',')]
    items.append(dict(name=m.group(1), p=-np.array([float(v) for v in m.group(2).split(',')]), M=RIVA.T @ qm(-X, -Z, -Y, W), s=[float(v) for v in m.group(4).split(',')]))
# ---- panels: props with the same facing, on one plane, touching
N = len(items); par = list(range(N))
def root(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
for i in range(N):
    for j in range(i + 1, N):
        a, b = items[i], items[j]; na, nb = a['M'][:, 2], b['M'][:, 2]
        if na @ nb > math.cos(math.radians(6)) and abs(na @ (b['p'] - a['p'])) < .025 and np.linalg.norm(b['p'] - a['p']) < .09: par[root(i)] = root(j)
groups = collections.defaultdict(list)
for i in range(N): groups[root(i)].append(i)
panels = []
for ids in groups.values():
    if len(ids) < 10: continue
    X = np.array([items[i]['p'] for i in ids]); n = np.mean([items[i]['M'][:, 2] for i in ids], 0); n /= np.linalg.norm(n)
    up = np.mean([-items[i]['M'][:, 1] for i in ids], 0); up -= n * (up @ n); up /= np.linalg.norm(up)
    B = np.array([np.cross(up, n), up, n]).T; L = (X - X.mean(0)) @ B
    panels.append(dict(B=B, d=np.median(X @ n), c=X.mean(0), lo=L.min(0) - .12, hi=L.max(0) + .12))
def snap(R):                                            # nearest signed permutation: whole quarter turns
    S = np.zeros((3, 3))
    for c in range(3): r = int(np.argmax(abs(R[:, c]))); S[r, c] = np.sign(R[r, c])
    return S if abs(np.linalg.det(S) - 1) < 1e-6 else None
mounts = collections.defaultdict(collections.Counter)
for it in items:
    best = None
    for k, pn in enumerate(panels):
        n = pn['B'][:, 2]
        if max(abs(it['M'][:, j] @ n) for j in range(3)) < .97: continue
        h = it['p'] @ n - pn['d']; l = (it['p'] - pn['c']) @ pn['B']
        if abs(h) > .09 or (l[:2] < pn['lo'][:2]).any() or (l[:2] > pn['hi'][:2]).any(): continue
        if best is None or abs(h) < best[0]: best = (abs(h), k, h)
    if best is None: continue
    S = snap(panels[best[1]]['B'].T @ it['M'])
    if S is not None: mounts[it['name']][(tuple(S.ravel()), round(best[2], 3), round(it['s'][0], 4))] += 1
# ---- models: KSP's rule, the PROP's MODEL or else the .mu beside its cfg
models = {}
for f in glob.glob(os.path.join(GD, 'ASET', '**', '*.cfg'), recursive=True):
    tt = open(f, errors='replace').read()
    for b in re.split(r'^\s*PROP\s*$', tt, flags=re.M)[1:]:
        n = re.search(r'^\s*name\s*=\s*(\S+)', b, re.M)
        if not n: continue
        ms = re.findall(r'^\s*model\s*=\s*(\S+)', b, re.M)
        models.setdefault(n.group(1), [os.path.join(GD, x + '.mu') for x in ms] if ms else sorted(glob.glob(os.path.join(os.path.dirname(f), '*.mu')))[:1])
res, miss = {}, []
DEFAULT = (-1, 0, 0, 0, -1, 0, 0, 0, 1)              # the usual ASET panel prop: x across (mirrored), -up, out
for name in av.used():
    if name not in models: miss.append(name); continue
    if mounts[name]: (R, h, s), _ = mounts[name].most_common(1)[0]; src_ = 'alcor'
    else: R, h, s, src_ = DEFAULT, 0.0, .45, 'default'
    lo, hi = Vector((9, 9, 9)), Vector((-9, -9, -9))
    for p in models[name]:
        if not os.path.exists(p): continue
        for o in list(bpy.data.objects): bpy.data.objects.remove(o)
        bpy.ops.import_object.ksp_mu(filepath=p); bpy.context.view_layer.update()
        for o in bpy.data.objects:
            if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE':
                for c in o.bound_box: w = o.matrix_world @ Vector(c); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    if lo.x > hi.x: miss.append(name); continue
    Rm = np.array(R).reshape(3, 3); C = np.array([[x, y, z] for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]) * s @ Rm.T + [0, 0, h]
    res[name] = dict(R=list(R), h=h, s=s, lo=C.min(0).round(4).tolist(), hi=C.max(0).round(4).tolist(), src=src_)
json.dump(dict(note='Derived from ALCOR (alexustas, JonnyOThan; CC BY-NC-SA 3.0) and ASET Props/Avionics models: mounts and footprints only.', props=res), open(out, 'w'), indent=0)
print('MOUNTS', len(res), 'props;', sum(v['src'] == 'default' for v in res.values()), 'by default; missing', miss)

"""Finds pieces that touch nothing: every mesh island must overlap (or lie within 6 mm of) another, back to the part's biggest one.
Moving parts are judged in the stowed pose. usage: blender -b -P check_float.py -- part.mu ..."""
import bpy, sys, os, addon_utils
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
addon_utils.enable('io_object_mu', default_set=True)
EPS = .006
for path in sys.argv[sys.argv.index('--') + 1:]:
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    bpy.ops.import_object.ksp_mu(filepath=path); bpy.context.scene.frame_set(0); bpy.context.view_layer.update()
    isl = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.muproperties.collider != 'MU_COL_NONE' or not o.data.polygons: continue
        v = np.array([o.matrix_world @ x.co for x in o.data.vertices])
        key = {}; par = list(range(len(v)))                       # weld split normals by position
        rep = [key.setdefault(tuple(np.round(p, 4)), i) for i, p in enumerate(v)]
        def find(a):
            while par[a] != a: par[a] = par[par[a]]; a = par[a]
            return a
        polys = [[rep[i] for i in p.vertices] for p in o.data.polygons]
        for p in polys:
            for b in p[1:]: par[find(b)] = find(p[0])
        groups = {}
        for p in polys: groups.setdefault(find(p[0]), []).append(p)
        for g in groups.values():
            ids = sorted({i for p in g for i in p}); m = {i: k for k, i in enumerate(ids)}
            isl.append((o.name, v[ids], [[m[i] for i in p] for p in g if len(set(p)) > 2]))
    isl = [i for i in isl if i[2]]
    n = len(isl); lo = np.array([i[1].min(0) for i in isl]) - EPS; hi = np.array([i[1].max(0) for i in isl]) + EPS
    T = [BVHTree.FromPolygons([tuple(p) for p in i[1]], i[2], epsilon=EPS) for i in isl]
    par = list(range(n))
    def find(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for a in range(n):
        near = np.nonzero(((lo[a] <= hi[a + 1:]) & (hi[a] >= lo[a + 1:])).all(1))[0] + a + 1 if a + 1 < n else []
        for b in near:
            if find(a) == find(b): continue
            hit = bool(T[a].overlap(T[b]))
            if not hit:
                s, t = (a, b) if len(isl[a][1]) < len(isl[b][1]) else (b, a)
                st = max(1, len(isl[s][1]) // 60)
                hit = any((T[t].find_nearest(V(p), EPS)[3] is not None) for p in isl[s][1][::st])
            if hit: par[find(a)] = find(b)
    size = {}
    for k in range(n): size.setdefault(find(k), []).append(k)
    main = max(size.values(), key=lambda ks: sum(len(isl[k][2]) for k in ks))
    bad = [ks for ks in size.values() if ks is not main]
    print(f'FLOAT {os.path.basename(path)}: {n} islands, {len(bad)} floating groups')
    for ks in sorted(bad, key=lambda ks: -sum(len(isl[k][2]) for k in ks))[:14]:
        c = np.concatenate([isl[k][1] for k in ks]); print('   ', isl[ks[0]][0].split('∧')[0], 'at', c.mean(0).round(2).tolist(), 'size', (c.max(0) - c.min(0)).round(2).tolist(), len(ks), 'islands')

"""Tests the Block 3 nose window kits against SEP's real nosecone. Exits 1 on any failure.
  * the measured rings in layout.py still match SEP_26_SHIP_NOSECONE.mu, and so does the faceted surface built on them
  * every kit vertex (and the frames with a 4 cm margin) lies over bare steel, with either ablative subtype shown
  * frames: no more than a few cm proud and every frame's foot under the skin (no floating, no gaps);
    glass above the skin and below the frame's top; nothing facing into the hull
  * every piece touches the hull (check_float.py's test against the combined nose and kit)
usage: blender -b -P check_nose.py -- <SEP dir> <build/mu>"""
import bpy, sys, os, math, addon_utils
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
import layout as L, nose as N
addon_utils.enable('io_object_mu', default_set=True)
sep, mu = sys.argv[sys.argv.index('--') + 1:][:2]
STEEL = ('Nose_7_EXT', 'Cylinder')
fails = []


def check(ok, msg):
    print(('ok    ' if ok else 'FAIL  ') + msg)
    if not ok:
        fails.append(msg)


def base(o): return o.name.split('∧')[0]


def imp(path):
    before = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=path); bpy.context.view_layer.update()
    return [o for o in bpy.data.objects if o not in before]


def vis(objs):
    return [o for o in objs if o.type == 'MESH' and o.muproperties.collider == 'MU_COL_NONE' and o.data.polygons and not base(o).startswith('atmofx')]


def tree(objs):
    vs, fs, own = [], [], []
    for o in objs:
        n = len(vs); m = o.matrix_world
        vs += [tuple(m @ v.co) for v in o.data.vertices]
        for p in o.data.polygons:
            fs.append(tuple(n + i for i in p.vertices)); own.append(base(o))
    return BVHTree.FromPolygons(vs, fs, all_triangles=False), own


def radial(t, az, z):
    a = math.radians(az); d = V((math.sin(a), -math.cos(a), 0))
    h = t.ray_cast(V((0, 0, z)) + d * 6, -d, 7)
    return h


sepo = vis(imp(f'{sep}/Assets/BL3/SEP_26_SHIP_NOSECONE.mu'))
shell, _ = tree([o for o in sepo if base(o) in STEEL])
states = {s: tree([o for o in sepo if base(o) != f'Ablative {k}']) for s, k in (('39', 43), ('43', 39))}

# 1. the stored rings and the surface built on them
err = []
for z, r in L.NOSE_RINGS:
    h = radial(shell, 0.0, z + (.002 if z < 0 else -.002))
    err.append(abs((6 - h[3]) - N.ring_r(z + (.002 if z < 0 else -.002))) if h[0] else 1)
check(max(err) < .002, f'rings match the mesh at their vertices: worst {max(err) * 1000:.1f} mm')
err = []
for z in np.arange(-2.6, 5.7, .05):
    if any(abs(z - w) < .03 for w in L.NOSE_WELDS):
        continue
    for az in np.arange(-75, 75.1, 1.25):
        h = radial(shell, az, z)
        if h[0]:
            err.append(abs((6 - h[3]) - N.point(az, z).xy.length))
check(max(err) < .002, f'faceted surface from the rings matches the shell: worst {max(err) * 1000:.1f} mm over {len(err)} rays')

for name in ('STMS_B3_WindowsCrew', 'STMS_B3_WindowsCrewCargo'):
    path = os.path.join(mu, name + '.mu')
    if not os.path.exists(path):
        check(False, f'{name}.mu not built'); continue
    kit = vis(imp(path))
    print(name)
    for o in kit:
        if 'cams' in base(o):                            # hull camera housings: on bare steel, and nothing more asked of them
            v = np.array([o.matrix_world @ x.co for x in o.data.vertices]); az = np.degrees(np.arctan2(v[:, 0], -v[:, 1]))
            hits = {s: {own[radial(t_, a_, z_)[2]] for a_, z_ in zip(az[::7], v[::7, 2]) if radial(t_, a_, z_)[2] is not None} - set(STEEL) for s, (t_, own) in states.items()}
            check(not any(hits.values()), f'  cameras: over bare steel in both ablative subtypes' + ('' if not any(hits.values()) else f' (hits {hits})')); continue
        kind = 'glass' if 'glass' in base(o) else 'frames'
        m = o.matrix_world; v = np.array([m @ x.co for x in o.data.vertices])
        az = np.degrees(np.arctan2(v[:, 0], -v[:, 1])); z = v[:, 2]; rho = np.hypot(v[:, 0], v[:, 1])
        # 2. bare steel under every vertex, in both ablative subtypes; frames also 4 cm around
        bad = {}
        for s, (t, own) in states.items():
            for i in range(len(v)):
                probes = [(az[i], z[i])] if kind == 'glass' else [(az[i] + da, z[i] + dz) for da, dz in ((0, 0), (1.0, 0), (-1.0, 0), (0, .04), (0, -.04))]
                for a_, z_ in probes:
                    h = radial(t, a_, z_)
                    if not h[0] or own[h[2]] not in STEEL:
                        bad.setdefault(s, set()).add(own[h[2]] if h[0] else 'nothing')
        check(not bad, f'  {kind}: over bare steel in both ablative subtypes' + (f' (hits {bad})' if bad else ''))
        # 3. height off the skin, along the facet normal
        off = np.empty(len(v))
        for i in range(len(v)):
            h = radial(shell, az[i], z[i]); off[i] = ((rho[i] - (6 - h[3])) / math.sqrt(1 + N.slope(z[i]) ** 2)) if h[0] else 9
        if kind == 'frames':
            frame_top = off.max()
            check(off.max() < .03, f'  frames: at most {off.max() * 100:.1f} cm proud (limit 3)')
        # islands: weld by position, join through faces
        key = {}; rep = [key.setdefault(tuple(np.round(p, 4)), i) for i, p in enumerate(v)]; par = list(range(len(v)))
        def find(a):
            while par[a] != a: par[a] = par[par[a]]; a = par[a]
            return a
        for p in o.data.polygons:
            for b in p.vertices[1:]: par[find(rep[b])] = find(rep[p.vertices[0]])
        isl = {}
        for i in range(len(v)): isl.setdefault(find(rep[i]), []).append(i)
        lo = np.array([off[k].min() for k in isl.values()]); hi = np.array([off[k].max() for k in isl.values()])
        if kind == 'frames':
            check((lo < -.002).all(), f'  frames: all {len(isl)} feet under the skin (highest foot {lo.max() * 1000:.1f} mm)')
            # 4. float: every frame overlaps the hull
            ft, _ = tree([o]); touch = len({i for i, _ in ft.overlap(shell)})
            check(touch > 0, f'  frames: overlap the hull ({touch} faces cross it)')
        else:
            check(lo.min() > 0 and hi.max() < frame_top, f'  glass: {lo.min() * 1000:.1f} to {hi.max() * 1000:.1f} mm above the skin, under the frame top {frame_top * 1000:.0f} mm')
            check((lo < .006).all(), f'  glass: all {len(isl)} panes within 6 mm of the hull')
        # 5. faces that would be culled from outside
        inward = 0
        for p in o.data.polygons:
            c = m @ p.center; n = (m.to_3x3() @ p.normal).normalized()
            if n.dot(N.normal(math.degrees(math.atan2(c.x, -c.y)), c.z)) < -.5:
                inward += 1
        check(inward == 0, f'  {kind}: {inward} faces turned into the hull')
    # clearances worth knowing in game
    fin = [o for o in bpy.data.objects if base(o).startswith('node_fin')][:2]
    fr = [o for o in kit if 'frames' in base(o)][0]; v = np.array([fr.matrix_world @ x.co for x in fr.data.vertices])
    print(f'  nearest frame to a flap hinge node: {min(np.linalg.norm(v - np.array(f.matrix_world.translation), axis=1).min() for f in fin):.2f} m;'
          f' widest window edge at az {np.degrees(np.abs(np.arctan2(v[:, 0], -v[:, 1]))).max():.1f} deg (flap hinges at {L.NOSE_FLAP_AZ:.0f})')
    for o in kit:
        bpy.data.objects.remove(o)
print(f'check_nose: {len(fails)} failures')
sys.exit(1 if fails else 0)

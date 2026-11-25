"""Reads the exported skins back: bones unrotated, weights as authored, every vertex at its modelled place at rest,
rest bounds that reach the far end of travel, and piston bones at local zero under a parent at the part's origin."""
import sys, bpy, addon_utils
addon_utils.enable('io_object_mu')
from io_object_mu.mu import Mu
from mathutils import Quaternion, Vector, Matrix
from collections import Counter
SW = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
for p in sys.argv[sys.argv.index('--') + 1:]:
    m = Mu(); m.read(p); found = {}; smr = []
    def walk(o, M):
        t = o.transform
        W = M @ Matrix.Translation(t.localPosition) @ Quaternion(t.localRotation).to_matrix().to_4x4()
        found[t.name] = (W, t.localRotation)
        if t.name.endswith('Servo'):
            assert Vector(t.localPosition).length < 1e-5, f'{t.name} must sit at local zero, has {t.localPosition}'
            off = M.translation; assert off.length < 1e-4, f'{t.name}: its parent must sit at the part origin (KSP drops the offset in flight), has {tuple(off)}'
        if getattr(o, 'skinned_mesh_renderer', None):
            smr.append((o, W))
        for c in o.children:
            walk(c, W)
    walk(m.obj, Matrix())
    print('MU', p.split('/')[-1], {k: ([round(x, 3) for x in v[0].translation], [round(x, 3) for x in v[1]]) for k, v in found.items() if k.endswith(('Servo', 'Anchor'))})
    for o, W in smr:
        s = o.skinned_mesh_renderer; me = s.mesh; err = 0; shares = Counter()
        for v, bw in zip(me.verts, me.boneWeights):
            q = Vector((0, 0, 0)); tot = 0
            for i, w in zip(bw.indices, bw.weights):
                if w <= 0:
                    continue
                bp = me.bindPoses[i]; B = Matrix([bp[0:4], bp[4:8], bp[8:12], bp[12:16]]) if len(bp) == 16 else Matrix(bp)
                q += (found[s.bones[i]][0] @ SW @ B @ SW @ Vector(v)) * w; tot += w
                if s.bones[i].endswith('Servo'):
                    shares[round(w, 2)] += 1
            err = max(err, (q / tot - W @ Vector(v)).length)
        print('MU  skin', o.transform.name, 'verts', len(me.verts), 'piston shares', dict(shares), 'rest error %.5f' % err, 'bounds', [round(x, 2) for x in s.center], [round(x, 2) for x in s.size])

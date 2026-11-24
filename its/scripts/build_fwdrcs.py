"""Forward-firing RCS pods for SEP's Starship nosecones, after SEP's aft thrusters: a small bare-steel wedge with one short round
nozzle, two pods on the leeward side, a second MODEL on the parts in v3/patches/STMS_FwdRCS.cfg, which also swaps SEP's hull textures
in. KSP fires along a thruster's up axis: forward, canted outward so the push runs close to the stack's centre of mass."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import bmesh
from hls_common import sep_mat
V = Vector; CANT = 6.0
for variant, (AZ, Z0, R0, SL) in {'B3': (54, 2.46, 2.618, -.170), 'B1': (40, -.10, 2.637, -.165)}.items():          # azimuth, height, hull radius there, dr/dz
    P = start('STMS_FwdRCS_' + variant); MS = sep_mat(P, 'stms_steel', 'stms_steel_diff', 'stms_steel_nrm', 'stms_steelmask_diff'); g, dg = Geo(), Geo()
    for s in (-1, 1):
        a = math.radians(s * AZ); n = V((math.sin(a), -math.cos(a), -SL)).normalized(); up = V((0, 0, 1)); up = (up - up.dot(n) * n).normalized(); x = up.cross(n)
        F = Matrix((x, up, n)).transposed().to_4x4(); F.translation = V((R0 * math.sin(a), -R0 * math.cos(a), Z0))          # +Y up the hull, +Z out of it
        e = V((math.sin(a) * math.sin(math.radians(CANT)), -math.cos(a) * math.sin(math.radians(CANT)), math.cos(math.radians(CANT)))); el = F.to_3x3().inverted() @ e
        # wedge: wide foot, narrower top, running out to nothing aft; the front face square to the exhaust
        fy = lambda h: .16 - el.z / el.y * (h - .07)
        pts = [(w, y, h) for w, y, h in ((-.17, fy(-.06), -.06), (.17, fy(-.06), -.06), (-.10, fy(.15), .15), (.10, fy(.15), .15), (-.10, -.02, .15), (.10, -.02, .15), (-.15, -.40, -.06), (.15, -.40, -.06), (-.06, -.34, .02), (.06, -.34, .02))]
        bm = bmesh.new(); [bm.verts.new(p) for p in pts]; bmesh.ops.convex_hull(bm, input=bm.verts); bm.normal_update()
        bmesh.ops.bevel(bm, geom=[q for q in bm.edges if q.is_manifold and q.calc_face_angle() > .3], offset=.008, segments=1, affect='EDGES'); bm.normal_update()
        for f in bm.faces:
            b = len(g.v); g.v += [tuple(F @ v.co) for v in f.verts]; ax = max(range(3), key=lambda i: abs(f.normal[i])); uv = [(v.co[(0, 1, 0)[ax] if ax != 0 else 1], v.co[(0, 2, 1)[ax]]) for v in f.verts]
            g.face(list(range(b, b + len(f.verts))), [(0.3486 + p * .087, 0.1189 + q * .12) for p, q in uv])
        bm.free(); ex = e.cross(V((-math.cos(a), -math.sin(a), 0))).normalized(); ey = e.cross(ex); NF = Matrix((ex, ey, e)).transposed().to_4x4(); NF.translation = F @ V((0, fy(.06), .06))
        dg.add(cyl(.074, .012, 24, zone=Z.steel, bevel=.003, center_z=False), NF); dg.add(cyl(.060, .055, 24, zone=Z.steel, bevel=.006, center_z=False), NF); dg.add(cyl(.047, .0565, 24, zone=Z.black, center_z=False), NF)
        for t in range(6): dg.add(cyl(.006, .018, 6, zone=Z.steel, center_z=False), NF @ T(.068 * math.cos(t * TAU / 6), .068 * math.sin(t * TAU / 6), 0))
        TF = NF.copy(); TF.translation = NF @ V((0, 0, .055)); P.empty('STMS_FwdRCS', TF, P.model)
    P.mesh('stms_fwdrcs', g, MS, smooth_angle=20); P.mesh('stms_fwdrcs_nozzle', dg, P.det, smooth_angle=40); P.two_sided = True; finish(P)

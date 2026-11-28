"""Forward-firing RCS pods for SEP's Starship nosecones, after SEP's aft thrusters: a small bare-steel wedge with one short round
nozzle, two pods on the leeward side, a second MODEL on the parts in v3/patches/STMS_FwdRCS.cfg, which makes them an option and
swaps SEP's hull textures in; four on the fairing base. KSP fires along a thruster's up axis: forward, canted outward so the push runs close to the stack's centre of mass."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import bmesh
from hls_common import sep_mat
V = Vector; CANT = 6.0
ABL_EDGE = ((52.5, 2.164), (67.5, 2.581))      # (az, z): the diagonal edge of SEP's Ablative 43 where it crosses the Block 3 pods, measured
for variant, (AZ, Z0, R0, SL) in {'B3': (54, 2.46, 2.618, -.170), 'B1': (40, -.10, 2.637, -.165), 'B1C': (60, -.10, 2.637, -.165), 'FB': (45, .06, 2.8125, 0)}.items():          # azimuth, height, hull radius there, dr/dz
    P = start('STMS_FwdRCS_' + variant); MS = sep_mat(P, 'stms_steel', 'stms_steel_diff', 'stms_steel_nrm', 'stms_steelmask_diff'); g, dg, ga = Geo(), Geo(), Geo()
    for s in (-1, 1) + ((-3, 3) if variant == 'FB' else ()):          # the fairing base takes four, all round
        a = math.radians(s * AZ); n = V((math.sin(a), -math.cos(a), -SL)).normalized(); up = V((0, 0, 1)); up = (up - up.dot(n) * n).normalized(); x = up.cross(n)
        F = Matrix((x, up, n)).transposed().to_4x4(); F.translation = V((R0 * math.sin(a), -R0 * math.cos(a), Z0))          # +Y up the hull, +Z out of it
        e = V((math.sin(a) * math.sin(math.radians(CANT)), -math.cos(a) * math.sin(math.radians(CANT)), math.cos(math.radians(CANT)))); el = F.to_3x3().inverted() @ e
        # wedge: wide foot, narrower top, running out to nothing aft; the front face square to the exhaust
        fy = lambda h: .16 - el.z / el.y * (h - .07)
        pts = [(w, y, h) for w, y, h in ((-.17, fy(-.022), -.022), (.17, fy(-.022), -.022), (-.10, fy(.15), .15), (.10, fy(.15), .15), (-.10, -.02, .15), (.10, -.02, .15), (-.15, -.40, -.022), (.15, -.40, -.022), (-.06, -.34, .02), (.06, -.34, .02))]
        bm = bmesh.new(); [bm.verts.new(p) for p in pts]; bmesh.ops.convex_hull(bm, input=bm.verts); bm.normal_update()
        bmesh.ops.bevel(bm, geom=[q for q in bm.edges if q.is_manifold and q.calc_face_angle() > .3], offset=.008, segments=1, affect='EDGES'); bmesh.ops.triangulate(bm, faces=bm.faces); bm.normal_update()
        def lay(bm_, g_, push=0.0):
            for f in bm_.faces:
                b = len(g_.v); g_.v += [tuple(F @ (v.co + v.normal * push)) for v in f.verts]; ax = max(range(3), key=lambda i: abs(f.normal[i])); uv = [(v.co[(0, 1, 0)[ax] if ax != 0 else 1], v.co[(0, 2, 1)[ax]]) for v in f.verts]
                g_.face(list(range(b, b + len(f.verts))), [(0.3486 + p * .087, 0.1189 + q * .12) for p, q in uv])
        lay(bm, g)
        if variant == 'B3':                          # the part under the edge of SEP's extended ablative strip, as a skin 1.5 mm proud
            hp = lambda az, z: V((s / abs(s) * math.sin(math.radians(az)) * R0, -math.cos(math.radians(az)) * R0, z))
            A, B = hp(ABL_EDGE[0][0], ABL_EDGE[0][1]), hp(ABL_EDGE[1][0], ABL_EDGE[1][1]); Fi = F.inverted(); R3 = F.to_3x3().inverted()
            no = R3 @ (B - A).cross(n); co = Fi @ A; below = (Fi @ (A + V((0, 0, -.3))) - co).dot(no) > 0
            bm2 = bm.copy(); bmesh.ops.bisect_plane(bm2, geom=bm2.verts[:] + bm2.edges[:] + bm2.faces[:], plane_co=co, plane_no=no); bm2.normal_update()
            bmesh.ops.delete(bm2, geom=[f for f in bm2.faces if ((f.calc_center_median() - co).dot(no) > 0) != below], context='FACES'); bm2.normal_update()
            lay(bm2, ga, .0015); bm2.free()
        bm.free(); ex = e.cross(V((-math.cos(a), -math.sin(a), 0))).normalized(); ey = e.cross(ex); NF = Matrix((ex, ey, e)).transposed().to_4x4(); NF.translation = F @ V((0, fy(.06), .06))
        dg.add(cyl(.074, .012, 24, zone=Z.steel, bevel=.003, center_z=False), NF); dg.add(cyl(.060, .055, 24, zone=Z.steel, bevel=.006, center_z=False), NF); dg.add(cyl(.047, .0565, 24, zone=Z.black, center_z=False), NF)
        for t in range(6): dg.add(cyl(.006, .018, 6, zone=Z.steel, center_z=False), NF @ T(.068 * math.cos(t * TAU / 6), .068 * math.sin(t * TAU / 6), 0))
        TF = NF.copy(); TF.translation = NF @ V((0, 0, .055)); P.empty('STMS_FwdRCS', TF, P.model)
    # the housings hang under stms_fwdrcs_set (the Forward RCS switch). On Block 3 the edge of SEP's extended ablative strip crosses them,
    # so the part under it also comes as an ablative skin, which SEP's Ablative switch shows with Extended (B9 gives it SEP's textures)
    root = P.empty('stms_fwdrcs_set', Matrix(), P.model); P.mesh('stms_fwdrcs', g, MS, parent=root, frame=Matrix(), smooth_angle=20)
    if variant == 'B3': P.mesh('stms_fwdrcs_abl', ga, sep_mat(P, 'stms_fwdrcs_abl', 'stms_steel_diff', 'stms_steel_nrm', 'stms_steelmask_diff'), parent=root, frame=Matrix(), smooth_angle=20)
    P.mesh('stms_fwdrcs_nozzle', dg, P.det, smooth_angle=40); P.two_sided = True; finish(P)

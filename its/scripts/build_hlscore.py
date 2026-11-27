"""HLS core: tanks, engine bay for SEP's Raptors, black leg panels, landing thruster band, elevator track."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Core'); MH = None
CELL = HL.PITCH; d = Geo(); import bmesh
bores = [g + k * CELL for g in HL.GROUPS for k in (-1, 0, 1)]
inb = lambda az: any(abs(wrap(az - b)) < CELL / 2 for b in bores)
for SH_, SX, (B0, B1), BORE_ in (('core', '', HL.BAND, HL.BORE), ('core_o', '_o', HL.O_BAND, HL.O_BORE)):      # the 2024 render's skin, and the original's
    zs = [0, .30, HL.Z_BLACK, 2.2, 3.5, 4.85, 8, 12, 16, B0, B1, HL.Z_SKIN]
    hull = skin(zs, SH_, keep=lambda a, z: not (B0 < z < B1 and inb(a)))
    zm = (B0 + B1) / 2; bell = Geo(); dk = Geo()
    for b in bores:
        # patch: the cell's rectangle down to an ellipse, sampled where the facets change so nothing gaps
        w = math.degrees(BORE_[0] / HL.R); h = BORE_[1]; HW, HH = CELL / 2, (B1 - B0) / 2
        pts = [(-HW + t * CELL / 3, -HH) for t in (0, 1, 2)]
        pts += [(HW, -HH + t * 2 * HH / 5) for t in range(5)] + [(HW - t * CELL / 3, HH) for t in range(3)] + [(-HW, HH - t * 2 * HH / 5) for t in range(5)]
        def ell(x, y):
            t = math.atan2(y / HH, x / HW); return w * math.cos(t), h * math.sin(t)
        N = len(pts); fine = []
        for i in range(N):                                   # two ellipse points per outer edge
            a, c = pts[i], pts[(i + 1) % N]
            fine += [(a[0] + (c[0] - a[0]) * t / 2, a[1] + (c[1] - a[1]) * t / 2) for t in range(2)]
        M = len(fine); n0 = len(hull.v); uvf = lambda x, y: huv(b + x, zm + y, SH_)
        inner = [ell(*p) for p in fine]
        for lst in (fine, inner): hull.v += [tuple(hp(b + x, zm + y)) for x, y in lst]
        for i in range(M):
            j = (i + 1) % M
            hull.face([n0 + i, n0 + j, n0 + M + j, n0 + M + i], [uvf(*fine[i]), uvf(*fine[j]), uvf(*inner[j]), uvf(*inner[i])])
        # oblique duct to a bell whose axis is canted down
        a = math.radians(b); out = V((math.sin(a), -math.cos(a), 0)); c_ = math.radians(HL.CANT)
        ax = out * math.cos(c_) + V((0, 0, -1)) * math.sin(c_)
        c0 = hp(b, zm); q = frame_axes(c0, ax, x=V((math.cos(a), math.sin(a), 0)))
        rim = [hp(b + x, zm + y) for x, y in inner]
        loc = [q.inverted() @ p for p in rim]
        rows = [rim]
        for dep, f in ((-.40, .93), (-.48, .96), (-.62, .80), (-.80, .56), (-.95, .33), (-1.02, .24)):
            rows.append([q @ V((p.x / max(1e-6, math.hypot(p.x, p.y)) * BORE_[0] * f, p.y / max(1e-6, math.hypot(p.x, p.y)) * BORE_[0] * f, dep)) for p in loc])
        def band_(g, r0, r1, zone, t0, t1):
            n = len(g.v); g.v += [tuple(p) for p in r0 + r1]
            for i in range(M):
                j = (i + 1) % M
                g.face([n + i, n + j, n + M + j, n + M + i], [zone.uv(i / M, t0), zone.uv((i + 1) / M, t0), zone.uv((i + 1) / M, t1), zone.uv(i / M, t1)])
        band_(dk, rows[0], rows[1], Z.black, 0, .4); band_(dk, rows[1], rows[2], Z.steel, 0, .1)
        for k in range(2, len(rows) - 1): band_(bell, rows[k], rows[k + 1], Z.invar, (k - 2) / 5, (k - 1) / 5)
        n = len(bell.v); bell.v += [tuple(p) for p in rows[-1]] + [tuple(sum(rows[-1], V()) / M)]
        for i in range(M): bell.face([n + i, n + (i + 1) % M, n + M], [Z.black.uv(.2, .2), Z.black.uv(.3, .2), Z.black.uv(.25, .3)])
        # thrust transform: KSP pushes along -forward; Unity forward is Blender local +Y here
        if SH_ == 'core_o': continue
        P.empty('landingThrust', None, P.model)
        e = bpy.data.objects[[o.name for o in P.coll.objects if o.name.startswith('landingThrust')][-1]]
        y = ax.normalized(); x = V((math.cos(a), math.sin(a), 0)); z_ = x.cross(y); m = Matrix((x, y, z_)).transposed().to_4x4(); m.translation = c0 - ax * .44
        if 75 < b < 109 or 251 < b < 285: m = Rz(1.875 if b > 180 else -1.875) @ m      # the beam groups sit a half facet off; their thrust does not, so it balances
        P.place(e, m, P.model)
    ho = P.mesh('hull' + SX, hull, hull_mat(P, 'hls_' + SH_), smooth_angle=30)
    # weld the patches to the skin so the shading runs across
    bm = bmesh.new(); bm.from_mesh(ho.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-4); bm.to_mesh(ho.data); bm.free()
    P.mesh('bells' + SX, bell, P.det, smooth_angle=60); P.mesh('ducts' + SX, dk, P.det, smooth_angle=40)
B0, B1 = HL.BAND; zm = (B0 + B1) / 2
# ---------------- elevator track: rails, rungs and stiles on the outside of the tank wall, a mesh of their own so they can be left off
TR = HL.TRACK; RR = HL.R; ZT = HL.Z_SKIN; tk = Geo()
for s in (-1, 1):
    x = s * (HL.TRACK_R * math.sin(math.radians(TR)) - .035); y = -RR
    tk.add(box(.05, .09, ZT - .06, zone=Z.alu, bevel=.01, center=(x, y - .03, ZT / 2)))
    tk.add(box(.02, .05, ZT - .06, zone=Z.steel, center=(x - s * .02, y - .075, ZT / 2)))
    for z in np.arange(1.0, ZT - .3, 1.6): tk.add(box(.09, .05, .12, zone=Z.grey, bevel=.008, center=(x, y - .0, float(z))))
    tk.add(box(.02, .07, ZT - .2, zone=Z.grey, center=(s * .16, -RR - .025, ZT / 2)))
for z in np.arange(.35, ZT - .05, .38): tk.add(tube([(-.16, -RR - .05, float(z)), (.16, -RR - .05, float(z))], .012, 5, zone=Z.steel))
P.mesh('track', tk, P.det, smooth_angle=40)
# ---------------- engine bay, laid out as on SEP's Block 3 ship: hat-stringer skirt with four hoops, flat ring, cone, engine puck
from mathutils.geometry import delaunay_2d_cdt
ZP = HL.Z_SL; RI = 2.787; ZC = 2.25; RC0, RC1 = 1.09, 1.98; WR = .47; aft = Geo()
MA = sep_mat(P, 'hls_aft', 'hls_aft_diff', 'hls_aft_nrm', 'stms_steelmask_diff')
SW_ = {'dark': (.01, .90), 'straw': (.90, .90), 'black': (.01, .01), 'bright': (.90, .01)}        # swatches in the sheet's corners, .09 wide
class _S:
    def __init__(s, k): s.o = SW_[k]
    def uv(s, a, b): return (s.o[0] + .09 * (a % 1.0001), s.o[1] + .09 * (b % 1.0001))
    def uv_m(s, a, b, offs=(0, 0)): return s.uv(a * .4, b * .4)
S = {k: _S(k) for k in SW_}; puv = lambda x, y: (.5 + x / 6.6, .5 + y / 6.6)
def rev(prof, k, n, m=None, a0=0.0):                       # surface of revolution in one swatch
    g = Geo(); g.v = [(r * math.sin(TAU * i / n + a0), -r * math.cos(TAU * i / n + a0), z) for r, z in prof for i in range(n)]
    for q in range(len(prof) - 1):
        for i in range(n):
            i2 = (i + 1) % n; t0, t1 = (i % 8) / 8, (i % 8 + 1) / 8
            g.face([q * n + i, (q + 1) * n + i, (q + 1) * n + i2, q * n + i2], [S[k].uv(u_, .05 + .9 * w_ / len(prof)) for u_, w_ in ((t0, q), (t0, q + 1), (t1, q + 1), (t1, q))])
    aft.add(g, m) if m is not None else aft.add(g)
vac = [(HL.R_VAC * math.sin(math.radians(a)), -HL.R_VAC * math.cos(math.radians(a))) for a in (60, 180, 300)]
sl = [(HL.R_SL * math.sin(math.radians(a)), -HL.R_SL * math.cos(math.radians(a))) for a in (0, 120, 240)]
hz = lambda r: ZP + (ZC - ZP) * min(1, max(0, (r - RC0) / (RC1 - RC0)))
holes = [(x, y, WR, HL.Z_VAC) for x, y in vac] + [(x, y, .19, 2.14) for x, y in sl] + [(x * .52, y * .52, .062, 2.1) for x, y in sl]
loops = [circ(RC0, 48), circ(RC1, 96), circ(RI, 96)] + [circ(r, 32, x, y) for x, y, r, _ in holes]
pv, pe = [], []
for l in loops: b = len(pv); pv += [V(p) for p in l]; pe += [(b + i, b + (i + 1) % len(l)) for i in range(len(l))]
ov, _, of, *_ = delaunay_2d_cdt(pv, pe, [], 0, 1e-5)
pl = Geo(); pl.v = [(p.x, p.y, hz(math.hypot(p.x, p.y))) for p in ov]
for t_ in of:
    for k in range(1, len(t_) - 1):
        t = [t_[0], t_[k], t_[k + 1]]; p = [ov[i] for i in t]; m = sum(p, V((0, 0))) / 3
        if math.hypot(m.x, m.y) > RI or any(math.hypot(m.x - x, m.y - y) < r - 1e-3 for x, y, r, _ in holes): continue
        s_ = (p[1] - p[0]).cross(p[2] - p[0])
        if abs(s_) < 1e-9: continue
        t = t if s_ < 0 else t[::-1]; pl.face(t, [puv(ov[i].x, ov[i].y) for i in t])
P.mesh('aftplate', pl, MA, smooth_angle=12)
for x, y, r, top in holes:                                 # bores and their rims, following the cone
    n = 32; rim = [(x + r * math.cos(TAU * i / n), y + r * math.sin(TAU * i / n)) for i in range(n)]; b = Geo()
    hr = [hz(math.hypot(*p)) for p in rim]; th = .022 if r > .1 else .01
    rows = [[(x + (q[0] - x) * (1 + th / r), y + (q[1] - y) * (1 + th / r), h + .002) for q, h in zip(rim, hr)], [(x + (q[0] - x) * (1 + th / r * .7), y + (q[1] - y) * (1 + th / r * .7), h - th) for q, h in zip(rim, hr)],
            [(q[0], q[1], h - th) for q, h in zip(rim, hr)], [(q[0], q[1], top) for q in rim]]
    for l in rows: b.v += l
    for q in range(3):
        for i in range(n): i2 = (i + 1) % n; b.face([q * n + i, q * n + i2, (q + 1) * n + i2, (q + 1) * n + i][::-1], [S['bright'].uv(u_, w_) for u_, w_ in ((i / n, q / 3), ((i + 1) / n, q / 3), ((i + 1) / n, q / 3 + .3), (i / n, q / 3 + .3))][::-1])
    c_ = len(b.v); b.v.append((x, y, top)); [b.face([3 * n + i, 3 * n + (i + 1) % n, c_][::-1], [S['black'].uv(.2, .2), S['black'].uv(.3, .2), S['black'].uv(.25, .3)]) for i in range(n)]
    aft.add(b)
rev([(HL.R, 0), (RI, 0)], 'bright', HL.SIDES); rev([(RI, 0), (RI, ZC)], 'dark', HL.SIDES)
NH = 144
for k in range(NH):                                        # hat stringers, open sections against the wall
    a = TAU * (k + .5) / NH; g = Geo(); z0, z1 = .03, ZC - .01; hh = [(-.036, RI), (-.020, RI - .05), (.020, RI - .05), (.036, RI)]
    g.v = [(rr * math.sin(a) + w * math.cos(a), -rr * math.cos(a) + w * math.sin(a), z) for z in (z0, z1) for w, rr in hh]
    for i in range(3): g.face([i, 4 + i, 5 + i, i + 1], [S['dark'].uv(u_, w_) for u_, w_ in ((.3 * i, 0), (.3 * i, 1), (.3 * i + .3, 1), (.3 * i + .3, 0))])
    g.face([0, 1, 2, 3], [S['bright'].uv(.1, .1), S['bright'].uv(.2, .2), S['bright'].uv(.3, .2), S['bright'].uv(.4, .1)]); aft.add(g)
for za, zb in ((.365, .42), (.825, .88), (1.285, 1.34), (2.06, 2.15)):      # hoops: web and flange, straw tinted
    rev([(RI, za), (2.69, za), (2.69, zb), (RI, zb)], 'straw', HL.SIDES)
    g = Geo()
    for k in range(NH):                                    # clips that tie each stringer to the hoops, above and below
        a0, a1 = TAU * (k + .12) / NH, TAU * (k + .88) / NH
        for z0, z1 in ((za, za - .035), (zb, zb + .035)):
            b = len(g.v); g.v += [(rr * math.sin(q), -rr * math.cos(q), z) for q, rr, z in ((a0, 2.728, z0), (a1, 2.728, z0), ((a0 * .75 + a1 * .25), 2.728, z1), ((a0 * .25 + a1 * .75), 2.728, z1))]
            f_ = [b, b + 1, b + 3, b + 2]; u_ = [S['straw'].uv(*q) for q in ((.1, .1), (.5, .1), (.4, .3), (.2, .3))]
            g.face(f_[::-1], u_[::-1]) if z1 > z0 else g.face(f_, u_)
    aft.add(g)
rev([(RI, ZC - .055), (RI - .05, ZC - .05), (RI - .05, ZC)], 'dark', HL.SIDES)
for a in (15, 135, 255):                                   # engine bay cameras on the upper hoop
    d.add(box(.10, .12, .09, zone=Z.dark, bevel=.015), on_cyl(a, 2.0, 2.68)); d.add(cyl(.028, .03, 14, zone=Z.rubber), on_cyl(a, 2.0, 2.61))
ab = P.mesh('aftbay', aft, MA, smooth_angle=25); ab['facing_ok'] = True
for i, (x, y) in enumerate(vac): P.node(f'vac{i + 1}', (x, y, HL.Z_VAC), (0, 0, -1), 1)
for i, (x, y) in enumerate(sl): P.node(f'sl{i + 1}', (x, y, ZP), (0, 0, -1), 1)
# ---------------- forward dome
d.add(lathe([(2.76, 20.1), (2.76, 20.35), (2.6, 20.52), (2.36, 20.67)], 96, zone=Z.alu))
d.add(lathe([(2.36, 20.1), (2.36, 20.67), (2.2, 20.76), (1.6, 20.95), (.9, 21.06), (0, 21.1)], 96, zone=Z.dome))
d.add(lathe([(HL.R - .004, HL.Z_SKIN), (2.76, HL.Z_SKIN), (2.76, 20.1)], 96, zone=Z.alu))
# ---------------- leg hinges, lights, flush details
for az in HL.LEG_AZ:
    for s in (-1, 1): d.add(lay(box(.10, .55, .05, zone=Z.black, bevel=.015), az + s * 6.2, HL.HINGE[1], L_=.2))
for az in HL.LIGHT_AZ: d.add(lay(rounded_rect_ring(.11, .36, .05, .03, .025, 4, zone=Z.dark), az, zm))
LM = lamp_mat(P); lamp = Geo(); rd = Geo(); gr = Geo()
for s in (-1, 1):                                        # base floodlights either side of the track
    d.add(lay(box(.34, .13, .10, zone=Z.white, bevel=.02), s * 12.5, 4.85 + .05)); lamp.add(lay(box(.28, .02, .06, zone=Z.lamp), s * 12.5, 4.85 - .02, sink=-.04))
    add_spot(P, 'baseLight', hp(s * 12.5, 4.85 - .05, .12), (0, -.35, -1), power=260, angle=95, reach=14)
for az in HL.LIGHT_AZ: (gr if az < 180 else rd).add(lay(box(.05, .28, .016, zone=Z.lamp), az, zm))
P.mesh('lampglow', lamp, LM); P.mesh('navgreen', gr, P.material('hls_det', nrm='its_det', shader='KSP/Emissive/Bumped Specular', spec=(.12, .12, .12), shininess=.3, emissive='hls_green_emit', name='hls_green'))
P.mesh('navred', rd, P.material('hls_det', nrm='its_det', shader='KSP/Emissive/Bumped Specular', spec=(.12, .12, .12), shininess=.3, emissive='hls_red_emit', name='hls_red'))
f = Geo()                                                # quick-disconnect plate and refuelling interface on the docking side
f.add(lay(box(.9, .6, .02, zone=Z.alu, bevel=.008), 180, 2.6)); [f.add(lay(cyl(.1, .05, 18, zone=Z.dark, bevel=.01), 180 + s * 4.5, 2.6)) for s in (-1, 0, 1)]
d.add(f)
spots = []
for az in (68, 112, 248, 292):
    for z in (6.2,): spots += [(az, z, (1, 0, .35)), (az, z + .28, (-1, 0, .35)), (az, z + .56, (0, 1, .35)), (az, z - .28, (0, -1, .35))]
rcs(P, d, spots)
# ---------------- leg pods: faceted fairings with an arched opening the leg lives in and swings out of; a switch hides them
pod, pin = Geo(), Geo(); OW, OT, OR = HL.POD_OPEN
pw = lambda z, k: float(np.interp(z, [q[0] for q in HL.POD], [q[k] for q in HL.POD]))
owz = lambda z: OW if z <= OT - OR else OW - OR + math.sqrt(max(0, OR ** 2 - (z - OT + OR) ** 2))
hy = lambda x: -math.sqrt(HL.R ** 2 - x * x) + .03; ZK, ZE = HL.POD[1][0], HL.POD[2][0]
def fy_(z, x=0.0):                                       # the front: flat up to the kink, then bending into the hull's curve, so its top edge sinks in all along
    if z <= ZK: return -(HL.R + pw(z, 1))
    t = (z - ZK) / (ZE - ZK); return -(HL.R + HL.POD[1][1]) * (1 - t) + hy(x) * t
def pq(g, pts, M, zone=None):                            # hull paint, from a plain stretch of the core's sheet, laid on as one piece
    if g is pod:
        b = len(g.v); g.v += [tuple(M @ V(p)) for p in pts]; g.face(range(b, b + 4), [huv(80 + math.degrees(math.atan2(p[0], -p[1])), 7.75 + p[2] * .3, 'core') for p in pts])
    else: b = len(g.v); g.v += [tuple(M @ V(p)) for p in pts]; g.face(range(b, b + 4), [zone.uv(*t) for t in ((.1, .1), (.2, .1), (.2, .2), (.1, .2))])
zp = [0, 1.2, 2.4, 3.6] + [OT - OR + OR * math.sin(math.radians(t)) for t in (0, 22.5, 45, 67.5, 90)] + [ZK, 5.3, 5.65, 6.0, 6.35, 6.65, ZE]; NX = 6; NS = 2
for az in HL.LEG_AZ:
    M = Rz(az)
    for z0_, z1_ in zip(zp, zp[1:]):
        o0, o1 = owz(z0_), owz(z1_); op = z1_ <= OT + 1e-6
        for s in (-1, 1):
            b0, b1, t0, t1 = pw(z0_, 2), pw(z1_, 2), pw(z0_, 3), pw(z1_, 3)
            side = lambda z, b, t, k: (s * (b + (t - b) * k / NS), hy(b) + (fy_(z, t) - hy(b)) * k / NS, z)
            for k in range(NS): f = [side(z0_, b0, t0, k), side(z0_, b0, t0, k + 1), side(z1_, b1, t1, k + 1), side(z1_, b1, t1, k)]; pq(pod, f if s < 0 else f[::-1], M)
            i0, i1 = (o0, o1) if op else (0, 0)
            fr = lambda z, a, t, k: (s * (t + (a - t) * k / NX), fy_(z, t + (a - t) * k / NX), z)
            for k in range(NX): f = [fr(z0_, i0, t0, k), fr(z0_, i0, t0, k + 1), fr(z1_, i1, t1, k + 1), fr(z1_, i1, t1, k)]; pq(pod, f if s < 0 else f[::-1], M)
            if op:                                       # reveal round the opening, dark inside
                f = [(s * o0, fy_(z0_), z0_), (s * o0, hy(o0) + .02, z0_), (s * o1, hy(o1) + .02, z1_), (s * o1, fy_(z1_), z1_)]; pq(pin, f if s < 0 else f[::-1], M, Z.black)
            if z0_ == 0: f = [(s * b0, hy(b0), 0), (s * o0, hy(o0), 0), (s * o0, fy_(0), 0), (s * t0, fy_(0), 0)]; pq(pod, f if s < 0 else f[::-1], M)
    o = owz(OT); pq(pin, [(-o, fy_(OT), OT), (-o, hy(o) + .02, OT), (o, hy(o) + .02, OT), (o, fy_(OT), OT)], M, Z.black)
    for s in (-1, 1): P.hull_collider('col_pod%d%s' % (az, 'ab'[s > 0]), [tuple(M @ V(p)) for z in (.0, 4.6) for p in ((s * pw(z, 2), hy(pw(z, 2)), z), (s * pw(z, 3), fy_(z), z), (s * OW, fy_(z), z), (s * OW, hy(OW), z))])
    P.hull_collider('col_pod%dt' % az, [tuple(M @ V(p)) for s in (-1, 1) for z in (4.66, 4.95, 6.85) for p in ((s * pw(z, 2), hy(pw(z, 2)), z), (s * pw(z, 3), fy_(z), z))])
lp_ = P.mesh('legpods', pod, hull_mat(P, 'hls_core'), smooth_angle=20); bm = bmesh.new(); bm.from_mesh(lp_.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-4); bm.to_mesh(lp_.data); bm.free(); P.mesh('legpods_in', pin, P.det, smooth_angle=40)
P.mesh('details', d, P.det, smooth_angle=40)
# hull cameras (its/patches/STMS_Cameras.cfg), numbered as on the ship: 1 landing (low, looking down past the legs), 2 engine bay,
# 3 a leg and its footpad, 4 the docking hardware on the far side. +Y looks, +Z is the picture's up
cm = Geo(); rad = lambda az: V((math.sin(math.radians(az)), -math.cos(math.radians(az)), 0))
def camf(p, look, up):
    y = V(look).normalized(); z = V(up); z = (z - z.dot(y) * y).normalized(); m = Matrix((y.cross(z), y, z)).transposed().to_4x4(); m.translation = V(p); return m
for cid, az, z, look, pod in ((1, 0, 2.6, None, True), (3, 22, 7.6, rad(45) * HL.FOOT_R + V((0, 0, HL.SOLE + .3)), True), (4, 160, HL.Z_DOCK + 1.6, V((0, HL.R_DOCK + 1.5, HL.Z_DOCK)), True)):
    p0 = rad(az) * (HL.R + .035) + V((0, 0, z)); lk = (V((0, 0, -1)) + rad(az) * .18) if look is None else (look - p0)
    p = p0 + V((0, 0, .085 if lk.z > 0 else -.085))      # the camera at the housing's front face, the end it looks from
    P.empty(f'stms_cam{cid}', camf(p, lk, rad(az) if look is None else V((0, 0, 1))), P.model)
    Fh = Matrix((rad(az + 90), V((0, 0, 1)), rad(az))).transposed().to_4x4(); Fh.translation = rad(az) * (HL.R - .01) + V((0, 0, z))
    cm.add(box(.11, .15, .08, zone=Z.dark, bevel=.014, center=(0, 0, .04)), Fh); cm.add(cyl(.03, .04, 12, zone=Z.black), camf(p, lk, V((0, 0, 1))) @ Rx(90))
pe = rad(25) * (HL.R - .45) + V((0, 0, 1.6)); P.empty('stms_cam2', camf(pe, V((0, 0, -1.5)) - pe, -rad(25)), P.model)      # inside the engine bay, no pod
P.mesh('stms_campods', cm, P.det, smooth_angle=40)
# ---------------- nodes and colliders
P.node('top', (0, 0, HL.Z_TOP), (0, 0, 1), 5); P.node('bottom', (0, 0, 0), (0, 0, -1), 5)
P.node('docking', (0, HL.R_DOCK, HL.Z_DOCK), (0, 1, 0), 2)
for i, az in enumerate(HL.LEG_AZ):
    p = on_cyl(az, HL.HINGE[1], HL.R); P.node(f'leg{i + 1}', p.translation, p.to_3x3() @ V((0, 0, 1)), 1); P.node(f'shroud{i + 1}', p.translation + p.to_3x3() @ V((0, 0, .0)), p.to_3x3() @ V((0, 0, 1)), 2)
def arcs(a0, a1, r0, r1, z0, z1, n):
    return [tuple(hp(a0 + (a1 - a0) * i / n, z, r=r)) for i in range(n + 1) for r in (r0, r1) for z in (z0, z1)]
for i, (a0, a1) in enumerate(((0, 90), (90, 180), (180, 270), (270, 360))):
    P.hull_collider(f'col_body{i}', [tuple(hp(a0 + (a1 - a0) * k / 8, z)) for k in range(9) for z in (ZC, HL.Z_SKIN)] + [tuple(hp(a0 + (a1 - a0) * k / 4, ZP, r=RC0)) for k in range(5)] + [(0, 0, ZP), (0, 0, HL.Z_SKIN)])
for k in range(16):
    a0, a1 = 22.5 * k, 22.5 * (k + 1); P.hull_collider(f'col_skirt{k}', arcs(a0, a1, HL.R, RI, 0, ZC, 2))
P.hull_collider('col_dome', [tuple(hp(a, z, r=r)) for a in range(0, 360, 30) for z, r in ((20.5, 2.6), (20.95, 1.6))])
P.box_trigger('ladder', climb_frame((0, -RR - .14, HL.Z_SKIN / 2 + .3), (0, -1, 0)), (.5, .3, HL.Z_SKIN - .3), 'Ladder')
finish(P, ({'hull', 'bells', 'ducts', 'legpods', 'legpods_in'}, {'hull_o', 'bells_o', 'ducts_o'}))

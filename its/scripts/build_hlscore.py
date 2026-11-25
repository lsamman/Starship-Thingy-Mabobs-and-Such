"""HLS core: tanks, engine bay for SEP's Raptors, black leg panels, landing thruster band, elevator track."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Core'); MH = hull_mat(P, 'hls_core')
B0, B1 = HL.BAND; CELL = HL.PITCH
bores = [g + k * CELL for g in HL.GROUPS for k in (-1, 0, 1)]
inb = lambda az: any(abs(wrap(az - b)) < CELL / 2 for b in bores)
zs = [0, .30, HL.Z_BLACK, 2.2, 3.5, HL.PANEL_TOP, 8, 12, 16, B0, B1, HL.Z_SKIN]
hull = skin(zs, 'core', keep=lambda a, z: not (B0 < z < B1 and inb(a)))
zm = (B0 + B1) / 2; d = Geo(); bell = Geo(); ND = []
for b in bores:
    # patch: the cell's rectangle down to an ellipse, sampled where the facets change so nothing gaps
    w = math.degrees(HL.BORE[0] / HL.R); h = HL.BORE[1]; HW, HH = CELL / 2, (B1 - B0) / 2
    pts = [(-HW + t * CELL / 3, -HH) for t in (0, 1, 2)]
    pts += [(HW, -HH + t * 2 * HH / 5) for t in range(5)] + [(HW - t * CELL / 3, HH) for t in range(3)] + [(-HW, HH - t * 2 * HH / 5) for t in range(5)]
    def ell(x, y):
        t = math.atan2(y / HH, x / HW); return w * math.cos(t), h * math.sin(t)
    N = len(pts); fine = []
    for i in range(N):                                   # two ellipse points per outer edge
        a, c = pts[i], pts[(i + 1) % N]
        fine += [(a[0] + (c[0] - a[0]) * t / 2, a[1] + (c[1] - a[1]) * t / 2) for t in range(2)]
    M = len(fine); n0 = len(hull.v); uvf = lambda x, y: huv(b + x, zm + y, 'core')
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
        rows.append([q @ V((p.x / max(1e-6, math.hypot(p.x, p.y)) * HL.BORE[0] * f, p.y / max(1e-6, math.hypot(p.x, p.y)) * HL.BORE[0] * f, dep)) for p in loc])
    def band_(g, r0, r1, zone, t0, t1):
        n = len(g.v); g.v += [tuple(p) for p in r0 + r1]
        for i in range(M):
            j = (i + 1) % M
            g.face([n + i, n + j, n + M + j, n + M + i], [zone.uv(i / M, t0), zone.uv((i + 1) / M, t0), zone.uv((i + 1) / M, t1), zone.uv(i / M, t1)])
    band_(d, rows[0], rows[1], Z.black, 0, .4); band_(d, rows[1], rows[2], Z.steel, 0, .1)
    for k in range(2, len(rows) - 1): band_(bell, rows[k], rows[k + 1], Z.invar, (k - 2) / 5, (k - 1) / 5)
    n = len(bell.v); bell.v += [tuple(p) for p in rows[-1]] + [tuple(sum(rows[-1], V()) / M)]
    for i in range(M): bell.face([n + i, n + (i + 1) % M, n + M], [Z.black.uv(.2, .2), Z.black.uv(.3, .2), Z.black.uv(.25, .3)])
    # thrust transform: KSP pushes along -forward; Unity forward is Blender local +Y here
    P.empty('landingThrust', None, P.model)
    e = bpy.data.objects[[o.name for o in P.coll.objects if o.name.startswith('landingThrust')][-1]]
    y = ax.normalized(); x = V((math.cos(a), math.sin(a), 0)); z_ = x.cross(y); m = Matrix((x, y, z_)).transposed().to_4x4(); m.translation = c0 - ax * .44
    if 75 < b < 109 or 251 < b < 285: m = Rz(1.875 if b > 180 else -1.875) @ m      # the beam groups sit a half facet off; their thrust does not, so it balances
    P.place(e, m, P.model)
ho = P.mesh('hull', hull, MH, smooth_angle=30)
import bmesh                                             # weld the patches to the skin so the shading runs across
bm = bmesh.new(); bm.from_mesh(ho.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-4); bm.to_mesh(ho.data); bm.free()
P.mesh('bells', bell, P.det, smooth_angle=60)
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
# ---------------- base: lip, inner skirt, stringers, engine plate with wells for SEP's vacuum Raptors
ZP = HL.Z_SL; RI = 2.77
d.add(lathe([(HL.R, 0), (HL.R - .16, 0)], HL.SIDES, zone=Z.alu, flip=True))
d.add(lathe([(RI - .035, 0), (RI - .035, .05), (RI, .05)], HL.SIDES, zone=Z.dark, flip=True))
d.add(lathe([(RI, .05), (RI, ZP)], HL.SIDES, zone=Z.wall, flip=True))
for k in range(48):
    az = 3.75 + 7.5 * k
    d.add(box(.045, .05, ZP - .1, zone=Z.alu, bevel=.008), on_cyl(az, ZP / 2, RI - .012) @ Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1))))
    a, c = on_cyl(az - 3, .09, RI - .022).translation, on_cyl(az + 3, .36, RI - .022).translation
    d.add(strut(a, c, .013, Z.grey, 5)); d.add(strut(on_cyl(az + 3, .09, RI - .022).translation, on_cyl(az - 3, .36, RI - .022).translation, .013, Z.grey, 5))
d.add(ring(RI - .035, RI, .36, .42, Z.alu, 96)); d.add(ring(RI - .04, RI, 1.12, 1.18, Z.alu, 96))
vac = [(HL.R_VAC * math.sin(math.radians(a)), -HL.R_VAC * math.cos(math.radians(a))) for a in (60, 180, 300)]
outer = [(p.x, p.y) for p in (hp(a, 0, r=RI) for a in np.arange(0, 359.9, 3.75))]
WR = .56
d.add(plate(outer, [circ(WR, 32, *v) for v in vac], ZP, Z.dome))
for i, (x, y) in enumerate(vac):
    d.add(lathe([(WR, ZP), (WR, HL.Z_VAC), (0, HL.Z_VAC)], 32, zone=Z.dark, flip=True), T(x, y, 0))
    d.add(lathe([(WR + .07, ZP), (WR + .06, ZP - .035), (WR + .005, ZP - .035), (WR, ZP)], 32, zone=Z.alu, flip=True), T(x, y, 0))
    P.node(f'vac{i + 1}', (x, y, HL.Z_VAC), (0, 0, -1), 1)
for i, a in enumerate((0, 120, 240)):
    P.node(f'sl{i + 1}', (HL.R_SL * math.sin(math.radians(a)), -HL.R_SL * math.cos(math.radians(a)), ZP), (0, 0, -1), 1)
d.add(lathe([(1.12, ZP), (1.10, ZP - .05), (1.02, ZP - .06), (1.02, ZP - .004)], 48, zone=Z.alu, flip=True))
for a in (0, 120, 240):                                  # feed lines and boxes between the engines
    for q in (-14, 14):
        p = [on_cyl(a + q, ZP - .05, r).translation for r in (1.15, 1.6, 2.3, 2.66)]; d.add(tube(p, .05, 10, zone=Z.alu))
    d.add(box(.5, .34, .13, zone=Z.white, bevel=.02), Rz(a) @ T(0, -2.42, ZP - .06) if a else Rz(0) @ T(.55, -2.2, ZP - .06))
    d.add(tube([on_cyl(a + 33, ZP + .01, 1.16).translation, on_cyl(a + 33, ZP - .08, 1.3).translation, on_cyl(a + 33, ZP + .01, 1.44).translation], .04, 8, zone=Z.copper))
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
    d.add(lay(box(.34, .13, .10, zone=Z.white, bevel=.02), s * 12.5, HL.PANEL_TOP + .05)); lamp.add(lay(box(.28, .02, .06, zone=Z.lamp), s * 12.5, HL.PANEL_TOP - .02, sink=-.04))
    add_spot(P, 'baseLight', hp(s * 12.5, HL.PANEL_TOP - .05, .12), (0, -.35, -1), power=260, angle=95, reach=14)
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
def pq(g, pts, zone, M):                                 # quad facing the way its points turn, planar mapped
    n = len(g.v); g.v += [tuple(M @ V(p)) for p in pts]; o_, e1 = V(pts[0]), (V(pts[1]) - V(pts[0])); L1 = max(e1.length, 1e-6); e2 = V(pts[-1]) - V(pts[0]); g.face(range(n, n + len(pts)), [zone.uv(min(1, max(0, (V(p) - o_).dot(e1) / L1 / 7)), min(1, max(0, (p[2] - pts[0][2]) / 7))) for p in pts])
pw = lambda z, k: float(np.interp(z, [q[0] for q in HL.POD], [q[k] for q in HL.POD]))
owz = lambda z: OW if z <= OT - OR else OW - OR + math.sqrt(max(0, OR ** 2 - (z - OT + OR) ** 2))
hy = lambda x: -math.sqrt(HL.R ** 2 - x * x) + .03; fy_ = lambda z: -(HL.R + pw(z, 1)) + .03 * (z >= HL.POD[-1][0] - 1e-6)
zp = [0, 1.2, 2.4, 3.6] + [OT - OR + OR * math.sin(math.radians(t)) for t in (0, 22.5, 45, 67.5, 90)] + [HL.POD[1][0], 5.6, 6.25, HL.POD[2][0]]
for az in HL.LEG_AZ:
    M = Rz(az)
    for z0_, z1_ in zip(zp, zp[1:]):
        o0, o1 = owz(z0_), owz(z1_); op = z1_ <= OT + 1e-6
        for s in (-1, 1):
            b0, b1, t0, t1 = pw(z0_, 2), pw(z1_, 2), pw(z0_, 3), pw(z1_, 3)
            f = [(s * b0, hy(b0), z0_), (s * t0, fy_(z0_), z0_), (s * t1, fy_(z1_), z1_), (s * b1, hy(b1), z1_)]; pq(pod, f if s < 0 else f[::-1], Z.white, M)
            i0, i1 = (o0, o1) if op else (0, 0)
            f = [(s * t0, fy_(z0_), z0_), (s * i0, fy_(z0_), z0_), (s * i1, fy_(z1_), z1_), (s * t1, fy_(z1_), z1_)]; pq(pod, f if s < 0 else f[::-1], Z.white, M)
            if op:                                       # reveal round the opening, dark inside
                f = [(s * o0, fy_(z0_), z0_), (s * o0, hy(o0) + .02, z0_), (s * o1, hy(o1) + .02, z1_), (s * o1, fy_(z1_), z1_)]; pq(pin, f if s < 0 else f[::-1], Z.black, M)
            if z0_ == 0: f = [(s * b0, hy(b0), 0), (s * o0, hy(o0), 0), (s * o0, fy_(0), 0), (s * t0, fy_(0), 0)]; pq(pod, f if s < 0 else f[::-1], Z.white, M)
    o = owz(OT); pq(pin, [(-o, fy_(OT), OT), (-o, hy(o) + .02, OT), (o, hy(o) + .02, OT), (o, fy_(OT), OT)], Z.black, M)
    for s in (-1, 1): P.hull_collider('col_pod%d%s' % (az, 'ab'[s > 0]), [tuple(M @ V(p)) for z in (.0, 4.6) for p in ((s * pw(z, 2), hy(pw(z, 2)), z), (s * pw(z, 3), fy_(z), z), (s * OW, fy_(z), z), (s * OW, hy(OW), z))])
    P.hull_collider('col_pod%dt' % az, [tuple(M @ V(p)) for s in (-1, 1) for z in (4.66, 4.95, 6.85) for p in ((s * pw(z, 2), hy(pw(z, 2)), z), (s * pw(z, 3), fy_(z), z))])
P.mesh('legpods', pod, P.det, smooth_angle=25); P.mesh('legpods_in', pin, P.det, smooth_angle=40)
P.mesh('details', d, P.det, smooth_angle=40)
# ---------------- nodes and colliders
P.node('top', (0, 0, HL.Z_TOP), (0, 0, 1), 5); P.node('bottom', (0, 0, 0), (0, 0, -1), 5)
P.node('docking', (0, HL.R_DOCK, HL.Z_DOCK), (0, 1, 0), 2)
for i, az in enumerate(HL.LEG_AZ):
    p = on_cyl(az, HL.HINGE[1], HL.R); P.node(f'leg{i + 1}', p.translation, p.to_3x3() @ V((0, 0, 1)), 1); P.node(f'shroud{i + 1}', p.translation + p.to_3x3() @ V((0, 0, .0)), p.to_3x3() @ V((0, 0, 1)), 2)
def arcs(a0, a1, r0, r1, z0, z1, n):
    return [tuple(hp(a0 + (a1 - a0) * i / n, z, r=r)) for i in range(n + 1) for r in (r0, r1) for z in (z0, z1)]
for i, (a0, a1) in enumerate(((0, 90), (90, 180), (180, 270), (270, 360))):
    P.hull_collider(f'col_body{i}', [tuple(hp(a0 + (a1 - a0) * k / 8, z)) for k in range(9) for z in (ZP, HL.Z_SKIN)] + [(0, 0, ZP), (0, 0, HL.Z_SKIN)])
for k in range(16):
    a0, a1 = 22.5 * k, 22.5 * (k + 1); P.hull_collider(f'col_skirt{k}', arcs(a0, a1, HL.R, RI, 0, ZP, 2))
P.hull_collider('col_dome', [tuple(hp(a, z, r=r)) for a in range(0, 360, 30) for z, r in ((20.5, 2.6), (20.95, 1.6))])
P.box_trigger('ladder', climb_frame((0, -RR - .14, HL.Z_SKIN / 2 + .3), (0, -1, 0)), (.5, .3, HL.Z_SKIN - .3), 'Ladder')
finish(P)

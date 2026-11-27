"""HLS crew nose: cabins, the row of windows, airlock bay with its door, two roll-out solar arrays behind side hatches,
and an opening nose cap over a docking port for Orion. Origin at the joint's stack node."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
TALL = globals().get('TALL', False); P = start('STMS_HLS_CrewTall' if TALL else 'STMS_HLS_Crew'); MH = hull_mat(P, 'hls_crew'); MG = glass_mat(P); LM = lamp_mat(P)
O = HL.Z_TOP; dz = V((0, 0, O)); D0, D1 = HL.DOOR; S0, S1 = HL.SOL_Z; ZC = HL.Z_OGIVE + 7.40
zs = sorted({HL.Z_SKIN, D0, D1, S0, S1, HL.Z_OGIVE, *[HL.Z_OGIVE + z for z, _ in HL.OGIVE], *[HL.Z_OGIVE + z for z in (.42, 1.33, 2.2, 2.97, 3.75, 4.97, 6.0)]})
insol = lambda a: any(abs(wrap(a - s)) < HL.SOL_HW for s in HL.SOL_AZ)
def keep(a, z):
    if abs(wrap(a)) < HL.DOOR_AZ and D0 < z < D1: return False
    if S0 < z < S1 and insol(a): return False
    return True
hull = skin(zs, 'crew', O, keep); P.mesh('hull', hull, MH, smooth_angle=30)
d = Geo()
def put(pts, zone, g=None): quad([p - dz for p in pts], zone, g if g is not None else d)
# ---------------- the rails and ladder go on up to the door
ct = Geo()
TR, RR = HL.TRACK, HL.R
for s in (-1, 1):
    x = s * (HL.TRACK_R * math.sin(math.radians(TR)) - .035); H_ = D0 - HL.Z_SKIN - .06
    ct.add(box(.05, .09, H_, zone=Z.alu, bevel=.01, center=(x, -RR - .03, (D0 + HL.Z_SKIN) / 2 - O - .03)))
    ct.add(box(.02, .05, H_, zone=Z.steel, center=(x - s * .02, -RR - .075, (D0 + HL.Z_SKIN) / 2 - O - .03)))
    ct.add(box(.02, .07, H_, zone=Z.grey, center=(s * .16, -RR - .025, (D0 + HL.Z_SKIN) / 2 - O - .03)))
for z in np.arange(HL.Z_SKIN + .15, D0 - .08, .38): ct.add(tube([(-.16, -RR - .05, float(z) - O), (.16, -RR - .05, float(z) - O)], .012, 5, zone=Z.steel))
P.mesh('crewtrack', ct, P.det, smooth_angle=40)
# ---------------- airlock bay
XB = HL.R * math.sin(math.radians(HL.DOOR_AZ)); YB = HL.BAY_BACK; az_s = [i * 3.75 - HL.DOOR_AZ for i in range(11)]
for z, flip in ((D0, False), (D1, True)):
    arc = [hp(a, z) for a in az_s]
    for p, q in zip(arc, arc[1:]):
        f = [V((p.x, p.y, z)), V((q.x, q.y, z)), V((q.x, YB, z)), V((p.x, YB, z))]; put(f[::-1] if flip else f, Z.deck if not flip else Z.white)
for s in (-1, 1):
    e = hp(s * HL.DOOR_AZ, D0); p = [V((e.x, e.y, D0)), V((e.x, YB, D0)), V((e.x, YB, D1)), V((e.x, e.y, D1))]; put(p if s < 0 else p[::-1], Z.white)
    for z in (D0 + .35, D0 + .70): d.add(tube([(s * (XB - .07), -2.3, z - O), (s * (XB - .07), -1.5, z - O)], .018, 6, zone=Z.grey)); [d.add(box(.07, .03, .03, zone=Z.grey, center=(s * (XB - .035), y, z - O))) for y in (-2.25, -1.55)]
put([V((-XB, YB, D0)), V((XB, YB, D0)), V((XB, YB, D1)), V((-XB, YB, D1))], Z.white)
BF = Matrix(((1, 0, 0, 0), (0, 0, -1, YB), (0, 1, 0, (D0 + D1) / 2 - O), (0, 0, 0, 1)))      # +Z toward the door
d.add(rounded_rect_ring(.98, 1.28, .22, .09, .06, 6, zone=Z.alu), BF)
d.add(recolor(rounded_rect_ring(.82, 1.12, .18, .40, .05, 6), Z.hatch), BF); d.add(box(.1, .42, .05, zone=Z.hatch), BF)
d.add(tube([tuple(BF @ V((.22, -.2, .03))), tuple(BF @ V((.30, -.1, .10))), tuple(BF @ V((.22, 0, .03)))], .016, 6, zone=Z.steel))
d.add(rounded_rect_ring(.34, .26, .07, .04, .07, 5, zone=Z.dark), BF @ T(0, .28, 0))
wg = Geo()
def pane(w, h, rd_, cell):
    g = Geo(); pts = []
    for cx, cy, a0 in ((w / 2 - rd_, h / 2 - rd_, 0), (-w / 2 + rd_, h / 2 - rd_, 90), (-w / 2 + rd_, -h / 2 + rd_, 180), (w / 2 - rd_, -h / 2 + rd_, 270)):
        pts += [(cx + rd_ * math.cos(math.radians(a0 + 90 * k / 4)), cy + rd_ * math.sin(math.radians(a0 + 90 * k / 4))) for k in range(5)]
    m = len(pts); g.v = [(0, 0, 0)] + [(x / 2, y / 2, 0) for x, y in pts] + [(x, y, 0) for x, y in pts]
    uv = lambda x, y: ((cell % 4 + .5 + x / w * .9) / 8 + .5, (cell // 4 + .5 + y / h * .9) / 4 + .5)
    for i in range(m):
        j = (i + 1) % m; A, B = pts[i], pts[j]
        g.face([0, 1 + i, 1 + j], [uv(0, 0), uv(A[0] / 2, A[1] / 2), uv(B[0] / 2, B[1] / 2)])
        g.face([1 + i, 1 + m + i, 1 + m + j, 1 + j], [uv(A[0] / 2, A[1] / 2), uv(*A), uv(*B), uv(B[0] / 2, B[1] / 2)])
    return g
wg.add(pane(.27, .19, .05, 2), BF @ T(0, .28, .055))
for s in (-1, 1): d.add(box(.05, .06, 1.1, zone=Z.black, bevel=.015, center=(s * .62, YB - .025, (D0 + D1) / 2 - O)))
lamp = Geo(); lamp.add(box(.9, .10, .03, zone=Z.lamp, center=(0, -1.7, D1 - O - .012))); d.add(box(1.0, .16, .02, zone=Z.alu, center=(0, -1.7, D1 - O - .006)))
add_spot(P, 'doorLight', (0, -1.75, D1 - O - .04), (0, -.25, -1), power=170, angle=120, reach=6)
# frame round the door opening
for s in (-1, 1): d.add(lay(box(.05, D1 - D0 + .1, .016, zone=Z.alu, bevel=.005), s * (HL.DOOR_AZ + .5), (D0 + D1) / 2, O, sink=.004))
for z in (D0 - .025, D1 + .025):
    d.add(lay(box(XB * 2.08, .05, .016, zone=Z.alu, bevel=.005), 0, z, O, sink=.004)) if z > D0 else d.add(lay(box(XB * 2.08, .05, .016, zone=Z.alu, bevel=.005), 0, z - .012, O, sink=.004))
# ---------------- door: an awning hinged on its top edge
HY = -HL.R - .02; HZ = D1 - .015; hf = T(0, HY, HZ - O)
door = Geo(); ids = {}; dd = Geo(); az_d = [a for a in az_s]
rowsz = (D0 + .006, (D0 + D1) / 2, D1 - .006)
def dv(a, z, r): return hp(max(-HL.DOOR_AZ + .12, min(HL.DOOR_AZ - .12, a)), z, r=r) - dz
g0 = Geo()
for j in range(2):
    for i in range(10):
        q = [(az_d[i], rowsz[j]), (az_d[i + 1], rowsz[j]), (az_d[i + 1], rowsz[j + 1]), (az_d[i], rowsz[j + 1])]
        n = len(g0.v); g0.v += [tuple(dv(a, z, HL.R)) for a, z in q]; g0.face(range(n, n + 4), [huv(abs(a), z, 'crew') for a, z in q])
        n = len(dd.v); dd.v += [tuple(dv(a, z, HL.R - .07)) for a, z in q][::-1]; dd.face(range(n, n + 4), [Z.grey.uv((i + t) / 10, (j + u) / 2) for t, u in ((0, 1), (1, 1), (1, 0), (0, 0))])
edge = [(a, rowsz[0]) for a in az_d] + [(az_d[-1], rowsz[2])] + [(a, rowsz[2]) for a in az_d[::-1]] + [(az_d[0], rowsz[0])]
for A, B in zip(edge, edge[1:]):
    n = len(dd.v); dd.v += [tuple(dv(*A, HL.R - .07)), tuple(dv(*B, HL.R - .07)), tuple(dv(*B, HL.R)), tuple(dv(*A, HL.R))]; dd.face(range(n, n + 4), [Z.white.uv(*t) for t in ((0, 0), (.1, 0), (.1, .05), (0, .05))])
for x in (-.6, 0, .6): dd.add(box(.07, .05, 1.3, zone=Z.alu, bevel=.01, center=(x, -2.722 + abs(x) * .06, (D0 + D1) / 2 - O)))
dpiv = P.empty('door', hf, P.model)
P.mesh('doorskin', g0, MH, parent=dpiv, frame=hf, smooth_angle=30); P.mesh('doorframe', dd, P.det, parent=dpiv, frame=hf)
fl = Geo(); fx, fy, fw, fh = L.FLAG; FZ = Zone(fx, fy, fw, fh, atlas=2048)
fl.add(lay(quad_patch(.62, .33, FZ, nx=6, ny=2), 0, 22.72, O, sink=-.006)); P.mesh('flag', fl, P.det, parent=dpiv, frame=hf)
q0 = P.rest_quat(dpiv); NA = 60
for f, a in ((0, 0), (NA, -108)): P.key('doorOpen', dpiv, f, rotation_quaternion=q0 @ Quaternion((1, 0, 0), math.radians(a)))
P.hull_collider('col_door', [tuple(dv(a, z, r)) for a in (-18.75, -9, 0, 9, 18.75) for z in (D0 + .01, D1 - .01) for r in (HL.R, HL.R - .06)], parent=dpiv, frame=hf)
# hinges: pads on the hull over the opening, lugs out to the pin, straps down the door; two struts from the bay's walls hold it up
for x in (-.55, 0, .55):
    yh = -math.sqrt(HL.R ** 2 - x * x); z0 = HZ - O
    d.add(box(.22, .05, .12, zone=Z.alu, bevel=.012), T(x, yh - .012, z0 + .125)); [d.add(box(.026, abs(HY - yh) + .07, .15, zone=Z.alu, bevel=.008), T(x + q, (HY + yh) / 2 + .005, z0 + .075)) for q in (-.075, .075)]
    for q in (-.075, .075): d.add(cyl(.036, .032, 18, zone=Z.grey, bevel=.006), T(x + q, HY, z0) @ Ry(90)); [d.add(cyl(.012, .02, 8, zone=Z.steel), T(x + q, yh - .04, z0 + .15) @ Rx(90))]
    d.add(cyl(.018, .21, 12, zone=Z.steel), T(x, HY, z0) @ Ry(90))
    hd = Geo(); hd.add(cyl(.034, .10, 18, zone=Z.white, bevel=.006), T(x, HY, z0) @ Ry(90)); hd.add(box(.09, abs(HY - yh) + .05, .06, zone=Z.white, bevel=.008), T(x, (HY + yh) / 2 + .005, z0 - .035)); hd.add(box(.10, .022, .34, zone=Z.white, bevel=.008), T(x, yh - .006, z0 - .20))
    for zz in (-.12, -.30): hd.add(cyl(.013, .012, 8, zone=Z.steel), T(x, yh - .02, z0 + zz) @ Rx(90))
    P.mesh('doorhinge', hd, P.det, parent=dpiv, frame=hf)
PV = V((0, HY, HZ - O))
for s in (-1, 1):
    X = s * .815; A = V((X, -1.31, HZ - O - .64)); B0 = V((X, -2.50, HZ - O - .55)); L0 = (B0 - A).length; e = (B0 - A).normalized()
    d.add(box(.10, .12, .12, zone=Z.grey, bevel=.015), T(s * (XB - .045), A.y, A.z)); d.add(cyl(.03, .05, 14, zone=Z.steel), T(X, A.y, A.z) @ Ry(90))
    db_ = Geo(); db_.add(box(.05, .17, .07, zone=Z.white, bevel=.01), T(X, B0.y - .085, B0.z)); db_.add(cyl(.026, .05, 14, zone=Z.steel), T(X, B0.y, B0.z) @ Ry(90)); P.mesh('doorlug', db_, P.det, parent=dpiv, frame=hf)
    n_ = 'LR'[s > 0]; fa, fb = T(*A), T(*B0); cy, ro = P.empty('strutCyl' + n_, fa, P.model), P.empty('strutRod' + n_, fb, P.model)
    P.mesh('strutcyl', strut(A, A + e * (L0 - .04), .026, Z.dark, 12), P.det, parent=cy, frame=fa); P.mesh('strutrod', strut(B0, B0 - e * (L0 - .04), .014, Z.steel, 10), P.det, parent=ro, frame=fb)
    qa, qb, lb = P.rest_quat(cy), P.rest_quat(ro), ro.location.copy()
    for f in range(0, NA + 1, 4):
        B = PV + Quaternion((1, 0, 0), math.radians(-108 * f / NA)) @ (B0 - PV); B.x = X; v_ = B - A; th = math.atan2(v_.z, v_.y) - math.atan2(e.z, e.y); R_ = Quaternion((1, 0, 0), th)
        P.key('doorOpen', cy, f, rotation_quaternion=qa @ R_); P.key('doorOpen', ro, f, location=lb + (B - B0), rotation_quaternion=qb @ R_)
    print('STRUT shut %.2f open %.2f' % (L0, (B - A).length))
# ---------------- windows
wf = Geo(); WW, WHt = HL.WIN
for i in range(HL.WIN_N):
    az = -HL.WIN_SPAN + 2 * HL.WIN_SPAN * i / (HL.WIN_N - 1); fr_w, fr_h = WW + .07, WHt + .07
    wf.add(lay(rounded_rect_ring(fr_w, fr_h, .105, .045, .024, 5, zone=Z.black), az, HL.WIN_Z, O))
    wf.add(lay(box(WW + .01, .03, .016, zone=Z.black), az, HL.WIN_Z - .05, O))
    wg.add(lay(pane(WW, WHt, .075, (i * 3 + 1) % 8), az, HL.WIN_Z, O, .08, -.004))
for rz, rn, rs_, rw, rh in HL.ROWS_TALL if TALL else ():
    for i in range(rn):
        az = -rs_ + 2 * rs_ * i / (rn - 1); wf.add(lay(rounded_rect_ring(rw + .05, rh + .05, min(rw, rh) * .34, .034, .018, 4, zone=Z.black), az, rz, O)); wg.add(lay(pane(rw, rh, min(rw, rh) * .28, (i * 5 + int(rz * 7)) % 8), az, rz, O, .06, -.004))
d.add(wf)
P.mesh('windows', wg, MG, smooth_angle=60)
# hull cameras for RasterPropMonitor's camera pages (its/patches/STMS_Cameras.cfg), numbered as on SEP's ship (its/scripts/make_cameras_cfg.py):
# 5 airlock and elevator (above the door, looking down the hull), 6 horizon (the far side), 7 hull looking aft, 8 nose looking forward
hr = lambda z: float(np.interp(z, [HL.Z_OGIVE + z_ for z_, _ in HL.OGIVE], [r for _, r in HL.OGIVE])) if z > HL.Z_OGIVE else HL.R
cm = Geo()
for cid, az, z, look in ((5, 0, 24.3, 'down'), (6, 140, 24.6, 'out'), (7, 90, 21.0, 'down'), (8, 60, 26.6, 'up')):
    a_ = math.radians(az); n = V((math.sin(a_), -math.cos(a_), -(hr(z + .05) - hr(z - .05)) / .1)).normalized(); upz = V((0, 0, 1)); tg = (upz - upz.dot(n) * n).normalized()
    y_, z_ = {'down': (-tg, n), 'up': (tg, n), 'out': (n, tg)}[look]; base = V((hr(z) * math.sin(a_), -hr(z) * math.cos(a_), z - O))
    Fc = Matrix((y_.cross(z_), y_, z_)).transposed().to_4x4(); Fc.translation = base + (n * .07 if look == 'out' else n * .035 + y_ * .085); P.empty(f'stms_cam{cid}', Fc, P.model)      # at the housing's front face
    Fh = Matrix((tg.cross(n), tg, n)).transposed().to_4x4(); Fh.translation = base - n * .01; cm.add(box(.10, .14, .08, zone=Z.dark, bevel=.012, center=(0, 0, .04)), Fh); cm.add(cyl(.028, .03, 12, zone=Z.black), Fc @ Rx(90))
P.mesh('stms_campods', cm, P.det, smooth_angle=40)
# ---------------- solar bays: four pockets with a node each; the array part brings its own hatch
for k, az0 in enumerate(HL.SOL_AZ):
    F = on_cyl(az0, (S0 + S1) / 2 - O, 0); HWx = HL.R * math.sin(math.radians(HL.SOL_HW)); Hh = (S1 - S0) / 2; DP = HL.SOL_DP; HWb = DP * math.sin(math.radians(HL.SOL_HW))   # local +Z out, +Y up
    loc = lambda x, y, r: F @ V((x, y, r))
    aa = [az0 - HL.SOL_HW + 3.75 * i for i in range(11)]
    for z, flip in ((S0, False), (S1, True)):
        ar = [hp(a, z) for a in aa]
        for i, (p, q) in enumerate(zip(ar, ar[1:])):
            b0 = loc(-HWb + 2 * HWb * i / 10, 0, DP); b1 = loc(-HWb + 2 * HWb * (i + 1) / 10, 0, DP); b0.z = b1.z = z - O
            f = [p - dz, q - dz, b1, b0]; quad(f[::-1] if flip else f, Z.wall, d)
    for s in (-1, 1):
        e = [hp(az0 + s * HL.SOL_HW, z) - dz for z in (S0, S1)]; b = [loc(s * HWb, -Hh, DP), loc(s * HWb, Hh, DP)]
        f = [e[0], b[0], b[1], e[1]]; quad(f if s < 0 else f[::-1], Z.wall, d)
    quad([loc(-HWb, -Hh, DP), loc(HWb, -Hh, DP), loc(HWb, Hh, DP), loc(-HWb, Hh, DP)], Z.wall, d)
    P.node(f'solar{k + 1}', F @ V((0, 0, HL.R)), F.to_3x3() @ V((0, 0, 1)), 1)
# ---------------- nose cap, docking port
g = Geo(); CR = [(HL.Z_OGIVE + z, r) for z, r in HL.CAP]
g = skin([z for z, _ in CR if z < HL.Z_OGIVE + 8.56], 'crew', O)
n = len(g.v); z_l = HL.Z_OGIVE + 8.555; g.v.append((0, 0, HL.Z_OGIVE + 8.565 - O)); ids = [i for i, p in enumerate(g.v[:n]) if abs(p[2] + O - z_l) < 1e-4]
ids.sort(key=lambda i: math.atan2(g.v[i][0], -g.v[i][1]))
for a, b in zip(ids, ids[1:] + ids[:1]): g.face([a, b, n], [(.5, .99)] * 3)
R0 = HL.CAP[0][1]; HX = V((0, R0 + .06, ZC - O)); cf = T(*HX)
cap = P.empty('cap', cf, P.model); P.mesh('capskin', g, MH, parent=cap, frame=cf, smooth_angle=30)
ci = Geo(); ci.add(lathe([(R0 - .005, .003), (R0 - .06, .003), (R0 - .10, .06), (.72, .30), (.5, .62), (.2, .9), (0, .95)], 48, zone=Z.wall, flip=True), T(0, 0, ZC - O))
ci.add(box(.5, .08, .07, zone=Z.dark, bevel=.012), T(0, R0 - .10, ZC - O + .045))
# the hinge: a knuckle on the cap round the pin, with a strap from it up the cap's skin; on the hull, a clevis either side
hz = ZC - O; Rx_ = Matrix.Rotation(math.pi / 2, 4, 'Y')
ci.add(cyl(.045, .24, 16, zone=Z.steel, bevel=.006), T(*HX) @ Rx_); ci.add(box(.22, .08, .16, zone=Z.steel, bevel=.01), T(0, R0 + .0, hz + .07))
ci.add(box(.22, .16, .03, zone=Z.steel, bevel=.008), T(0, R0 - .03, hz + .03))
P.mesh('capin', ci, P.det, parent=cap, frame=cf)
qc = P.rest_quat(cap); NC = 90
for f, a in ((0, 0), (NC, -125)): P.key('noseCap', cap, f, rotation_quaternion=qc @ Quaternion((1, 0, 0), math.radians(a)))
zc = ZC - O
# flat seat for whatever docking port the user puts on the node; the shut cap covers it
d.add(lathe([(R0 - .002, zc), (R0 - .05, zc), (R0 - .055, zc - .03), (.40, zc - .03)], 64, zone=Z.grey)); d.add(lathe([(.40, zc - .03), (.385, zc - .022), (0, zc - .022)], 48, zone=Z.alu))
for sx in (-1, 1):                                  # the hinge's clevis plates and their foot on the ogive, and the pin through them
    d.add(box(.035, .10, .11, zone=Z.steel, bevel=.008), T(sx * .145, R0 + .06, zc - .015)); d.add(box(.07, .06, .10, zone=Z.steel, bevel=.01), T(sx * .145, R0 + .055, zc - .09))
d.add(cyl(.022, .36, 12, zone=Z.alu), T(0, R0 + .06, zc) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
d.add(bolts(24, .62, .016), T(0, 0, zc - .03)); d.add(bolts(16, .36, .010), T(0, 0, zc - .022)); d.add(box(.34, .10, .07, zone=Z.dark, bevel=.015), T(0, R0 - .10, zc - .005))
P.node('port', (0, 0, zc - .022), (0, 0, 1), 1)
# ---------------- bottom: dome, skirt inside
zb = HL.Z_SKIN - O
d.add(lathe([(2.765, zb), (2.765, .30), (2.36, .33)], 96, zone=Z.wall, flip=True)); d.add(lathe([(2.36, .33), (0, .36)], 96, zone=Z.wall, flip=True))
d.add(lathe([(HL.R - .004, zb), (2.765, zb)], 96, zone=Z.alu, flip=True))
# ---------------- lights, antennas, RCS
for s in (-1, 1):
    d.add(lay(box(.30, .12, .09, zone=Z.white, bevel=.02), s * 14, D1 + .20, O)); lamp.add(lay(box(.24, .02, .05, zone=Z.lamp), s * 14, D1 + .135, O, sink=-.035))
    add_spot(P, 'doorLight', hp(s * 14, D1 + .12, .12) - dz, (0, -.35, -1), power=260, angle=95, reach=26)
P.mesh('lampglow', lamp, LM)
for az in (95, 265): d.add(lay(cyl(.11, .03, 20, zone=Z.white, bevel=.008), az, 27.2, O)); d.add(lay(box(.34, .34, .02, zone=Z.white, bevel=.008), az, 26.2, O))
d.add(lay(cyl(.05, .05, 14, zone=Z.dark, bevel=.01), 0, 24.6 if TALL else 26.35, O)); d.add(lay(rounded_rect_ring(.2, .14, .04, .03, .03, 4, zone=Z.white), 0, 24.6 if TALL else 26.35, O))
spots = []
for az in (80, 100, 260, 280):
    z = 25.1; spots += [(az, z, (1, 0, .35)), (az, z + .28, (-1, 0, .35)), (az, z + .56, (0, 1, .35)), (az, z - .28, (0, -1, .35))]
rcs(P, d, spots, O)
P.mesh('details', d, P.det, smooth_angle=40)
# ---------------- nodes, colliders, triggers
P.node('bottom', (0, 0, 0), (0, 0, -1), 5); P.node('lift', (0, -HL.TRACK_R, D0 - O), (0, -1, 0), 1); P.node('floor', (0, YB - .5, D0 - O), (0, 0, 1), 0)
def ringpts(z, a0, a1, n, r=None): return [tuple(hp(a0 + (a1 - a0) * i / n, z, r=r) - dz) for i in range(n + 1)]
for i, (a0, a1) in enumerate(((18.75, 99.4), (99.4, 180), (180, 260.6), (260.6, 341.25))):
    lo, hi = HL.Z_SKIN, HL.Z_OGIVE
    for j in range(2):
        b0, b1 = a0 + (a1 - a0) * j / 2, a0 + (a1 - a0) * (j + 1) / 2; P.hull_collider(f'col_w{i}{j}', [p for z in (lo, hi) for r in (2.1, HL.R) for p in ringpts(z, b0, b1, 4, r)])
for k in range(4): P.hull_collider(f'col_track{k}', [p for z in (HL.Z_SKIN, D0) for r in (2.1, HL.R) for p in ringpts(z, -18.75 + 9.375 * k, -9.375 + 9.375 * k, 3, r)])
P.hull_collider('col_floor', [(x, y, z) for x in (-XB, XB) for y in (-2.66, YB) for z in (D0 - O, D0 - O - .4)])
P.hull_collider('col_back', [(x, y, z) for x in (-XB, XB) for y in (YB, YB + .1) for z in (D0 - O, D1 - O)])
P.hull_collider('col_over', [p for z in (D1, HL.Z_OGIVE) for r in (2.1, HL.R) for p in ringpts(z, -18.75, 18.75, 6, r)])
P.hull_collider('col_base', [p for z in (zb + O + .55, O + .36) for p in ringpts(z, 0, 345, 23, 2.4)])
for i, (za, zb_) in enumerate(((0, 1.82), (1.82, 3.36), (3.36, 4.64), (4.64, 5.81), (5.81, 7.40))):
    P.hull_collider(f'col_n{i}', [p for z in (HL.Z_OGIVE + za, HL.Z_OGIVE + zb_) for p in ringpts(z, 0, 345, 23)])
P.hull_collider('col_seat', [(.9 * math.cos(t * math.pi / 8), .9 * math.sin(t * math.pi / 8), z) for z in (zc - .2, zc - .03) for t in range(16)])
P.hull_collider('col_cap', [tuple(hp(a, HL.Z_OGIVE + z) - dz) for z in (7.41, 7.93, 8.38) for a in range(0, 360, 30)] + [(0, 0, HL.Z_OGIVE + 8.56 - O)], parent=cap, frame=cf)
AZ_ = D0 - O + .55; print('AIRLOCK z', D0 - O, D1 - O, 'YB', YB, 'RR', RR)
P.box_trigger('airlock', climb_frame((0, -2.5, AZ_), (0, -1, 0)), (.8, .5, .9), 'Airlock')      # KSP's obstruction ray starts .5 m behind this and runs from the part's origin, our own colliders included: check_airlocks.py
P.box_trigger('ladder', climb_frame((0, -RR - .14, (HL.Z_SKIN + D0) / 2 - O + .1), (0, -1, 0)), (.5, .3, D0 - HL.Z_SKIN + .2), 'Ladder')
P.bake_clips(0)
finish(P)

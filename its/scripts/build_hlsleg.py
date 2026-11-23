"""HLS landing leg: a telescoping strut folded against its black panel, two side struts from the skirt, an octagonal pad.
Stock wheel-module layout as in ITS_Leg. Authored deployed; frame 0 of legDeploy is stowed. Origin on the hull, -Y outboard."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Leg'); N = 120; F_SWING, F_SLIDE, F_DONE = 70, 25, 100; XA = V((1, 0, 0))
H0 = V((0, -(HL.HINGE[0] - HL.R) - .20, 0)); OZ = HL.HINGE[1]     # hinge pin, proud of the hull
SUSP, RAD = .32, .30; AN = V((0, -(HL.FOOT_R - HL.R), HL.SOLE - OZ + RAD + SUSP))   # ankle at rest
U = (AN - H0).normalized(); SLEN = (AN - H0).length; TILT = math.atan2(-U.y, -U.z)
PAD_Z = HL.FOOT_STOW + .47 - OZ; LSTOW = H0.z - PAD_Z        # stowed ankle height: strut hangs straight down the hull
NST = 2; IN = .40; OUT_L = LSTOW - .35; STEP = (SLEN - LSTOW) / NST
R1, RS = .19, (.155, .125); SW = TILT
print(f'strut {SLEN:.2f} stowed {LSTOW:.2f} step {STEP:.2f} tilt {math.degrees(TILT):.1f}')
leg = P.empty('leg', None, P.model)
b = Geo()
for s in (-1, 1):
    b.add(box(.08, .30, .50, zone=Z.black, bevel=.02), T(s * .27, -.12, 0)); b.add(cyl(.11, .05, 16, zone=Z.steel, bevel=.01), T(s * .325, H0.y, 0) @ Ry(90))
b.add(tube([(-.33, H0.y, 0), (.33, H0.y, 0)], .06, 12, zone=Z.steel)); b.add(box(.5, .06, .62, zone=Z.dark, bevel=.015), T(0, -.02, 0))
# side strut pivots on the skirt
D = [V((s * 1.08, 0, .62 - OZ)) for s in (-1, 1)]
for s, p in zip((-1, 1), D):
    az = math.degrees(math.asin(p.x / HL.R)); q = on_cyl(az, p.z, HL.R); q.translation += V((0, HL.R, 0)); p.y = (q @ V((0, 0, .11))).y; p.x = (q @ V((0, 0, .11))).x
    b.add(box(.34, .26, .08, zone=Z.black, bevel=.02), q @ T(0, 0, .02)); b.add(cyl(.10, .22, 14, zone=Z.dark, bevel=.015), T(*p))
P.mesh('bracket', b, P.det, parent=leg)
wc = P.empty('wheelCollider', T(*AN), leg); wc.muproperties.layer = 27
at = lambda d_: H0 + U * d_
g = Geo(); g.add(tube([at(.05), at(OUT_L)], R1, 20, zone=Z.dark))
for q, w, r in ((.25, .10, .025), (1.3, .05, .012), (2.4, .05, .012), (OUT_L - .12, .13, .03)): g.add(tube([at(q), at(q + w)], R1 + r, 20, zone=Z.black))
g.add(cyl(.16, .44, 18, zone=Z.black, bevel=.02), T(*H0) @ Ry(90)); g.add(tube([at(.6) + V((0, -.2, .03)), at(2.6) + V((0, -.2, .03))], .03, 6, zone=Z.grey))
[g.add(box(.08, .10, .08, zone=Z.grey), T(*(at(x) + V((0, -.18, .02))))) for x in (.65, 1.6, 2.55)]
pf = T(*H0); pb = P.mesh('pistonbase', g, P.det, parent=leg, frame=pf); qr = P.rest_quat(pb)
UNSW = Quaternion((1, 0, 0), SW)
if (UNSW @ U - V((0, 0, -1))).length > .01: UNSW = Quaternion((1, 0, 0), -SW)
assert (UNSW @ U - V((0, 0, -1))).length < .01
for f, t in ((0, 0), (F_SWING, 1), (N, 1)): P.key('legDeploy', pb, f, rotation_quaternion=UNSW if t == 0 else Quaternion())
parent = pb; prev = OUT_L
for k, r in enumerate(RS):
    s0 = at(STEP * (k + 1)); end = OUT_L + STEP * (k + 1); g = Geo(); g.add(tube([at(end - STEP - .35), at(end + (0 if k < NST - 1 else .35))], r, 18, zone=Z.grey if k else Z.alu)); g.add(tube([at(end - .11), at(end + .02)], r + .03, 18, zone=Z.black))
    if k == NST - 1: g.add(cyl(.17, .30, 16, zone=Z.black, bevel=.02), T(*AN) @ Ry(90))
    o = P.mesh(f'strut{k + 2}', g, P.det, parent=parent, frame=T(*s0)); rest = o.location.copy(); st = rest - U * STEP
    for f, l in ((0, st), (F_SLIDE, st), (F_DONE, rest), (N, rest)): P.key('legDeploy', o, f, location=l)
    parent = o
last = parent
P.empty('deployTgt', T(*AN), pb)
g = Geo(); g.add(tube([AN + V((0, 0, .04)), AN + V((0, 0, -SUSP))], .085, 12, zone=Z.alu)); pi = P.mesh('piston', g, P.det, parent=pb, frame=T(*AN)); l1 = pi.location.copy(); l0 = l1 - U * (STEP * NST)
for f, l, q in ((0, l0, UNSW.inverted()), (F_SLIDE, l0, UNSW.inverted()), (F_DONE, l1, Quaternion()), (N, l1, Quaternion())): P.key('legDeploy', pi, f, location=l, rotation_quaternion=Quaternion())
FC = AN + V((0, 0, -SUSP)); ft = T(*FC); s_ = Geo()
OCT = lambda r: [(r * math.cos(math.radians(22.5 + 45 * i)), r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
rows = [(.36, -RAD), (.50, -RAD + .03), (.56, -RAD + .11), (.54, -RAD + .14), (.24, -RAD + .22), (.16, -.02)]
for r, z in rows: s_.v += [(x, y, z) for x, y in OCT(r)]
for j in range(len(rows) - 1):
    for i in range(8):
        i2 = (i + 1) % 8; s_.face([j * 8 + i, j * 8 + i2, (j + 1) * 8 + i2, (j + 1) * 8 + i], [Z.black.uv(i / 8, j / 5), Z.black.uv((i + 1) / 8, j / 5), Z.black.uv((i + 1) / 8, (j + 1) / 5), Z.black.uv(i / 8, (j + 1) / 5)])
for j, rev in ((0, True), (len(rows) - 1, False)):
    c = len(s_.v); s_.v.append((0, 0, rows[j][1]))
    for i in range(8): t = [c, j * 8 + i, j * 8 + (i + 1) % 8]; s_.face(t[::-1] if rev else t, [Z.rubber.uv(.5, .5), Z.rubber.uv(.2, .3), Z.rubber.uv(.3, .2)])
for i in range(8): s_.add(box(.03, .34, .10, zone=Z.dark, bevel=.008), Rz(45 * i) @ T(0, -.34, -RAD + .17) @ Rx(-18))
s_.add(cyl(.12, .28, 14, zone=Z.steel, bevel=.015), Ry(90))
shoe = Geo(); shoe.add(s_, ft); fo = P.mesh('foot', shoe, P.det, parent=pi, frame=ft, smooth_angle=30); fl = fo.location.copy()
QF = Quaternion((1, 0, 0), math.radians(90 - math.degrees(0)))    # stowed: pad flat against the hull, sole outboard
tst = QF @ V((0, 0, -1))
if tst.y > 0: QF = Quaternion((1, 0, 0), math.radians(-90))
# parent (piston) sits in the swung frame, so the stowed foot also undoes that swing: it must end up vertical
for f, l, q in ((0, V((0, 0, 0)), 0), (F_SLIDE, V((0, 0, 0)), 0), (F_DONE, fl, 1), (N, fl, 1)):
    P.key('legDeploy', fo, f, location=UNSW.inverted() @ V((0, .02, 0)) if q == 0 else l, rotation_quaternion=(UNSW.inverted() @ QF) if q == 0 else Quaternion())
# side struts: two nested tubes aimed frame by frame
CD = SLEN - HL.COLLAR                                      # deployed collar distance from hinge, on the last stage
cl = Geo(); cl.add(tube([at(CD - .08), at(CD + .08)], RS[-1] + .05, 16, zone=Z.black)); [cl.add(cyl(.07, .12, 12, zone=Z.dark, bevel=.01), T(*(at(CD) + XA * s * .2)) @ Ry(90)) for s in (-1, 1)]
P.mesh('collar', cl, P.det, parent=last, frame=T(*at(CD)))
FR = sorted({0, 8, 16, 25, 34, 42, 50, 58, 66, 74, 82, 90, F_DONE, N}); sc = bpy.context.scene
P.bake_clips(0)                                            # so the collar's path can be read off the posed model
pos = {}
for f in FR:
    sc.frame_set(f); bpy.context.view_layer.update(); pos[f] = bpy.data.objects['collar'].matrix_world.translation.copy()
sc.frame_set(0); P.clips = {}
for k, s in enumerate((-1, 1)):
    tip = {f: pos[f] + XA * s * .2 for f in FR}; ln = {f: (tip[f] - D[k]).length for f in FR}; BL = min(ln.values()) - .12; mx = max(ln.values())
    assert mx < 2 * BL + .6, (mx, BL)
    dd_ = (tip[N] - D[k]).normalized(); fA = frame_axes(D[k], dd_, x=V((0, 0, 1))); fB = frame_axes(tip[N], -dd_, x=V((0, 0, 1)))
    ga, gb = Geo(), Geo(); ga.add(tube([(0, 0, .02), (0, 0, BL)], .085, 14, zone=Z.black)); ga.add(tube([(0, 0, BL - .08), (0, 0, BL + .01)], .10, 14, zone=Z.dark)); gb.add(tube([(0, 0, .02), (0, 0, mx - BL + .2)], .062, 12, zone=Z.grey)); gb.add(cyl(.075, .12, 12, zone=Z.dark, bevel=.01), Ry(90))
    oa = P.mesh(f'drag{k}', Geo().add(ga, fA), P.det, parent=leg, frame=fA); ob = P.mesh(f'rod{k}', Geo().add(gb, fB), P.det, parent=leg, frame=fB)
    for f in FR:
        u = (tip[f] - D[k]).normalized()
        P.key('legDeploy', oa, f, rotation_quaternion=frame_axes((0, 0, 0), u, x=V((0, 0, 1))).to_quaternion(), location=D[k]); P.key('legDeploy', ob, f, rotation_quaternion=frame_axes((0, 0, 0), -u, x=V((0, 0, 1))).to_quaternion(), location=tip[f])
    print('drag', k, '%.2f..%.2f' % (min(ln.values()), mx))
def cap(name, a, c, r, parent):
    o = P.empty(name, frame_axes((a + c) / 2, (a - c).normalized()), parent); m = o.muproperties; m.collider = 'MU_COL_CAPSULE'; m.isTrigger = False; m.radius = r; m.height = (a - c).length; m.direction = 'MU_Z'; m.center = (0, 0, 0); m.layer = 26
cap('pistonbaseCollider', at(.1), at(OUT_L), R1, pb); cap('col_strut', at(SLEN - 1.2), at(SLEN - .1), .13, last)
o = P.empty('piston_collider', T(*AN), pi); m = o.muproperties; m.collider = 'MU_COL_CAPSULE'; m.isTrigger = False; m.radius = .12; m.height = SUSP + .3; m.direction = 'MU_Z'; m.center = (0, 0, -SUSP / 2); m.layer = 26
P.hull_collider('col_bracket', [(x, y, z) for x in (-.3, .3) for y in (0, -.26) for z in (-.25, .25)], parent=leg)
P.node('mount', (0, 0, 0), (0, 1, 0), 1)
P.bake_clips(0); finish(P)

"""HLS roll-out solar array: a flush hatch over a shallow bay, and eight thin panels folded flat in it on a carriage. One part per bay,
so each has its own animation (two panel modules on one part share an Animation and stop each other). Origin on the hull at the
bay's middle, -Y outboard, +Z up. Authored deployed (the array straight out from the hull, the panels nested); frame 0 is stowed.
Deploy: the hatch swings up, the carriage runs out SOL_OUT, the array folds out about its hinge at the bay's foot, then telescopes.
The hinge is also the tilt axis: the plugin (its/plugin) turns `tilt` about its X to hang the array down the hull."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Solar'); MH = hull_mat(P, 'hls_crew'); MS = P.material('its_solar', spec=(.25, .25, .28), shininess=.6)
R, DP = HL.R, HL.SOL_DP; Hh = (HL.SOL_Z[1] - HL.SOL_Z[0]) / 2; ZM = sum(HL.SOL_Z) / 2; OFF = V((0, R, -ZM))
F = on_cyl(0, 0, 0); F.translation = V((0, R, 0)); HW = HL.SOL_HW; END = 240; CL = 'solarDeploy'
T_HATCH, T_SLIDE, T_FOLD = 50, 80, 130      # frames: hatch open, carriage out, array folded out; then it telescopes to END
RH = HL.SOL_PIVR - HL.SOL_OUT; YH = HL.SOL_PIVY      # the hinge, stowed: radius, height
pt = lambda a, z, r=R: hp(a, z, r=r) + OFF
# ---------------- fixed: rails on the bay's floor from the back wall to the sill, catches under its top edge
b = Geo()
for s in (-1, 1):
    b.add(box(.05, .05, R - .07 - DP, zone=Z.alu, bevel=.008), F @ T(s * .38, -Hh + .03, (DP + R - .07) / 2))
    b.add(box(.10, .08, .08, zone=Z.dark, bevel=.012), F @ T(s * .52, Hh - .04, R - .17))
b.add(box(.86, .40, .02, zone=Z.grey, bevel=.006), F @ T(0, .05, DP + .01))
P.mesh('rails', b, P.det)
# ---------------- hatch on its upper edge
hs, hm = Geo(), Geo(); rz = (HL.SOL_Z[0] + .012, HL.SOL_Z[1] - .012); ha = [-HW + .25 + (2 * HW - .5) * i / 10 for i in range(11)]
for i in range(10):
    q = [(ha[i], rz[0]), (ha[i + 1], rz[0]), (ha[i + 1], rz[1]), (ha[i], rz[1])]; n = len(hs.v)
    hs.v += [tuple(pt(a, z)) for a, z in q]; hs.face(range(n, n + 4), [huv(60 + abs(a) * .2, z - 1.6, 'crew') for a, z in q])
    n = len(hm.v); hm.v += [tuple(pt(a, z, R - .04)) for a, z in q][::-1]; hm.face(range(n, n + 4), [Z.grey.uv(*u) for u in ((0, .1), (.1, .1), (.1, 0), (0, 0))])
ed = [(a, rz[0]) for a in ha] + [(a, rz[1]) for a in ha[::-1]] + [(ha[0], rz[0])]
for A, B in zip(ed, ed[1:]):
    n = len(hm.v); hm.v += [tuple(pt(*A, R - .04)), tuple(pt(*B, R - .04)), tuple(pt(*B)), tuple(pt(*A))]; hm.face(range(n, n + 4), [Z.white.uv(*u) for u in ((0, 0), (.1, 0), (.1, .05), (0, .05))])
for s in (-1, 1): hm.add(box(.08, .12, .03, zone=Z.alu, bevel=.008), F @ T(s * .52, Hh - .08, R - .055))
hf = F @ T(0, Hh - .01, R + .005); hatch = P.empty('hatch', hf, P.model); P.mesh('hatchskin', hs, MH, parent=hatch, frame=hf, smooth_angle=30); P.mesh('hatchin', hm, P.det, parent=hatch, frame=hf)
q0 = P.rest_quat(hatch)
for f, a in ((0, 0), (T_HATCH, -HL.SOL_HATCH), (END, -HL.SOL_HATCH)): P.key(CL, hatch, f, rotation_quaternion=q0 @ Quaternion((1, 0, 0), math.radians(a)))
# ---------------- carriage: a sled on each rail and the hinge brackets; it runs straight out
sf = F @ T(0, YH, RH); slide = P.empty('slide', sf, P.model); r0 = slide.location.copy(); uo = F.to_3x3() @ V((0, 0, 1))
for f, x in ((0, 0), (T_HATCH, 0), (T_SLIDE, HL.SOL_OUT), (END, HL.SOL_OUT)): P.key(CL, slide, f, location=r0 + uo * x)
c = Geo()
for s in (-1, 1):
    c.add(box(.10, .035, .16, zone=Z.dark, bevel=.008), F @ T(s * .38, -Hh + .072, DP + .10))
    c.add(box(.05, .035, RH - .025 - DP - .03, zone=Z.steel, bevel=.006), F @ T(s * .38, YH - .03, (DP + .03 + RH - .025) / 2))
    c.add(box(.04, .05, .05, zone=Z.steel, bevel=.008), F @ T(s * .38, YH, RH))
c.add(box(.66, .03, .03, zone=Z.alu, bevel=.006), F @ T(0, YH - .03, DP + .10))
P.mesh('carriage', c, P.det, parent=slide, frame=sf)
# ---------------- fold (the deploy animation) and tilt (the plugin) on the hinge; the sun pivot turns the array about its length
fold = P.empty('fold', sf, slide); qf = P.rest_quat(fold)
for f, a in ((0, -90), (T_SLIDE, -90), (T_FOLD, 0), (END, 0)): P.key(CL, fold, f, rotation_quaternion=qf @ Quaternion((1, 0, 0), math.radians(a)))
tilt = P.empty('tilt', sf, fold); piv = P.empty('sunPivot', sf, tilt)
PW, PL, NP, PT = 1.20, .98, 8, .016; SK = PT * (NP - 1) + .016      # panels: width, length, count, pitch; the stack's thickness
P.empty('suncatcher', sf @ T(0, SK + .10, 2.0), piv)
hg = Geo(); hg.add(cyl(.02, 1.10, 12, zone=Z.steel), sf @ Matrix.Rotation(math.pi / 2, 4, 'Y')); P.mesh('hinge', hg, P.det, parent=tilt, frame=sf)     # the pin turns with the tilt, not the tracking
h = Geo(); h.add(box(PW + .04, SK, .028, zone=Z.white, bevel=.006), sf @ T(0, SK / 2 - .008, .06))
P.mesh('hub', h, P.det, parent=piv, frame=sf)
par, p0 = piv, sf @ T(0, 0, .075)
for i in range(NP):
    fr = p0 @ T(0, PT * i, 0); pn = Geo(); w = PW / 2; uv = lambda x, z: (.5 + x / PW * .96, .02 + .96 * (1 + (i % 3) + z / PL) / 4)
    C4 = ((-w, 0), (w, 0), (w, PL), (-w, PL)); pn.v += [(x, .006, z) for x, z in C4]; pn.face([3, 2, 1, 0], [uv(*C4[q]) for q in (3, 2, 1, 0)]); pn.v += [(x, -.002, z) for x, z in C4]; pn.face([4, 5, 6, 7], [(.90, .05)] * 4)
    def bar(sx, sy, sz, c_): n = len(pn.uv); pn.add(box(sx, sy, sz, center=c_)); pn.uv[n:] = [tuple([(.10, .05)] * len(u)) for u in pn.uv[n:]]
    for s in (-1, 1): bar(.03, .014, PL, (s * w, 0, PL / 2))
    for zz in (.012, PL - .012): bar(PW, .013, .024, (0, 0, zz))
    g = Geo(); g.add(pn, fr); o = P.mesh(f'panel{i}', g, MS, parent=par, frame=fr)
    if i:
        l0 = o.location.copy(); l1 = l0 + V((0, -PT, PL - .006))
        for f, l in ((0, l0), (T_FOLD, l0), (END, l1)): P.key(CL, o, f, location=l)
    par = o
P.hull_collider('col_base', [tuple(F @ V((x, y, r))) for x in (-.42, .42) for y in (-Hh + .02, 0) for r in (DP + .02, R - .1)])
P.node('mount', (0, 0, 0), (0, 1, 0), 1)
P.bake_clips(0); finish(P)

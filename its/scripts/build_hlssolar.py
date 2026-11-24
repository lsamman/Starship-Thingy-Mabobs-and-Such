"""HLS roll-out solar array: a flush hatch and a package on rails behind it. One part per bay, so each has its own
animation (two panel modules on one part share an Animation and stop each other). Origin on the hull at the bay's
middle, -Y outboard, +Z up. Authored with the panels nested; frame 0 is stowed."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Solar'); MH = P.material('hls_crew', spec=(1, 1, 1), shininess=.62); MS = P.material('its_solar', spec=(.9, .9, .95), shininess=.6)
R, DP = HL.R, HL.SOL_DP; Hh = (HL.SOL_Z[1] - HL.SOL_Z[0]) / 2; ZM = sum(HL.SOL_Z) / 2; OFF = V((0, R, -ZM))
F = on_cyl(0, 0, 0); F.translation = V((0, R, 0)); HW = HL.SOL_HW; END = 240; CL = 'solarDeploy'
pt = lambda a, z, r=R: hp(a, z, r=r) + OFF
# ---------------- fixed: rails from the back wall to the sill, so the package hangs on something
b = Geo()
for s in (-1, 1):
    b.add(box(.07, .07, R - DP - .12, zone=Z.alu, bevel=.01, center=(0, 0, 0)), F @ T(s * .50, -Hh + .075, (DP + R - .12) / 2)); [b.add(box(.12, .06, .10, zone=Z.grey, bevel=.01), F @ T(s * .50, -Hh + .03, r)) for r in (DP + .12, 2.0, R - .22)]
b.add(tube([F @ V((0, -Hh + .07, DP)), F @ V((0, -Hh + .07, R - .2))], .02, 8, zone=Z.steel)); b.add(box(1.2, .5, .03, zone=Z.grey, bevel=.01), F @ T(0, 0, DP + .02))
for s in (-1, 1): b.add(box(.10, .08, .12, zone=Z.dark, bevel=.015), F @ T(s * .62, -Hh + .03, R - .20))
P.mesh('rails', b, P.det)
# ---------------- hatch on its lower edge
hs, hm = Geo(), Geo(); rz = (HL.SOL_Z[0] + .012, HL.SOL_Z[1] - .012); ha = [-HW + .25 + (2 * HW - .5) * i / 10 for i in range(11)]
for i in range(10):
    q = [(ha[i], rz[0]), (ha[i + 1], rz[0]), (ha[i + 1], rz[1]), (ha[i], rz[1])]; n = len(hs.v)
    hs.v += [tuple(pt(a, z)) for a, z in q]; hs.face(range(n, n + 4), [huv(60 + abs(a) * .2, z - 1.6, 'crew') for a, z in q])
    n = len(hm.v); hm.v += [tuple(pt(a, z, R - .04)) for a, z in q][::-1]; hm.face(range(n, n + 4), [Z.grey.uv(*u) for u in ((0, .1), (.1, .1), (.1, 0), (0, 0))])
ed = [(a, rz[0]) for a in ha] + [(a, rz[1]) for a in ha[::-1]] + [(ha[0], rz[0])]
for A, B in zip(ed, ed[1:]):
    n = len(hm.v); hm.v += [tuple(pt(*A, R - .04)), tuple(pt(*B, R - .04)), tuple(pt(*B)), tuple(pt(*A))]; hm.face(range(n, n + 4), [Z.white.uv(*u) for u in ((0, 0), (.1, 0), (.1, .05), (0, .05))])
for s in (-1, 1): hm.add(box(.08, .30, .05, zone=Z.alu, bevel=.01), F @ T(s * .62, -Hh + .16, R - .20))
hf = F @ T(0, -Hh + .01, R + .005); hatch = P.empty('hatch', hf, P.model); P.mesh('hatchskin', hs, MH, parent=hatch, frame=hf, smooth_angle=30); P.mesh('hatchin', hm, P.det, parent=hatch, frame=hf)
q0 = P.rest_quat(hatch)
for f, a in ((0, 0), (50, 112), (END, 112)): P.key(CL, hatch, f, rotation_quaternion=q0 @ Quaternion((1, 0, 0), math.radians(a)))
# ---------------- carriage, pivot, nested panels in one block with the spreader bar
sf = F @ T(0, 0, DP + .06); slide = P.empty('slide', sf, P.model); r0 = slide.location.copy(); uo = F.to_3x3() @ V((0, 0, 1))
for f, x in ((0, 0), (50, 0), (90, 1.28), (END, 1.28)): P.key(CL, slide, f, location=r0 + uo * x)
c = Geo(); c.add(box(.46, .34, .24, zone=Z.white, bevel=.03), sf @ T(0, -.03, .12)); c.add(box(1.14, .09, .20, zone=Z.alu, bevel=.012), sf @ T(0, -.24, .12)); c.add(box(.30, .12, .16, zone=Z.dark, bevel=.015), sf @ T(0, -.20, .12))
for s in (-1, 1): c.add(box(.13, .12, .20, zone=Z.dark, bevel=.015), sf @ T(s * .50, -.305, .12))
P.mesh('carriage', c, P.det, parent=slide, frame=sf)
pf = sf @ T(0, 0, .24); piv = P.empty('sunPivot', pf, slide); P.empty('suncatcher', pf @ T(0, .12, 2.0), piv)
PW, PL, NP, PT = 1.42, .62, 9, .020; h = Geo(); h.add(cyl(.12, .07, 20, zone=Z.dark, bevel=.012, center_z=False), pf @ T(0, 0, -.005)); h.add(box(1.46, .24, .09, zone=Z.white, bevel=.015), pf @ T(0, -.06, .10)); P.mesh('hub', h, P.det, parent=piv, frame=pf)
par, p0 = piv, pf @ T(0, 0, .135)
for i in range(NP):
    fr = p0 @ T(0, .03 - PT * i, 0); pn = Geo(); w = PW / 2; uv = lambda x, z: (.5 + x / PW * .96, .02 + .96 * (1 + (i % 3) + z / PL) / 4)
    C4 = ((-w, 0), (w, 0), (w, PL), (-w, PL)); pn.v += [(x, .006, z) for x, z in C4]; pn.face([3, 2, 1, 0], [uv(*C4[q]) for q in (3, 2, 1, 0)]); pn.v += [(x, -.002, z) for x, z in C4]; pn.face([4, 5, 6, 7], [(.90, .05)] * 4)
    def bar(sx, sy, sz, c_): n = len(pn.uv); pn.add(box(sx, sy, sz, center=c_)); pn.uv[n:] = [tuple([(.10, .05)] * len(u)) for u in pn.uv[n:]]
    for s in (-1, 1): bar(.03, .016, PL, (s * w, 0, PL / 2))
    for zz in (.012, PL - .012): bar(PW, .015, .024, (0, 0, zz))
    g = Geo(); g.add(pn, fr); o = P.mesh(f'panel{i}', g, MS, parent=par, frame=fr)
    if i:
        l0 = o.location.copy(); l1 = l0 + V((0, PT, PL - .006))
        for f, l in ((0, l0), (90, l0), (END, l1)): P.key(CL, o, f, location=l)
    par = o
P.hull_collider('col_base', [tuple(F @ V((x, y, r))) for x in (-.55, .55) for y in (-Hh + .02, 0) for r in (DP + .02, R - .3)])
P.node('mount', (0, 0, 0), (0, 1, 0), 1)
P.bake_clips(0); finish(P)

"""Tanker kit, a second MODEL on a copy of SEP's Block 3 nosecone (its/patches/STMS_Variants.cfg): propellant transfer plate with two
couplings, vents and two conduits up the leeward steel. In the nose's frame: barrel z -3.42..0, then the ogive; leeward is azimuth 0."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_TankerKit'); ST = sep_mat(P, 'stms_steel', 'stms_steel_diff', 'stms_steel_nrm', 'stms_steelmask_diff'); R = HL.R
def rz(z):
    if z <= 0: return R
    for (a, ra), (b, rb) in zip(HL.OGIVE, HL.OGIVE[1:]):
        if z <= b: return ra + (rb - ra) * (z - a) / (b - a)
    return HL.OGIVE[-1][1]
pr = lambda az, z, o=0.0: V(((rz(z) + o) * math.sin(math.radians(az)), -(rz(z) + o) * math.cos(math.radians(az)), z))
def slab(g, az, w, zs, h0, uv, taper=.25):
    """A low box laid up the hull: half-angle w, through heights zs, h0 proud, sloped in at both ends and sides."""
    m = len(zs); pts = []; NC = max(1, round(w / 1.2))
    for i, z in enumerate(zs):
        h = 0.012 if i in (0, m - 1) else h0
        c = [az + w * (1 - taper) * (2 * j / NC - 1) for j in range(NC + 1)]; pts.append([pr(az - w, z, -.02)] + [pr(q, z, h) for q in c] + [pr(az + w, z, -.02)])
    for i in range(m - 1):
        for k in range(NC + 2):
            q = [pts[i][k], pts[i][k + 1], pts[i + 1][k + 1], pts[i + 1][k]]; n = len(g.v); g.v += [tuple(p) for p in q]; g.face([n, n + 1, n + 2, n + 3], [uv((k + a) * .1, zs[i + b] * .25) for a, b in ((0, 0), (1, 0), (1, 1), (0, 1))])
s_ = Geo(); suv = lambda u, v: (.3 + u * .1, .1 + v % 1)
for q in (-1, 1): slab(s_, q * 9.5, 1.5, [-3.30, -3.16, -2.0, -1.0, 0, .84, 1.82, 2.58, 2.95, 3.15], .075, suv)
slab(s_, 0, 9.0, [-2.34, -2.26, -1.46, -1.38], .05, suv, .06)
P.mesh('stms_tanksteel', s_, ST, smooth_angle=25)
g = Geo(); F = lambda az, z, o=0.0: frame_axes(tuple(pr(az, z, o)), z=V((math.sin(math.radians(az)), -math.cos(math.radians(az)), 0)))
for q, zn in ((-1, Z.white), (1, Z.copper)):
    f = F(q * 4.6, -1.86, .045); g.add(cyl(.155, .05, 28, zone=Z.dark, bevel=.012), f @ T(0, 0, .02)); g.add(cyl(.12, .09, 28, zone=Z.steel, bevel=.012), f @ T(0, 0, .05)); g.add(cyl(.075, .10, 24, zone=zn, bevel=.01), f @ T(0, 0, .055)); g.add(bolts(10, .138, .010), f @ T(0, 0, .046))
for x, z in ((-7.4, -2.14), (7.4, -2.14), (-7.4, -1.58), (7.4, -1.58)): g.add(cyl(.045, .05, 14, zone=Z.alu, bevel=.006), F(x, z, .06))
f = F(0, -1.60, .05); g.add(box(.30, .10, .04, zone=Z.dark, bevel=.008), f); g.add(box(.24, .06, .03, zone=Z.stripe), f @ T(0, 0, .012))
for q in (-1, 1):
    for z in (-.62, -.40): f = F(q * 15, z, .0); g.add(cyl(.075, .05, 20, zone=Z.dark, bevel=.01), f @ T(0, 0, .012)); g.add(cyl(.05, .06, 18, zone=Z.grey), f @ T(0, 0, .014))
    for z in (-2.9, -2.4, -1.3, -.7, .3, 1.2, 2.1): g.add(box(.17, .05, .018, zone=Z.alu, bevel=.004), F(q * 9.5, z, .078))
for k in range(9): f = F(0, -1.22 + k * .2, .03); g.add(tube([tuple(f @ V((x, 0, zz))) for x, zz in ((-.13, -.04), (-.13, .05), (.13, .05), (.13, -.04))], .010, 6, zone=Z.alu))
P.mesh('tanker_detail', g, P.det, smooth_angle=35); P.two_sided = True; P.variants = (); finish(P)

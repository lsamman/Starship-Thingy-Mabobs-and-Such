"""Ends for the two raceways of SEP's Block 3 core, which are cut off square at its top when nothing carries them on: the tapered dome
SEP's nosecone closes them with, rebuilt from measured sections. In the core's frame; a second MODEL on the expendable core (v3/patches/STMS_B3_Expendable.cfg)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from hls_common import sep_mat
P = start('STMS_RacewayCap'); MS = sep_mat(P, 'stms_steel', 'stms_steel_diff', 'stms_steel_nrm', 'stms_steelmask_diff')
SEC = [(21.35, 2.805), (21.2, 2.846), (20.8, 2.92), (19.9, 2.982), (18.7, 3.026), (17.3, 3.048), (15.9, 3.046), (14.5, 3.019), (13.4, 2.971), (12.6, 2.906), (12.3, 2.832), (12.2, 2.805)]      # azimuth, radius
Z0, C, R0 = 7.97, 16.75, 2.80; RINGS = [(-.03, 1, 1), (0, 1, 1), (.18, 1, 1), (.26, .92, .93), (.33, .80, .82), (.41, .73, .70), (.46, .67, .56), (.505, .60, .38), (.535, .54, .20), (.55, .50, .02)]
g = Geo()
for s in (-1, 1):
    rows = []
    for dz, w, h in RINGS:
        b = len(g.v); rows.append(b)
        for az, r in SEC: t = math.radians(s * (C + (az - C) * w)); r_ = R0 + (r - .004 - R0) * h; g.v.append((r_ * math.sin(t), -r_ * math.cos(t), Z0 + dz))
    m = len(SEC)
    for j in range(len(rows) - 1):
        for k in range(m - 1):
            q = [rows[j] + k, rows[j] + k + 1, rows[j + 1] + k + 1, rows[j + 1] + k]; uv = [((k + a) / m * .5, (RINGS[j + b][0] + .03)) for a, b in ((0, 0), (1, 0), (1, 1), (0, 1))]
            A, B, D_ = [Vector(g.v[i]) for i in (q[0], q[1], q[3])]; c = (A + B + D_) / 3; out = c - Vector((math.sin(math.radians(s * C)) * 2.75, -math.cos(math.radians(s * C)) * 2.75, c.z - .12))
            if (B - A).cross(D_ - A).dot(out) < 0: q, uv = q[::-1], uv[::-1]
            g.face(q, uv)
P.mesh('stms_racewaycap', g, MS, smooth_angle=50); P.two_sided = True; finish(P)

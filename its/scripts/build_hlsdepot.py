"""White storage depot nose for the Block 3 Expendable Core in white, after SpaceX's render of an HLS docked to a depot: the crew section's shape
with no windows, door or rails, four solar pockets and small blue position lights. Origin at the joint's stack node."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_Depot'); MW = sep_mat(P, 'hls_crew_o', 'hls_crew_o_diff', 'hls_crew_nrm', None, True)
O = HL.Z_TOP; dz = V((0, 0, O)); S0, S1 = HL.SOL_Z; d = Geo()
insol = lambda a: any(abs(wrap(a - s)) < HL.SOL_HW for s in HL.SOL_AZ)
zs = sorted({HL.Z_SKIN, S0, S1, HL.Z_OGIVE, *[HL.Z_OGIVE + z for z, _ in HL.OGIVE], *[HL.Z_OGIVE + z for z in (.42, 1.33, 2.2, 2.97, 3.75, 4.97, 6.0)], *[HL.Z_OGIVE + z for z, _ in HL.CAP if z < 8.56]})
g = skin(zs, 'crew_o', O, lambda a, z: not (S0 < z < S1 and insol(a)))
lim = 1 - HL.PAD * .5; g.uv = [tuple((u, min(v, lim)) for u, v in f) for f in g.uv]      # the cap shares the sheet's last row
n = len(g.v); ids = [i for i, p in enumerate(g.v[:n]) if abs(p[2] + O - HL.Z_OGIVE - 8.555) < 1e-4]; ids.sort(key=lambda i: math.atan2(g.v[i][0], -g.v[i][1])); g.v.append((0, 0, HL.Z_OGIVE + 8.565 - O))
for a, b in zip(ids, ids[1:] + ids[:1]): g.face([a, b, n], [(.5, lim)] * 3)
P.mesh('hull', g, MW, smooth_angle=30)
for k, az0 in enumerate(HL.SOL_AZ):                      # solar pockets, as on the crew section
    F = on_cyl(az0, (S0 + S1) / 2 - O, 0); Hh = (S1 - S0) / 2; DP = HL.SOL_DP; HWb = DP * math.sin(math.radians(HL.SOL_HW)); loc = lambda x, y, r: F @ V((x, y, r)); aa = [az0 - HL.SOL_HW + 3.75 * i for i in range(11)]
    for z, flip in ((S0, False), (S1, True)):
        ar = [hp(a, z) for a in aa]
        for i, (p, q) in enumerate(zip(ar, ar[1:])):
            b0 = loc(-HWb + 2 * HWb * i / 10, 0, DP); b1 = loc(-HWb + 2 * HWb * (i + 1) / 10, 0, DP); b0.z = b1.z = z - O; f = [p - dz, q - dz, b1, b0]; quad(f[::-1] if flip else f, Z.wall, d)
    for s in (-1, 1):
        e = [hp(az0 + s * HL.SOL_HW, z) - dz for z in (S0, S1)]; b = [loc(s * HWb, -Hh, DP), loc(s * HWb, Hh, DP)]; f = [e[0], b[0], b[1], e[1]]; quad(f if s < 0 else f[::-1], Z.wall, d)
    quad([loc(-HWb, -Hh, DP), loc(HWb, -Hh, DP), loc(HWb, Hh, DP), loc(-HWb, Hh, DP)], Z.wall, d); P.node(f'solar{k + 1}', F @ V((0, 0, HL.R)), F.to_3x3() @ V((0, 0, 1)), 1)
spots = []
for az in (78.75, 281.25): z = 25.1; spots += [(az, z, (1, 0, .35)), (az, z + .28, (-1, 0, .35)), (az, z + .56, (0, 1, .35)), (az, z - .28, (0, -1, .35))]
for az in (33.75, 146.25, 213.75, 326.25): z = 22.0; spots += [(az, z, (1, 0, .35)), (az, z + .28, (-1, 0, .35)), (az, z + .56, (0, 1, .35)), (az, z - .28, (0, -1, .35))]
rcs(P, d, spots, O)
bl = Geo()
for az in (22.5, 78.75, 157.5, 202.5, 281.25, 337.5):
    for z in (21.3,): d.add(lay(rounded_rect_ring(.11, .30, .05, .03, .02, 4, zone=Z.dark), az, z, O)); bl.add(lay(box(.05, .22, .016, zone=Z.lamp), az, z, O))
P.mesh('depotlights', bl, P.material('hls_det', nrm='its_det', shader='KSP/Emissive/Bumped Specular', spec=(.12, .12, .12), shininess=.3, emissive='hls_green_emit', name='hls_green'))
for az in (0, 180): d.add(lay(cyl(.10, .02, 22, zone=Z.white, bevel=.006), az, 24.3, O)); d.add(lay(cyl(.06, .026, 18, zone=Z.dark), az, 24.3, O))      # vents
zb = HL.Z_SKIN - O; d.add(lathe([(2.765, zb), (2.765, .30), (2.36, .33)], 96, zone=Z.wall, flip=True)); d.add(lathe([(2.36, .33), (0, .36)], 96, zone=Z.wall, flip=True)); d.add(lathe([(HL.R - .004, zb), (2.765, zb)], 96, zone=Z.alu, flip=True))
P.mesh('details', d, P.det, smooth_angle=40)
ringpts = lambda z, a0, a1, n, r=None: [tuple(hp(a0 + (a1 - a0) * i / n, z, r=r) - dz) for i in range(n + 1)]
for k in range(12): P.hull_collider(f'col_s{k}', [p for z in (HL.Z_SKIN, O + .40) for r in (2.75, HL.R) for p in ringpts(z, 30 * k, 30 * k + 30, 2, r)])
P.hull_collider('col_core', [p for z in (O + .36, HL.Z_OGIVE) for p in ringpts(z, 0, 345, 23, 1.6)])
P.hull_collider('col_low', [p for z in (O + .36, S0) for p in ringpts(z, 0, 345, 23)]); P.hull_collider('col_high', [p for z in (S1, HL.Z_OGIVE) for p in ringpts(z, 0, 345, 23)])
for i, (a, b) in enumerate(((0, 1.82), (1.82, 3.36), (3.36, 4.64), (4.64, 5.81), (5.81, 7.40), (7.40, 8.5))): P.hull_collider(f'col_n{i}', [p for z in (HL.Z_OGIVE + a, HL.Z_OGIVE + b) for p in ringpts(z, 0, 345, 23)])
P.node('bottom', (0, 0, 0), (0, 0, -1), 5); finish(P)

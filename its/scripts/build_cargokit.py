"""HLS Cargo kit, the second MODEL of the cargo section (build_hlscargo.py): body-mounted solar
panels round the back of the barrel, and bay lights. Same frame: barrel z -3.42..0, door at azimuth 0."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_CargoKit'); MS = P.material('its_solar', spec=(.25, .25, .28), shininess=.6); R = HL.R
pr = lambda az, z, r: V((r * math.sin(math.radians(az)), -r * math.cos(math.radians(az)), z))
Z0, Z1, ROWS, STEP = -3.02, -.32, 4, 12
for k, (a0, a1) in enumerate(((108, 144), (162, 198), (216, 252))):
    pn, fr = Geo(), Geo()
    for i in range(int((a1 - a0) / STEP)):
        A, B = a0 + i * STEP + .5, a0 + (i + 1) * STEP - .5
        for j in range(ROWS):
            za, zb = Z0 + (Z1 - Z0) * j / ROWS + .02, Z0 + (Z1 - Z0) * (j + 1) / ROWS - .02
            q = [pr(A, za, R + .038), pr(B, za, R + .038), pr(B, zb, R + .038), pr(A, zb, R + .038)]; n = len(pn.v); pn.v += [tuple(p) for p in q]; s = (i + j) % 4
            pn.face([n, n + 1, n + 2, n + 3], [(.02, (s + .02) / 4), (.98, (s + .02) / 4), (.98, (s + .98) / 4), (.02, (s + .98) / 4)])
            b = [pr(az, z, R + o) for o in (-.03, .032) for az, z in ((A - .25, za - .012), (B + .25, za - .012), (B + .25, zb + .012), (A - .25, zb + .012))]; n = len(fr.v); fr.v += [tuple(p) for p in b]
            for f in ((4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): fr.face([n + x for x in f], [Z.white.uv(*u) for u in ((0, 0), (.5, 0), (.5, .5), (0, .5))])
    P.mesh(f'cargo_panel{k}', pn, MS); P.mesh(f'cargo_panelframe{k}', fr, P.det)
    am = (a0 + a1) / 2; o_ = V((math.sin(math.radians(am)), -math.cos(math.radians(am)), 0)); M = Matrix((V((0, 0, 1)).cross(-o_), o_, V((0, 0, 1)))).transposed().to_4x4()
    if M.determinant() < 0: M = Matrix((-V((0, 0, 1)).cross(-o_), o_, V((0, 0, 1)))).transposed().to_4x4()
    M.translation = o_ * (R + .25) + V((0, 0, (Z0 + Z1) / 2)); P.empty(f'cargoSun{k}', M, P.model)
g = Geo()
sl_ = Geo()
for k in range(22):                                          # black sill the platform swings over
    az = -38.5 + 77 * (k + .5) / 22; a, b = az - 1.75, az + 1.75; q = [pr(x, z, R + o) for o in (-.03, .016) for x, z in ((a, -2.74), (b, -2.74), (b, -2.62), (a, -2.62))]; n = len(sl_.v); sl_.v += [tuple(p) for p in q]
    for f in ((4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6)): sl_.face([n + x for x in f], [(Z.stripe if abs(az) < 33 else Z.black).uv(*u) for u in ((0, 0), (.2, 0), (.2, .2), (0, .2))])
P.mesh('cargo_sill', sl_, P.det)
lp = Geo()
for s in (-1, 1):
    for z in (-.4, 2.0):
        p = pr(180 + s * 40, z, 2.60 if z < 0 else 2.42); F = frame_axes(tuple(p), z=V((-p.x, -p.y, 0)).normalized()); g.add(box(.34, .14, .08, zone=Z.grey, bevel=.015), F); lp.add(box(.28, .09, .02, zone=Z.lamp), F @ T(0, 0, .045)); add_spot(P, 'cargoLight', p + V((-p.x, -p.y, 0)).normalized() * .08, (-p.x, -p.y, -1.4), power=160, angle=110, reach=6)
P.mesh('cargo_trim', g, P.det); LM = P.material('its_det', shader='KSP/Emissive/Bumped Specular', spec=(.12, .12, .12), shininess=.4, emissive='hls_lamp_emit', name='hls_lamp'); P.mesh('cargo_lamps', lp, LM)
P.variants = (); finish(P)

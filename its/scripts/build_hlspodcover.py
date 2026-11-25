"""Jettisonable cover for the opening of a 2024-style leg pod: a flush plate that follows the pod's front, a toe under the foot and the
spring pushers that throw it off. Origin as the leg shroud: on the hull at the leg's own height, -Y outboard."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hls_common import *
P = start('STMS_HLS_PodCover'); OFF = T(0, HL.R, -HL.HINGE[1]); OW, OT, OR = HL.POD_OPEN; G_ = .014; TH = .045
d0 = lambda z: float(np.interp(z, [q[0] for q in HL.POD], [q[1] for q in HL.POD])); fy = lambda z: -(HL.R + d0(z))
W, R_ = OW - G_, OR - G_; ZT, ZB = OT - G_, .012
def hw(z): return W if z <= ZT - R_ else W - R_ + math.sqrt(max(0, R_ ** 2 - (z - ZT + R_) ** 2))
zs = [ZB, 1.2, 2.4, 3.6] + [ZT - R_ + R_ * math.sin(math.radians(t)) for t in (0, 15, 30, 45, 60, 75, 85)] + [ZT]; NX = 6
skin, inn, edge = Geo(), Geo(), Geo(); uvp = lambda x, y, z: huv(80 + math.degrees(math.atan2(x, -y)), 7.75 + z * .3, 'core')
for a, b in zip(zs, zs[1:]):
    for i in range(NX):
        u0, u1 = -1 + 2 * i / NX, -1 + 2 * (i + 1) / NX
        q = [(u0 * hw(a), fy(a), a), (u1 * hw(a), fy(a), a), (u1 * hw(b), fy(b), b), (u0 * hw(b), fy(b), b)]
        n = len(skin.v); skin.v += [tuple(OFF @ V(p)) for p in q]; skin.face(range(n, n + 4), [uvp(*p) for p in q])
        q = [(x, y + TH, z) for x, y, z in q][::-1]; n = len(inn.v); inn.v += [tuple(OFF @ V(p)) for p in q]; inn.face(range(n, n + 4), [Z.grey.uv(.5 + p[0] / 3.2, p[2] / 5) for p in q])
loop = [(-hw(z), z) for z in zs[::-1]] + [(hw(z), z) for z in zs]            # rim
for (x0, z0), (x1, z1) in zip(loop, loop[1:] + loop[:1]):
    q = [(x0, fy(z0), z0), (x0, fy(z0) + TH, z0), (x1, fy(z1) + TH, z1), (x1, fy(z1), z1)]; n = len(inn.v); inn.v += [tuple(OFF @ V(p)) for p in q]; inn.face(range(n, n + 4), [Z.white.uv(*t) for t in ((.1, .1), (.2, .1), (.2, .2), (.1, .2))])
put = lambda g, x, z, dy, m: g.add(m, OFF @ T(x, fy(z) + dy, z) @ Rx(0))
YH = -HL.R - .006                # toe: closes the bottom between the cover and the hull
inn.add(box(2 * W, abs(fy(0) - YH) - TH, .02, zone=Z.white, bevel=.004), OFF @ T(0, (fy(0) + YH + TH) / 2, ZB + .012))
for z in (.14, .95, 1.75, 2.55, 3.35, 4.15): inn.add(box(2 * W - .10, .030, .06, zone=Z.alu, bevel=.006), OFF @ T(0, fy(z) + TH + .014, z))
for s in (-1, 1):
    inn.add(box(.05, .030, 3.9, zone=Z.alu, bevel=.006), OFF @ T(s * (W - .06), (fy(.2) + fy(4.1)) / 2 + TH + .014, 2.15) @ Rx(math.degrees(math.atan2(-(fy(4.1) - fy(.2)), 3.9))))
    for z in (.5, 1.9, 3.3, 4.15):
        inn.add(box(.09, .05, .12, zone=Z.dark, bevel=.01), OFF @ T(s * (W - .06), fy(z) + TH + .045, z)); inn.add(cyl(.018, .07, 10, zone=Z.steel), OFF @ T(s * (W - .03), fy(z) + TH + .045, z) @ Ry(90))      # pushers
        edge.add(cyl(.020, .010, 12, zone=Z.steel), OFF @ T(s * (W - .06), fy(z) - .002, z) @ Rx(90))                    # bolt heads
edge.add(rounded_rect_ring(.30, .22, .04, .02, .008, 4, zone=Z.alu), OFF @ T(0, fy(2.35) - .002, 2.35) @ Rx(90))
P.mesh('cover', skin, hull_mat(P, 'hls_core'), smooth_angle=20); P.mesh('coverin', Geo().add(inn).add(edge), P.det, smooth_angle=30)
P.hull_collider('col', [tuple(OFF @ V((x, fy(z) + y, z))) for x in (-W, W) for z in (.05, 4.4) for y in (0, TH)])
P.node('mount', (0, 0, 0), (0, 1, 0), 1); finish(P)

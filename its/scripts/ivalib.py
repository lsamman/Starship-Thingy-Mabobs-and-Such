"""Cabin interiors. Authored in the part frame; the model empty carries the rotation from part space to KSP's internal
space (internal Unity = -(part Blender), as in SHABTech's habitat). Props come from HabTechProps and the stock set, by name."""
import bpy, sys, os, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sl import *
import iva_layout as IL, hls_layout as HL
V = Vector; R_IVA = Matrix(((-1, 0, 0), (0, 0, -1), (0, -1, 0)))
Z = {k: Zone(*v, atlas=IL.ATLAS, ppm=300) for k, v in IL.ZONES.items()}
T_WALL = .11; WELL = .44


def outer(variant):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'v3', 'scripts'))
    if variant == 'hls':
        zs = [-5] + [HL.Z_OGIVE - HL.Z_TOP + z for z, _ in HL.OGIVE] + [HL.Z_OGIVE - HL.Z_TOP + 8.5]; rs = [HL.R] + [r for _, r in HL.OGIVE] + [.3]
    else:
        import importlib.util
        sp = importlib.util.spec_from_file_location('v3layout', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'v3', 'scripts', 'layout.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        zs, rs = zip(*m.NOSE_RINGS); outer.big = m.NOSE_BIG
    outer.breaks = list(zs)
    return lambda z: float(np.interp(z, zs, rs))


def build(variant):
    S_ = IL.VARIANTS[variant]; name = 'STMS_IVA_' + {'hls': 'HLS', 'crew': 'Crew', 'crewcargo': 'CrewCargo'}[variant]
    out = sys.argv[sys.argv.index('--') + 1]; enable_addon(); clean_scene(); np.random.seed(5)
    P = Part(name); M = P.material('stms_iva', spec=(.25, .25, .25), shininess=.3)
    ML = P.material('stms_iva', shader='KSP/Emissive/Bumped Specular', spec=(.2, .2, .2), shininess=.3, emissive='stms_iva_emit', name='iva_lit')
    for it in ML.mumatprop.color.properties:
        if it.name == '_EmissiveColor': it.value = (1, 1, 1, 1)
    MG = P.material('stms_ivaglass', shader='KSP/Alpha/Translucent', name='iva_glass')
    ro = outer(variant); ri = lambda z: ro(z) - T_WALL
    HATCH = None; BREAKS = outer.breaks; PROPS, SEATS, CAMS, LIGHTS = [], [], [], []; SH = Geo()

    def pos(az, r, z): a = math.radians(az); return V((r * math.sin(a), -r * math.cos(a), z))
    def inw(az, z, r): return on_cyl(az, z, r) @ Ry(180)
    def prop(nm, origin, uy, uz, sc=1.0):
        uy = V(uy).normalized(); uz = V(uz); uz = (uz - uz.dot(uy) * uy).normalized(); bx = uz.cross(uy); q = (R_IVA @ Matrix((bx, uz, uy)).transposed()).to_quaternion(); p = V(origin)
        PROPS.append((nm, (-p.x, -p.y, -p.z), (-q.x, -q.z, -q.y, q.w), sc))
    def on_panel(F, nm, x=0, y=0, z=0, sc=1.0, roll=0): m = F @ T(x, y, z) @ Rz(roll); prop(nm, m.translation, m.to_3x3().col[2], -m.to_3x3().col[1], sc)
    def q4(g, pts, zone, toward, uvs=None):
        n = len(g.v); g.v += [tuple(p) for p in pts]; a, b, c = [V(p) for p in pts[:3]]; nrm = (b - a).cross(c - a); cen = sum((V(p) for p in pts), V()) / len(pts)
        idx = list(range(n, n + len(pts))); uvs = uvs or [zone.uv(*t) for t in ((0, 0), (1, 0), (1, 1), (0, 1))][:len(pts)]
        if nrm.dot(V(toward) - cen) < 0: idx, uvs = idx[::-1], uvs[::-1]
        g.face(idx, uvs)
    def seat(x, y, zf, fwd, title):
        c = V((x, y, zf + .131)); fwd = V(fwd).normalized(); up = V((0, 0, 1)); F = Matrix((fwd.cross(up), fwd, up)).transposed().to_4x4(); F.translation = c
        n = len(SEATS) + 1; P.empty(f'seat{n}', F, P.model); prop('htProps_seat_Orion2', c, up, -fwd); SEATS.append((f'seat{n}', title))
        ped.add(cyl(.10, .06, 16, zone=Z['dark'], bevel=.01, center_z=False), T(x, y, zf)); ped.add(cyl(.035, .10, 12, zone=Z['metal'], center_z=False), T(x, y, zf + .02))
    def light(p, e=800, reach=2.8, col=(1, .965, .90)): LIGHTS.append((p, e, reach, col))
    def bar_arc(g, r, z, a0, a1, rad, zone, n=24): g.add(tube([tuple(pos(a0 + (a1 - a0) * i / n, r, z)) for i in range(n + 1)], rad, 8, zone=Z[zone]))
    wall_, floor_, ceil_, fur, soft, led, scr, glass, ped = [Geo() for _ in range(9)]
    decks = S_['decks']; top = decks[0]; full = lambda a0, a1, n: [a0 + (a1 - a0) * i / n for i in range(n + 1)]

    def curved(g, a0, a1, prof, zone, n, toward_axis=True):
        """Profile (r, z) swept between azimuths, with end caps."""
        area = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(prof, prof[1:] + prof[:1])); cw = area < -1e-6       # outward of the closed profile
        for i in range(n):
            b0, b1 = a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n
            for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
                m = V((0, 0, 0)); g0 = len(g.v); g.v += [tuple(pos(b0, r0, z0)), tuple(pos(b1, r0, z0)), tuple(pos(b1, r1, z1)), tuple(pos(b0, r1, z1))]
                zn = Z[zone] if isinstance(zone, str) else zone
                f_, u_ = [g0, g0 + 1, g0 + 2, g0 + 3], [zn.uv(i / n, 0), zn.uv((i + 1) / n, 0), zn.uv((i + 1) / n, 1), zn.uv(i / n, 1)]
                g.face(f_[::-1] if cw else f_, u_[::-1] if cw else u_)
        for b, f in ((a0, False), (a1, True)):
            n0 = len(g.v); g.v += [tuple(pos(b, r, z)) for r, z in prof]; idx = list(range(n0, n0 + len(prof)))
            c = len(g.v); rr = sum(r for r, _ in prof) / len(prof); zz = sum(z for _, z in prof) / len(prof); g.v.append(tuple(pos(b, rr, zz)))
            for p, q in zip(idx, idx[1:] + idx[:1]): g.face([c, q, p] if f != cw else [c, p, q], [(Z[zone] if isinstance(zone, str) else zone).uv(.5, .5)] * 3)

    for di, D in enumerate(decks):
        zf = D['floor']; zc = D['ceil'] if D['ceil'] else zf + 1.46; win = D['win']; big = win == 'big'; holes = []
        if win and not big: wz, wn, span, ww, wh = win; holes = [(-span + 2 * span * i / (wn - 1), wz, ww, wh) for i in range(wn)]
        if big:
            B = outer.big; zc = B['z1'] + .25
        # ---- wall: columns by azimuth, rows by height, holes for the windows
        azs = {round(a, 4) for a in np.arange(-180, 180.01, 7.5)}; zs = {zf, zc}
        if D.get('eva'): holes = [h for h in holes if abs(h[0]) > 12.8]
        rm = ri(win[0]) if holes else 0
        for az, z0, w, h in holes:
            ha = math.degrees(w / 2 / rm); azs |= {round(az - ha, 4), round(az + ha, 4)}; zs |= {z0 - h / 2, z0 + h / 2}
        if big: WA = math.degrees(B["ha"] / ri(B["z0"])) - .01; azs |= {round(a, 4) for a in np.linspace(-WA, WA, 65)}; zs |= {B['z0'], 3.36}
        zs |= {z for z in BREAKS if zf + .02 < z < zc - .02 and not any(abs(z - q) < .02 for q in zs)}
        azs, zs = sorted(azs), sorted(zs); zs2 = [z for z in zs]
        def ring_uv(a, z): s = ((a + 180) / 60) % 1.00001; return Z['panel'].uv(min(1, s), (z - zf) / (zc - zf))
        def cell(a0, a1, pts):
            t0 = math.floor(((a0 + a1) / 2 + 180) / 60) * 60 - 180
            uv = [Z['panel'].uv(1 - (a - t0) / 60, min(1, max(0, (z - zf) / (zc - zf)))) for a, z in pts]
            q4(wall_, [pos(a, ri(z), z) for a, z in pts], None, (0, 0, (pts[0][1] + pts[2][1]) / 2), uv)
        def arch(a):
            x = abs(math.radians(a)) * ri(B['z0']); return B['z0'] + (B['z1'] - B['z0']) * max(0, 1 - (x / B['ha']) ** 2) ** .5 if x < B['ha'] else None
        for a0, a1 in zip(azs, azs[1:]):
            am = (a0 + a1) / 2
            if big and arch(am):
                t0, t1 = arch(a0) or B['z0'], arch(a1) or B['z0']
                [cell(a0, a1, [(a0, p), (a1, p), (a1, q), (a0, q)]) for p, q in zip(zs2, zs2[1:]) if q <= B['z0'] + .001]; up_ = [z for z in zs2 if z > max(t0, t1) + .015]; cell(a0, a1, [(a0, t0), (a1, t1), (a1, up_[0]), (a0, up_[0])]); [cell(a0, a1, [(a0, p), (a1, p), (a1, q), (a0, q)]) for p, q in zip(up_, up_[1:])]
                for (za, zb), tw in (((B['z0'], B['z0']), 1), ((t0, t1), -1)): q4(fur, [pos(a0, ri(za), za), pos(a1, ri(zb), zb), pos(a1, ro(zb) - .012, zb), pos(a0, ro(za) - .012, za)], Z['white'], pos(am, ri(za), (za + zb) / 2 + tw))
                q4(glass, [pos(a, ro(z) - .02, z) for a, z in ((a0, B['z0']), (a1, B['z0']), (a1, t1), (a0, t0))], Zone(0, 0, 64, 64, atlas=64), (0, 0, 3))
                continue
            for z0, z1 in zip(zs2, zs2[1:]):
                zm = (z0 + z1) / 2
                if any(abs(am - az) < math.degrees(w / 2 / rm) and abs(zm - hz) < h / 2 for az, hz, w, h in holes): continue
                cell(a0, a1, [(a0, z0), (a1, z0), (a1, z1), (a0, z1)])
        for az, hz, w, h in holes:
            ha = math.degrees(w / 2 / rm); zl, zh = hz - h / 2, hz + h / 2; rr = lambda z: ro(z) - .012
            for z, tw in ((zl, 1), (zh, -1)): q4(fur, [pos(az - ha, ri(z), z), pos(az + ha, ri(z), z), pos(az + ha, rr(z), z), pos(az - ha, rr(z), z)], Z['black'], pos(az, ri(z), z + tw))
            for a, tw in ((az - ha, 2), (az + ha, -2)): q4(fur, [pos(a, ri(zl), zl), pos(a, ri(zh), zh), pos(a, rr(zh), zh), pos(a, rr(zl), zl)], Z['black'], pos(a + tw, ri(hz), hz))
            q4(glass, [pos(az - ha, rr(zl) - .01, zl), pos(az + ha, rr(zl) - .01, zl), pos(az + ha, rr(zh) - .01, zh), pos(az - ha, rr(zh) - .01, zh)], Zone(0, 0, 64, 64, atlas=64), (0, 0, hz))
            sl = math.atan2(ri(zh) - ri(zl), zh - zl); F = inw(az, hz, ri(hz) * math.cos(math.radians(ha)) - .004) @ Rx(math.degrees(-sl))
            fur.add(rounded_rect_ring(w + .06, h + .06, min(.08, h * .25), .035, .016, 4, zone=Z['black']), F)
            if h > .5: fur.add(box(w, .03, .03, zone=Z['black']), F @ T(0, -.05, -.05))
        if big:                                          # the lattice, seen from inside
            ribs = []; sd = B['side']; hg = sd * .866; s1 = B['z1'] - B['z0']
            ins = lambda x, s: 0 <= s <= s1 and abs(x) < B['ha'] * max(0, 1 - (s / s1) ** 2) ** .5
            pt = lambda x, s: pos(math.degrees(x / ri(B['z0'])), ro(B['z0'] + s) - .035, B['z0'] + s)
            for j in range(0, 8):
                for i in range(-7, 8):
                    a = ((i + .5 * (j % 2)) * sd, j * hg)
                    for d in ((sd, 0), (sd / 2, hg), (-sd / 2, hg)):
                        ps = [(a[0] + d[0] * t / 8, a[1] + d[1] * t / 8) for t in range(9)]; ps = [p for p in ps if ins(*p)]
                        if len(ps) > 1: fur.add(tube([tuple(pt(*p)) for p in ps], .014, 5, zone=Z['white']))
            e = [(a, arch(a) or B['z0']) for a in np.linspace(-48.6, 48.6, 65)]; fur.add(tube([tuple(pos(a, ri(z) - .005, z)) for a, z in e], .03, 8, zone=Z['white'])); bar_arc(fur, ri(B['z0']) - .005, B["z0"], -49, 49, .03, 'white', 40)
        # ---- floor and the ceiling under the deck above, both open round the ladder well
        last = di == len(decks) - 1; R0 = 0 if last else WELL; N = 48
        for a0, a1 in zip(full(0, 360, N), full(0, 360, N)[1:]):
            for r0, r1 in zip(*(lambda rs: (rs, rs[1:]))([max(R0, .001), 1.2, ri(zf) + .02])):
                pl = [pos(a0, r0, zf), pos(a1, r0, zf), pos(a1, r1, zf), pos(a0, r1, zf)]; q4(floor_, pl, None, (0, 0, zf + 9), [Z['floor'].uv(.5 + p.x / 5.8, .5 + p.y / 5.8) for p in pl])
        if D['ceil']:
            zz = D['ceil']
            for a0, a1 in zip(full(0, 360, N), full(0, 360, N)[1:]):
                pl = [pos(a0, WELL, zz), pos(a1, WELL, zz), pos(a1, ri(zz) + .02, zz), pos(a0, ri(zz) + .02, zz)]; q4(ceil_, pl, None, (0, 0, zz - 9), [Z['ceil'].uv(.5 + p.x / 5.8, .5 + p.y / 5.8) for p in pl])
            za = decks[di - 1]['floor']; ceil_.add(lathe([(WELL, zz), (WELL, za)], 40, zone=Z['white'], flip=True))
        if not last:
            fur.add(lathe([(WELL, zf - .01), (WELL, zf + .03), (WELL + .05, zf + .035), (WELL + .06, zf)], 40, zone=Z['grey'], flip=False)); fur.add(lathe([(WELL + .062, zf), (WELL + .05, zf + .036), (WELL, zf + .03)][::-1], 40, zone=Z['grey'], flip=True))
            for a0, a1 in ((35, 145), (215, 325)):        # guard rails, open fore and aft
                for z in (.26, .48): bar_arc(fur, WELL + .13, zf + z, a0, a1, .014, 'black')
                for a in (a0, (a0 + a1) / 2, a1): fur.add(tube([tuple(pos(a, WELL + .13, zf)), tuple(pos(a, WELL + .13, zf + .48))], .014, 8, zone=Z['black']))
        # ---- cove light where wall meets ceiling
        rc = ri(zc); curved(led, 0, 360, [(rc - .10, zc - .012), (rc - .10, zc - .035), (rc - .015, zc - .035)][::-1], 'led', 72)
        bar_arc(fur, ri(zf) - .02, zf + .04, 0, 360, .022, 'dark', 72)
        for a in (30, 150, 270): light(pos(a, ri(zf) * .55, min(zc, zf + .85)), 900 if D['ceil'] is None else 600, 3.4 if D['ceil'] is None else 2.8)
        # ================================================================== themes
        th = D['theme']; rw = ri(zf + .5)
        if th == 'flight':
            # ceiling: tapered gores up to the docking tunnel
            ztop = {'hls': 9.95}.get(variant, 5.75); prof = [(ri(z), z) for z in np.linspace(zc, ztop, 8)]; ceil_.add(lathe(prof, 48, zone=Z['ceil'], flip=True)); rt = ri(ztop)
            ceil_.add(lathe([(rt, ztop), (.5 if rt > .6 else rt, ztop + .02), (0, ztop + .02)], 48, zone=Z['white'], flip=True)); zl = zc + (ztop - zc) * .55; curved(led, 0, 360, [(ri(zl) - .06, zl + .0), (ri(zl) - .06, zl - .03), (ri(zl) + .02, zl - .03)][::-1], 'led', 60)
            prop('htProps_HatchCBM', (0, 0, ztop + .012), (0, 0, -1), (0, 1, 0), 1.25 if rt > .5 else .9); light((0, 0, zl - .5), 900, 4.0)
            # console: flat stations under the windows
            zb = (B['z0'] if big else win[0] - win[4] / 2); nS = 4; sp_ = 44 if big else 37; zt = min(zb - .03, zf + .74); rT, rB = ri(zt) - .10, ri(zt) - .46; zB = zf + .46
            for i in range(nS):
                a0, a1 = -sp_ + 2 * sp_ * i / nS, -sp_ + 2 * sp_ * (i + 1) / nS; am = (a0 + a1) / 2; hw = math.radians((a1 - a0) / 2) * rB * .995
                Tl, Tr, Bl, Br = pos(a1, rT, zt), pos(a0, rT, zt), pos(a1, rB, zB), pos(a0, rB, zB)     # seen from the seat, right is -az
                q4(fur, [Bl, Br, Tr, Tl], None, (0, 0, zt + 1), [Z['console'].uv(*t) for t in ((0, 0), (1, 0), (1, 1), (0, 1))])
                q4(fur, [Tl, Tr, pos(a0, ri(zt) + .0, zt), pos(a1, ri(zt), zt)], Z['dark'], (0, 0, zt + 9)); q4(fur, [pos(a1, rB, zB), pos(a0, rB, zB), pos(a0, rB + .05, zB - .10), pos(a1, rB + .05, zB - .10)], Z['dark'], (0, 0, zB)); q4(fur, [pos(a1, rB + .20, zB - .10), pos(a0, rB + .20, zB - .10), pos(a0, rB + .20, zf), pos(a1, rB + .20, zf)], Z['locker'], (0, 0, zf + .2))
                q4(fur, [pos(a1, rB + .05, zB - .10), pos(a0, rB + .05, zB - .10), pos(a0, rB + .20, zB - .10), pos(a1, rB + .20, zB - .10)], Z['dark'], (0, 0, zf - 3))
                c = (Tl + Tr + Bl + Br) / 4; xax = (Br - Bl).normalized(); yax = ((Tl + Tr) / 2 - (Bl + Br) / 2).normalized(); F = Matrix((xax, yax, xax.cross(yax))).transposed().to_4x4(); F.translation = c
                assert F.to_3x3().col[2].z > 0
                for k in (-1, 0, 1): on_panel(F, f'htProps_MFD_orion{(k + 1 + i) % 3 + 1}', k * .235, .045, .003, .92)
                on_panel(F, 'htProps_translationController', .30, -.16, .003, 1.0)
                for nm, x, sc in (('genericClusterSwitches01', -.22, 1.2), ('genericClusterButtons', 0, 1.2), ('genericClusterKnobs', .14, 1.1)): on_panel(F, nm, x, -.155, .004, sc)
                if i == 1: on_panel(F, 'ButtonSquare', -.36, -.15, .004, 2.2); on_panel(F, 'throttle', .36, -.02, .004, .6)
                # a wide display between the windows and the console top
                fs = inw(am, zt + .10, ri(zt) - .13)
            curved(fur, -sp_ - 1.5, -sp_, [(rB, zf), (rB, zB), (rT, zt), (ri(zt), zt), (ri(zf), zf)], 'dark', 1); curved(fur, sp_, sp_ + 1.5, [(rB, zf), (rB, zB), (rT, zt), (ri(zt), zt), (ri(zf), zf)], 'dark', 1)
            n_ = min(4, D['seats']); names = ['Pilot', 'Commander', 'Flight Engineer', 'Mission Specialist']
            for k in range(n_):
                am = -sp_ + 2 * sp_ * (k + .5) / nS; d = V((math.sin(math.radians(am)), -math.cos(math.radians(am)), 0)); p = d * (rB - .42); seat(p.x, p.y, zf, d, names[k])
            # overhead nav display
            for a_, s0 in ((-24, 0), (0, 1), (24, 3)):
                if big: continue
                F = inw(a_, zc + .24, ri(zc + .24) - .05) @ Rx(12); scr.add(quad_patch(.62, .34, Zone(IL.ZONES['screen'][0] + s0 * 256, IL.ZONES['screen'][1], 256, 256, atlas=IL.ATLAS)), F); fur.add(box(.66, .38, .03, zone=Z['black'], bevel=.008, center=(0, 0, -.018)), F)
            # aft: curved bench and table, lockers behind
            bz = ri(zf + .3); curved(soft, 122, 238, [(bz - .52, zf + .20), (bz - .52, zf + .27), (bz - .14, zf + .25), (bz - .14, zf + .27), (bz - .09, zf + .66), (bz - .01, zf + .66), (bz - .01, zf + .20)], 'bench', 24); curved(fur, 122, 238, [(bz - .46, zf), (bz - .46, zf + .21), (bz, zf + .21)], 'white', 24)
            curved(led, 122, 238, [(bz - .463, zf + .03), (bz - .463, zf + .012)], 'led', 24)
            if variant == 'hls':
                tr = bz - 1.02; curved(fur, 140, 220, [(tr - .18, zf + .40), (tr - .18, zf + .43), (tr + .20, zf + .43), (tr + .20, zf + .40), (tr - .18, zf + .40)], 'wood', 16)
                for a in (150, 180, 210): fur.add(cyl(.035, .40, 12, zone=Z['metal'], center_z=False), T(*pos(a, tr, zf)))
                for a in (135, 165, 195, 225): d = pos(a, 1, 0); p = d * (bz - .34); SEATS.append((f'seat{len(SEATS) + 1}', 'Wardroom')); F = Matrix(((-d).cross(V((0, 0, 1))), -d, V((0, 0, 1)))).transposed().to_4x4(); F.translation = V((p.x, p.y, zf + .30)); P.empty(SEATS[-1][0], F, P.model)
                cab, sides = [], (78, 102, 258, 282)
            else: sides = (72, 96, 264, 288)
            for k, a in enumerate(sides):
                rp = ri(zf + .9) * .985 - .12; F = inw(a, zf + .30, rp); on_panel(F, 'htProps_cabinet3x3', 0, 0, 0); on_panel(F, 'htProps_cabinetPanel_01_2x2', -.088, .088, 0); [on_panel(F, 'htProps_galleyCupboard1x1', x, y, 0) for x, y in ((-.176, -.176), (0, -.176), (.176, -.176), (.176, 0))]; on_panel(F, 'htProps_cabinetMonitor', .176, .176, 0); on_panel(F, 'htProps_cabinetMonitorScreen_' + ('graph', 'grid', 'signal', 'topography')[k], .176, .176, 0)
                F = inw(a, zf + .84, rp); on_panel(F, 'htProps_cabinet3x3', 0, 0, 0); [on_panel(F, 'htProps_galleyCupboard1x1', x, y, 0) for x in (-.176, 0, .176) for y in (-.176, .0, .176)]
                fur.add(box(.60, 1.16, .25, zone=Z['white'], bevel=.01), inw(a, zf + .57, rp + .10) @ T(0, 0, -.11))
            F = inw(60 if variant == 'hls' else 58, zf + .6, ri(zf + .6) - .06); on_panel(F, 'htProps_fireExtinguisher', 0, 0, .02)
            for a in (112, 248): F = inw(a, zf + 1.0, ri(zf + 1.0) - .012); on_panel(F, 'htProps_airVent01', 0, 0, 0, 1.4)
        if th == 'commons':
            for k, a in enumerate((135, 151.5, 168, 184.5)):
                rp = ri(zf + .3) - .20; F = inw(a, zf + .285, rp); on_panel(F, 'htProps_cabinet3x3'); on_panel(F, 'htProps_galleyFoodPrep1x2' if k == 1 else 'htProps_cabinetPanel_01_2x2', -.088 if k != 1 else 0, .088); [on_panel(F, 'htProps_galleyCupboard1x1', x, y) for x, y in ((-.176, -.176), (0, -.176), (.176, -.176), (.176, 0), (.176, .176)) + (((-.176, 0), (-.176, .176)) if k == 1 else ())]; fur.add(box(.60, .56, .30, zone=Z['white'], bevel=.01), F @ T(0, 0, -.16))
                F = inw(a, zf + .87, rp); on_panel(F, 'htProps_cabinet3x2'); [on_panel(F, 'htProps_galleyCupboard1x1', x, y) for x in (-.176, 0, .176) for y in (-.088, .088)]; fur.add(box(.60, .38, .30, zone=Z['white'], bevel=.01), F @ T(0, 0, -.16))
            curved(fur, 126, 194, [(ri(zf) - .36, zf + .56), (ri(zf) - .36, zf + .59), (ri(zf) - .10, zf + .59), (ri(zf) - .10, zf + .56)], 'wood', 12); curved(led, 126, 194, [(ri(zf) - .30, zf + .668), (ri(zf) - .20, zf + .668)], 'led', 12)
            bz = ri(zf + .3); curved(soft, 205, 300, [(bz - .50, zf + .20), (bz - .50, zf + .27), (bz - .13, zf + .25), (bz - .09, zf + .64), (bz - .01, zf + .64), (bz - .01, zf + .20)], 'bench', 18); curved(fur, 205, 300, [(bz - .44, zf), (bz - .44, zf + .21), (bz, zf + .21)], 'white', 18); tr = bz - .98; curved(fur, 226, 280, [(tr - .16, zf + .40), (tr - .16, zf + .43), (tr + .18, zf + .43), (tr + .18, zf + .40), (tr - .16, zf + .40)], 'wood', 10); [fur.add(cyl(.03, .40, 12, zone=Z['metal'], center_z=False), T(*pos(a, tr, zf))) for a in (238, 268)]
            for k in range(D['seats']):
                a = (-50, -27, 27, 50)[k]; d = pos(a, 1, 0); p = d * (ri(zf + .5) - .62); seat(p.x, p.y, zf, d, 'Observation Deck')
            for a0_, a1_ in ((-56, -13), (13, 56)): curved(fur, a0_, a1_, [(ri(zf + .5) - .24, zf + .42), (ri(zf + .5) - .24, zf + .46), (ri(zf + .5), zf + .46), (ri(zf + .5), zf + .42)], 'wood', 8)
            e0, e1, ex, ey = IL.EVA; ex += .03; ey += .03; yo = -ri(zf + .5)            # the airlock chamber, with the hatch on its inner face
            for s in (-1, 1): q4(fur, [(s * ex, yo, zf), (s * ex, ey, zf), (s * ex, ey, zc), (s * ex, yo, zc)], Z['hex'], (s * 9, ey, zf + .5))
            q4(fur, [(-ex, ey, zf), (ex, ey, zf), (ex, ey, zc), (-ex, ey, zc)], Z['hex'], (0, 9, zf + .5))
            Fh = Matrix(((-1, 0, 0, 0), (0, 0, 1, ey), (0, 1, 0, (e0 + e1) / 2), (0, 0, 0, 1))); fur.add(quad_patch(.52, .94, Z['door']), Fh @ T(0, 0, .012)); fur.add(rounded_rect_ring(.62, 1.04, .14, .07, .04, 6, zone=Z['white']), Fh)
            fur.add(tube([tuple(Fh @ V((.10 * math.cos(t), .10 * math.sin(t), .05))) for t in np.linspace(0, TAU, 25)], .013, 8, zone=Z['metal'])); [fur.add(tube([tuple(Fh @ V((s * .30, y, z))) for y, z in ((-.2, 0), (-.2, .05), (.2, .05), (.2, 0))], .012, 6, zone=Z['black'])) for s in (-1, 1)]
            HATCH = (0, ey + .03, (e0 + e1) / 2, 'stms_airlock')
            for k, a in enumerate((62, 78, 94)):           # hydroponics
                F = inw(a, zf + .6, ri(zf + .6) - .02); fur.add(box(.58, 1.0, .12, zone=Z['white'], bevel=.01), F)
                for y in (-.30, 0, .30):
                    fur.add(box(.52, .07, .10, zone=Z['grey'], bevel=.01), F @ T(0, y, .09)); led.add(box(.50, .012, .03, zone=Z['led']), F @ T(0, y + .25, .075))
                    for j in range(7): g = Geo(); [g.add(box(.012, .10 + .04 * np.random.rand(), .05, zone=Z['green']), Rz(q) @ T(0, .05, 0)) for q in (-35, 0, 35)]; fur.add(g, F @ T(-.21 + .07 * j, y + .03, .09))
            F = inw(112, zf + .6, ri(zf + .6) - .06); on_panel(F, 'htProps_fireExtinguisher', 0, .2, .02); on_panel(F, 'htProps_cargoBag_small_firstAid', 0, -.1, 0)
        if th == 'bunks':
            rb, hb = ri(zf) - .62, zc - zf
            for k in range(6):                            # berths round the aft half, two high
                a0 = 72 + 36 * k; a1 = a0 + 36; am = (a0 + a1) / 2; w = 2 * rb * math.sin(math.radians(17.2)); rm2 = rb * math.cos(math.radians(17.2))
                q4(fur, [pos(a0, rb, zf), pos(a0, ri(zf), zf), pos(a0, ri(zc), zc), pos(a0, rb, zc)], Z['white'], pos(a0 + 5, rb, zf)); q4(fur, [pos(a1, rb, zf), pos(a1, ri(zf), zf), pos(a1, ri(zc), zc), pos(a1, rb, zc)], Z['white'], pos(a1 - 5, rb, zf))
                for j, zz in enumerate((zf + .06, zf + hb * .52)):
                    F = inw(am, zz, rm2); hh = hb * .44; fur.add(box(w, .05, .60, zone=Z['white'], bevel=.008, center=(0, 0, -.30)), F); soft.add(box(w - .08, .07, .46, zone=Z['bench'], bevel=.025, center=(0, .055, -.29)), F); soft.add(box(.16, .06, .30, zone=Z['pillow'], bevel=.025, center=(-w / 2 + .16, .115, -.28)), F); soft.add(box(w * .55, .03, .44, zone=Z['blue'], bevel=.012, center=(w * .12, .10, -.29)), F)
                    led.add(box(.22, .015, .02, zone=Z['led'], center=(0, hh - .03, -.52)), F); fur.add(rounded_rect_ring(w, hh, .07, .03, .02, 4, zone=Z['grey']), F @ T(0, hh / 2, 0))
                    cg = Geo(); cw = .20
                    for i in range(13): x = w / 2 - .03 - cw * i / 12; [cg.v.append((x, y, .0 + .016 * math.sin(i * 2.1))) for y in (.04, hh - .03)]
                    for i in range(12): cg.face([2 * i + 1, 2 * i + 3, 2 * i + 2, 2 * i], [Z['curtain'].uv(i / 12, 1), Z['curtain'].uv((i + 1) / 12, 1), Z['curtain'].uv((i + 1) / 12, 0), Z['curtain'].uv(i / 12, 0)])
                    soft.add(cg, F @ T(0, 0, -.03)); on_panel(F @ T(0, hh * .55, -.55), ('htProps_cargoBag_small_blue', 'htProps_cargoBag_small_white', 'htProps_cargoBag_small_red')[(k + j) % 3], .2 - .1 * (k % 3), 0, 0, .7)
            for k in range(D['seats']): a = (-24, 24)[k]; d = pos(a, 1, 0); p = d * (ri(zf + .5) - .66); seat(p.x, p.y, zf, d, 'Passenger')
            curved(fur, -50, 50, [(ri(zf + .5) - .24, zf + .42), (ri(zf + .5) - .24, zf + .46), (ri(zf + .5), zf + .46), (ri(zf + .5), zf + .42)], 'wood', 14)
            for a in (-60, 60): F = inw(a, zf + .5, ri(zf + .5) - .04); on_panel(F, 'htProps_cargoBag_small_white', 0, 0, .03, 1.2); on_panel(F, 'htProps_airVent01', 0, .4, .02, 1.2)
        if th == 'airlock':
            yb = -1.02; X = math.sqrt(ri(zf) ** 2 - yb ** 2); dw, dh0, dh1 = .44, zf + .08, zf + 1.14
            for x0, x1, z0, z1 in ((-X, -dw, zf, zc), (dw, X, zf, zc), (-dw, dw, zf, dh0), (-dw, dw, dh1, zc)):
                q4(wall_, [(x0, yb, z0), (x1, yb, z0), (x1, yb, z1), (x0, yb, z1)], None, (0, 0, z0), [Z['hex'].uv(min(1, max(0, (p[0] + X) / (2 * X))), (p[1] - zf) / (zc - zf)) for p in ((x0, z0), (x1, z0), (x1, z1), (x0, z1))])
            F = Matrix(((-1, 0, 0, 0), (0, 0, 1, yb), (0, 1, 0, (dh0 + dh1) / 2), (0, 0, 0, 1)))     # +Z toward the cabin
            HATCH = (0, yb + .02, (dh0 + dh1) / 2, 'airlock'); fur.add(quad_patch(2 * dw, dh1 - dh0, Z['door']), F @ T(0, 0, -.05)); fur.add(rounded_rect_ring(2 * dw + .14, dh1 - dh0 + .14, .18, .09, .06, 6, zone=Z['white'], base=-.05), F)
            for s in (-1, 1): fur.add(tube([tuple(F @ V((s * (dw + .16), y, z))) for y, z in ((-.32, 0), (-.32, .06), (.32, .06), (.32, 0))], .016, 8, zone=Z['black']))
            fur.add(tube([tuple(F @ V((.12 * math.cos(t), .12 * math.sin(t), .02))) for t in np.linspace(0, TAU, 25)], .014, 8, zone=Z['metal'])); [fur.add(tube([tuple(F @ V((0, 0, .01))), tuple(F @ V((.12 * math.cos(t), .12 * math.sin(t), .02)))], .010, 6, zone=Z['metal'])) for t in (0, 2.09, 4.19)]
            Fp = F @ T(.86, .12, .02); fur.add(box(.34, .26, .04, zone=Z['black'], bevel=.01), Fp); scr.add(quad_patch(.30, .20, Zone(IL.ZONES['screen'][0] + 768, IL.ZONES['screen'][1], 256, 256, atlas=IL.ATLAS)), Fp @ T(0, 0, .0225)); light((0, yb + .35, zc - .12), 500, 2.4)
            def suit():
                g = Geo(); zs_ = Z['suit']
                for s in (-1, 1):
                    g.add(tube([(s * .085, 0, .07), (s * .09, .005, .26), (s * .085, 0, .44)], .07, 10, zone=zs_, r_fn=lambda t: .064 + .02 * t)); g.add(box(.12, .19, .08, zone=Z['grey'], bevel=.025, center=(s * .09, -.025, .04))); g.add(tube([(s * .20, 0, .74), (s * .26, -.01, .58), (s * .26, -.06, .44)], .05, 10, zone=zs_, r_fn=lambda t: .056 - .012 * t)); g.add(box(.07, .08, .10, zone=Z['dark'], bevel=.022, center=(s * .26, -.065, .385)))
                g.add(lathe([(0, .42), (.14, .42), (.16, .50), (.185, .62), (.19, .72), (.15, .80), (.07, .82), (0, .82)], 18, zone=zs_), S(1, .8, 1)); g.add(lathe([(0, .80), (.13, .82), (.18, .92), (.185, 1.0), (.14, 1.12), (.06, 1.17), (0, 1.175)], 20, zone=zs_)); g.add(lathe([(.155, .87), (.18, .95), (.172, 1.04), (.12, 1.11)], 12, -62, 62, zone=Z['black']), T(0, -.018, 0)); g.add(box(.30, .16, .46, zone=Z['white'], bevel=.03, center=(0, .20, .68))); g.add(box(.18, .06, .12, zone=Z['dark'], bevel=.015, center=(0, -.16, .66))); g.add(box(.04, .02, .30, zone=Z['red'], center=(0, -.155, .48))); return g
            for a in (104, 126, 234, 256): p = pos(a, ri(zf) - .42, zf + .02); fur.add(suit(), T(*p) @ Rz(a + 180)); fur.add(box(.52, .10, 1.24, zone=Z['locker'], bevel=.01), T(*pos(a, ri(zf) - .10, zf + .62)) @ Rz(a))
            for a in (152, 170, 188, 206): F = inw(a, zf + .30, ri(zf) - .22); on_panel(F, 'htProps_cabinet3x3'); [on_panel(F, 'htProps_galleyCupboard1x1', x, y) for x in (-.176, 0, .176) for y in (-.176, 0, .176)]; fur.add(box(.60, .58, .28, zone=Z['white'], bevel=.01), F @ T(0, 0, -.15)); on_panel(inw(a, zf + .80, ri(zf) - .14), 'htProps_cargoBag_small_' + ('white', 'blue', 'red', 'white')[(a // 18) % 4], 0, 0, 0, 1.6)
            F = inw(84, zf + .6, ri(zf) - .04); on_panel(F, 'htProps_fireExtinguisher', 0, 0, .04); on_panel(inw(276, zf + .7, ri(zf) - .05), 'htProps_cargoBag_small_firstAid', 0, 0, .03, 1.2)
    # ---- ladder through every deck
    zlo, zhi = decks[-1]['floor'], decks[0]['floor'] + .60
    if len(decks) > 1:
        for s in (-1, 1): fur.add(tube([(s * .15, .37, zlo), (s * .15, .37, zhi)], .018, 8, zone=Z['metal']))
        for z in np.arange(zlo + .16, zhi, .20): fur.add(tube([(-.15, .37, float(z)), (.15, .37, float(z))], .012, 6, zone=Z['metal']))
        for s in (-1, 1): fur.add(tube([(s * .15, .37, zhi), (s * .15, .45, zhi + .02), (s * .15, WELL + .12, decks[0]['floor'])], .016, 8, zone=Z['metal']))
    # ---- windows to look out of, and lights
    wins = [(a, (decks[0]['win'][0] if decks[0]['win'] != 'big' else outer.big['z0'] + .75)) for a in (-24, 0, 24)] + [(0, d['win'][0]) for d in decks[1:] if d['win'] and d['win'] != 'big']
    for k, (a, z) in enumerate(wins):
        d = pos(a, 1, 0); up = V((0, 0, 1)); F = Matrix((d.cross(up), d, up)).transposed().to_4x4(); F.translation = pos(a, ri(z) - .28, z); nm = f'windowCam{k}'; P.empty(nm, F, P.model)
        C = F.copy(); C.translation = pos(a, ro(z) - .03, z); o = P.empty(nm + 'collider', C, P.model); m = o.muproperties; m.collider = 'MU_COL_BOX'; m.isTrigger = False; m.size = (.34, .05, .28); m.center = (0, 0, 0); CAMS.append((nm + 'collider', nm))
    for k, (p, e, reach, col) in enumerate(LIGHTS):
        ld = bpy.data.lights.new(f'light{k}', 'POINT'); ld.energy = e; ld.color = col; ld.use_custom_distance = True; ld.cutoff_distance = reach; ld.mulightprop.cullingMask = [True] * 32
        o = bpy.data.objects.new(f'light{k}', ld); P.coll.objects.link(o); P.place(o, Matrix.Translation(p), P.model)
    fur.add(ped)
    for nm, g, mt, sa in (('wall', wall_, M, 30), ('floor', floor_, M, 5), ('ceiling', ceil_, M, 40), ('furnishings', fur, M, 40), ('soft', soft, M, 60), ('led', led, ML, 30), ('screens', scr, ML, 30), ('glass', glass, MG, 60)):
        for k in range(0, len(g.f), 12000):              # Unity's 65k vertex limit
            c = Geo(); c.v, c.f, c.uv, c.smooth = g.v, g.f[k:k + 12000], g.uv[k:k + 12000], g.smooth[k:k + 12000]; used = sorted({i for q in c.f for i in q}); m_ = {i: n for n, i in enumerate(used)}
            c.v, c.f = [g.v[i] for i in used], [tuple(m_[i] for i in q) for q in c.f]; P.mesh(nm + (str(k // 12000) if k else ''), c, mt, smooth_angle=sa)
    P.model.rotation_mode = 'QUATERNION'; P.model.rotation_quaternion = R_IVA.to_quaternion(); bpy.context.view_layer.update()
    for o in P.coll.objects:
        if o not in (P.root, P.model): o.muproperties.layer = 16
    P.export(out); tris = sum(P.meta['tris'].values())
    assert len(SEATS) == sum(d['seats'] for d in decks), (len(SEATS), name)
    # ---- what FreeIva walks on: walls, floors and ceilings with the ladder well open, as one concave mesh
    S2 = Part(name + '_shell'); w = Geo(); n = 40
    for di, D in enumerate(decks):
        zf = D['floor']; last = di == len(decks) - 1
        zt = D['ceil'] if D['ceil'] else {'hls': 9.95}.get(variant, 5.75)
        w.add(lathe([(ri(z), z) for z in np.linspace(zf, zt, 2 if D['ceil'] else 9)], n, flip=True)); w.add(lathe([(ri(zf) + .02, zf), (0 if last else WELL, zf)], n)); w.add(lathe([(ri(zt) + .02, zt), (0 if not D['ceil'] else WELL, zt)], n, flip=True))
        if D['ceil']: w.add(lathe([(WELL, zt), (WELL, decks[di - 1]['floor'])], 24, flip=True))
        if D['theme'] == 'airlock': X = 2.6; q4(w, [(-X, -1.02, zf), (X, -1.02, zf), (X, -1.02, zt), (-X, -1.02, zt)], Z['white'], (0, 9, zf))
        if D.get('eva'):
            ex, ey = IL.EVA[2] + .03, IL.EVA[3] + .03
            for s_ in (-1, 1): q4(w, [(s_ * ex, -2.7, zf), (s_ * ex, ey, zf), (s_ * ex, ey, zt), (s_ * ex, -2.7, zt)], Z['white'], (s_ * 9, ey, zf))
            q4(w, [(-ex, ey, zf), (ex, ey, zf), (ex, ey, zt), (-ex, ey, zt)], Z['white'], (0, 9, zf))
    me = w.to_mesh('shellCollider'); o = bpy.data.objects.new('shellCollider', me); S2.coll.objects.link(o); S2.place(o, Matrix(), S2.model); o.muproperties.collider = 'MU_COL_MESH'; o.muproperties.isConvex = False; o.hide_render = True
    S2.model.rotation_mode = 'QUATERNION'; S2.model.rotation_quaternion = R_IVA.to_quaternion(); bpy.context.view_layer.update()
    for x_ in S2.coll.objects:
        if x_ not in (S2.root, S2.model): x_.muproperties.layer = 16
    S2.export(out)
    f = lambda v: ', '.join(('%.5f' % x).rstrip('0').rstrip('.') for x in v)
    L_ = ['// Generated by its/scripts/ivalib.py; edit there.', 'INTERNAL', '{', f'\tname = {name}', '\tMODEL', '\t{', f'\t\tmodel = StarshipThingyMabobsAndSuch/ITS/Parts/{name}', '\t}']
    for n, t in SEATS: L_ += ['\tMODULE', '\t{', '\t\tname = InternalSeat', f'\t\tseatTransformName = {n}', '\t\tallowCrewHelmet = false', f'\t\tdisplayseatName = {t}', '\t}']
    for c_, n in CAMS: L_ += ['\tMODULE', '\t{', '\t\tname = InternalCameraSwitch', f'\t\tcolliderTransformName = {c_}', f'\t\tcameraTransformName = {n}', '\t}']
    for n, p, q, sc in PROPS: L_ += ['\tPROP', '\t{', f'\t\tname = {n}', f'\t\tposition = {f(p)}', f'\t\trotation = {f(q)}', f'\t\tscale = {f((sc,) * 3)}', '\t}']
    pos_ = lambda p: f([-c for c in p])
    part_ = {'hls': 'STMS_HLS_Crew', 'crew': 'STMS_B3_NoseCrew', 'crewcargo': 'STMS_B3_NoseCrewCargo'}[variant]; PS = ':NEEDS[FreeIva]:LAST[StarshipThingyMabobsAndSuch]'
    FI = [f'@PART[{part_}]:HAS[!MODULE[ModuleFreeIva]]' + PS, '{', '\tMODULE', '\t{', '\t\tname = ModuleFreeIva', '\t}', '}', f'@INTERNAL[{name}]:HAS[!MODULE[InternalModuleFreeIva]]' + PS, '{', '\tMODEL', '\t{', f'\t\tmodel = StarshipThingyMabobsAndSuch/ITS/Parts/{name}_shell', '\t}',
          '\tMODULE', '\t{', '\t\tname = InternalModuleFreeIva', '\t\tshellColliderName = shellCollider', '\t\t// no depth mask mesh: the windows are real openings', '\t\tinternalDepthMaskName =', '\t\tShadows', '\t\t{', '\t\t\twall = TwoSided', '\t\t\tfloor = TwoSided', '\t\t\tceiling = TwoSided', '\t\t}', '\t}',
          '\t@PROP[htProps_HatchCBM]', '\t{', '\t\tMODULE', '\t\t{', '\t\t\tname = HatchConfig', '\t\t\tattachNodeId = port', '\t\t\thideDoorWhenConnected = true', '\t\t}', '\t}',
          '\tPROP', '\t{', '\t\tname = FreeIva_Hatch_Invisible_Handle', f'\t\tposition = {pos_(HATCH[:3])}', '\t\trotation = 1, 0, 0, 0', '\t\tscale = 0.34, 0.08, 0.34', '\t\tMODULE', '\t\t{', '\t\t\tname = HatchConfig', f'\t\t\tairlockName = {HATCH[3]}', '\t\t}', '\t}']
    for z in np.arange(zlo + .16, zhi, .20): FI += ['\tPROP', '\t{', '\t\tname = HandRailInvisible', f'\t\tposition = {pos_((0, .37, float(z)))}', '\t\trotation = 0, 0, 0, 1', '\t\tscale = 0.3, 0.02, 0.02', '\t}']
    pdir = os.path.join(out, '..', 'patches'); os.makedirs(pdir, exist_ok=True); open(os.path.join(pdir, name + '_FreeIva.cfg'), 'w').write('// Generated by its/scripts/ivalib.py; edit there. Walk about inside with FreeIva.\n' + '\n'.join(FI + ['}', '']))
    idir = os.path.join(out, '..', 'iva'); os.makedirs(idir, exist_ok=True); open(os.path.join(idir, name + '.cfg'), 'w').write('\n'.join(L_ + ['}', '']))
    print(f'EXPORT IVA {name}: {tris} tris, {len(SEATS)} seats, {len(PROPS)} props')

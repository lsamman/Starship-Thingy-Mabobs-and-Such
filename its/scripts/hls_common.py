"""Helpers for the HLS parts: a faceted hull of revolution that everything is laid on exactly."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import hls_layout as HL
V = Vector
_start = start
def start(name):
    P = _start(name); P.mats.clear(); P.det = sep_mat(P, 'hls_det', 'hls_det_diff', 'its_det_nrm', 'hls_det_mask_diff'); return P
RINGS = [(0.0, HL.R), (HL.Z_OGIVE, HL.R)] + [(HL.Z_OGIVE + z, r) for z, r in HL.OGIVE[1:]] + [(HL.Z_OGIVE + z, r) for z, r in HL.CAP[1:]]


def rad(z):
    """Vertex radius at z."""
    if z <= 0: return HL.R
    for (z0, r0), (z1, r1) in zip(RINGS, RINGS[1:]):
        if z <= z1: return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return 0.0


def hp(az, z, off=0.0, r=None):
    """Point on the faceted hull (or on a 96-sided prism of radius r), off outward."""
    c = HL.STEP * (math.floor(az / HL.STEP + 1e-9) + .5)
    rr = (rad(z) if r is None else r) * math.cos(math.radians(HL.STEP / 2)) / math.cos(math.radians(az - c)) + off
    a = math.radians(az); return V((rr * math.sin(a), -rr * math.cos(a), z))


def hsurf(az, z, off=0.0, z0=0.0):
    """Frame on the hull: +Z out, +Y up, +X toward increasing azimuth. z0 is the part's origin height."""
    a = math.radians(az); e = .03
    s = (rad(z + e) - rad(z - e)) / (2 * e)
    n = V((math.sin(a), -math.cos(a), -s)).normalized(); up = V((0, 0, 1)); up = (up - up.dot(n) * n).normalized()
    m = Matrix((up.cross(n), up, n)).transposed().to_4x4(); m.translation = hp(az, z) + n * off - V((0, 0, z0)); return m


def lay(g, az, z, z0=0.0, L_=.10, sink=.006):
    """Bend a flat piece (x across, y up, z off) onto the hull at (az, z)."""
    g = subdiv(g, L_); out = Geo(); out.f, out.uv, out.smooth = g.f, g.uv, g.smooth; r = rad(z); e = .03
    sl = (rad(z + e) - rad(z - e)) / (2 * e); c = 1 / math.sqrt(1 + sl * sl)
    for x, y, h in g.v:
        a = math.degrees(x / r); zz = z + y * c - (h - sink) * sl * c
        out.v.append(tuple(hp(az + a, zz, 0) + V((math.sin(math.radians(az + a)), -math.cos(math.radians(az + a)), 0)) * (h - sink) * c - V((0, 0, z0))))
    return out


def huv(az, z, sheet):
    """Half-hull sheet, mirrored. az in 0..360."""
    a = az % 360; a = a if a <= 180 else 360 - a
    z0, z1 = HL.SHEET[sheet]
    return (HL.PAD + (1 - 2 * HL.PAD) * a / 180, HL.PAD + (1 - 2 * HL.PAD) * (z - z0) / (z1 - z0))


def skin(zs, sheet, z0=0.0, keep=None):
    """Outer skin through the given heights on the facet grid; keep(az_mid, z_mid) False leaves a hole."""
    g = Geo(); ids = {}
    def vid(k, z):
        key = (k % HL.SIDES, z)
        if key not in ids:
            ids[key] = len(g.v); p = hp(k * HL.STEP, z); g.v.append((p.x, p.y, z - z0))
        return ids[key]
    for za, zb in zip(zs, zs[1:]):
        for k in range(HL.SIDES):
            am = (k + .5) * HL.STEP
            if keep and not keep(am, (za + zb) / 2): continue
            u = lambda kk, z: huv(kk * HL.STEP if am < 180 or kk * HL.STEP < 360 else 360, z, sheet)
            g.face([vid(k, za), vid(k + 1, za), vid(k + 1, zb), vid(k, zb)], [u(k, za), u(k + 1, za), u(k + 1, zb), u(k, zb)])
    return g


def blister(zs, zone, inner=0.0, flip=False, n=18, shell=None, width=None, scale=None):
    """Shell over a stowed leg, from HL.SHELL, in the hull frame at azimuth 0."""
    H_ = lambda z: float(np.interp(z, *zip(*(shell or HL.SHELL)))); W_ = lambda z: float(np.interp(z, *zip(*(width or HL.SHELL_W)))); g = Geo(); rows = []
    for z in zs:
        h, w = H_(z), W_(z) - inner; row = []
        for k in range(n + 1):
            u = -1 + 2 * k / n; lat = max(0.0, 1 - abs(u) ** 3.0) ** .6; x = u * w; y = -math.sqrt(HL.R ** 2 - x * x); out = max(0.0, h - inner) * lat - .012
            row.append(len(g.v)); g.v.append(tuple(V((x, y, z)) + V((x, y, 0)).normalized() * out))
        rows.append(row)
    for j, (a, b) in enumerate(zip(rows, rows[1:])):
        for k in range(n):
            f = [a[k], a[k + 1], b[k + 1], b[k]]; u = [tuple(scale * c_ for c_ in (g.v[i][0] * 1.15, g.v[i][2])) for i in f] if scale else [zone.uv(kk / n, (zs[jj] - zs[0]) / (zs[-1] - zs[0])) for kk, jj in ((k, j), (k + 1, j), (k + 1, j + 1), (k, j + 1))]; g.face(f[::-1] if flip else f, u[::-1] if flip else u)
    return g


def wrap(az): return (az + 180) % 360 - 180


def fac(r, z0, z1, a0, a1, zone, flip=False, n=None):
    """Cylinder wall patch on a 96-sided prism."""
    n = n or max(1, round((a1 - a0) / HL.STEP)); g = Geo()
    for i in range(n + 1):
        for z in (z0, z1): g.v.append(tuple(hp(a0 + (a1 - a0) * i / n, z, r=r)))
    for i in range(n):
        q = [2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1]; u = [zone.uv(i / n, 0), zone.uv((i + 1) / n, 0), zone.uv((i + 1) / n, 1), zone.uv(i / n, 1)]
        g.face(q[::-1] if flip else q, u[::-1] if flip else u)
    return g


def quad(pts, zone, g=None):
    g = g or Geo(); n = len(g.v); g.v += [tuple(p) for p in pts]
    g.face(range(n, n + 4), [zone.uv(0, 0), zone.uv(1, 0), zone.uv(1, 1), zone.uv(0, 1)]); return g


def plate(outer, holes, z, zone, scale=.25, up=False):
    """Flat plate with round holes, planar mapped."""
    from mathutils.geometry import tessellate_polygon
    loops = [[V((x, y, 0)) for x, y in l] for l in [outer] + holes]; flat = [p for l in loops for p in l]; g = Geo()
    g.v = [(p.x, p.y, z) for p in flat]
    for t in tessellate_polygon(loops):
        p = [flat[i] for i in t]; nz = (p[1] - p[0]).cross(p[2] - p[0]).z
        if abs(nz) < 1e-9: continue
        t = t if (nz > 0) == up else t[::-1]
        g.face(t, [zone.uv(.5 + flat[i].x / 6, .5 + flat[i].y / 6) for i in t])
    return g


def circ(r, n=32, cx=0, cy=0): return [(cx + r * math.cos(TAU * i / n), cy + r * math.sin(TAU * i / n)) for i in range(n)]


def rcs(P, det, spots, z0=0.0):
    """Small flush ports and their thruster transforms. spots: (az, z, (x, y, z) exhaust direction in the hull frame)."""
    for az, z, d in spots:
        fr = hsurf(az, z, 0, z0); dd = fr.to_3x3() @ V(d).normalized()
        det.add(lay(rounded_rect_ring(.15, .15, .07, .03, .02, 5, zone=Z.black), az, z, z0)); det.add(lay(cyl(.052, .012, 14, zone=Z.rubber), az, z, z0, sink=0))
        # thruster transforms: exhaust along local +Z
        P.empty('RCSthruster', frame_axes(fr.translation + fr.to_3x3() @ V((0, 0, .03)), dd), P.model)


def sep_mat(P, name, base, nrm, mask=None, tiles=False):
    """SEP's own shader with its settings (Resurfaced, the numbers of its steel and tile materials), so the metal matches."""
    m = bpy.data.materials.new(name); mp = m.mumatprop; mp.shaderName = 'Resurfaced/PackedMetalAO'
    for k, t, n in (('_MainTex', base, False), ('_BumpMap', nrm, False), ('_MetalMap', mask, False), ('_AOMap', mask, False)):
        if t: it = mp.texture.properties.add(); it.name = k; it.tex = t; it.type = n; it.scale = (1, 1); it.offset = (0, 0)
    for k, v in (('_Color', (1, 1, 1, 1)), ('_EmissiveColor', (0, 0, 0, 0)), ('_RimColor', (0, 0, 0, 0)), ('_TemperatureColor', (0, 0, 0, 0))): it = mp.color.properties.add(); it.name = k; it.value = v
    for k, v in (('_Smoothness', 1), ('_MetalAlbedoMultiplier', 1), ('_Metalness', 0 if tiles else 1), ('_MetalRedMult', 0 if tiles else 1), ('_MetalGreenMult', 0), ('_MetalBlueMult', 0), ('_AORedMult', 1 if tiles else 0), ('_AOGreenMult', 1), ('_AOBlueMult', 1 if tiles else 0)):
        it = mp.float3.properties.add(); it.name = k; it.value = v
    return m


def hull_mat(P, sheet): return sep_mat(P, sheet, sheet + '_diff', sheet + '_nrm', None, True)          # paint: no metal, smoothness in the alpha


def glass_mat(P): return P.material('its_glass', shader='KSP/Emissive/Bumped Specular', spec=(1, 1, 1), shininess=.8, emissive='its_glass_emit')


def lamp_mat(P): return P.material('hls_det', nrm='its_det', shader='KSP/Emissive/Bumped Specular', spec=(.12, .12, .12), shininess=.4, emissive='hls_lamp_emit', name='hls_lamp')

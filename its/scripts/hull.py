"""The ITS ship's outer mould line and the numbers every part shares. Pure numpy, so textures and checks use it too.

Real metres, measured off SpaceX's 2016 slides (cutaway p36, CFD p38, Enceladus and back-quarter renders):
z = 0 at the vacuum engines' exit, z = 49.5 at the nose tip. Azimuth 0 is leeward (Blender -Y), 180 windward.
Parts are authored at z_ksp = (z - origin) * K.
"""
import numpy as np
K = 0.625
RB = 6.0                          # body radius
Z_TIP, Z_TAN, Z_SPLIT = 49.5, 34.0, 27.0
Z_LEE, Z_WIND = 5.0, 0.8          # skirt bottom edge: leeward, windward (render 31's swoosh)
Z_STAGE = 5.0                     # ship z at the top of the booster's interstage: 77.5 + 49.5 - 122 m
O_AFT, O_FWD = 15.0, 36.0         # part origins
RIDGE_AZ = (0.0, 120.0, 240.0)
R_RIDGE, W_RIDGE = 9.4, 0.65      # gives the published 17 m max width across the two lateral fairings
Z_R0, Z_R1, Z_R2, Z_R3 = 35.9, 15.6, 14.2, 6.3

# engines
R_SL = 1.95 * 0.8                 # 3 sea-level, real metres
R_VAC = 3.9                       # 6 vacuum
TIE_AZ = 0

_D = np.array([0, .12, .45, 1.1, 2.0, 3.5, 5.5, 7.4, 10.0, 12.9, 15.5, 60])
_R = np.array([0, .62, 1.18, 1.80, 2.42, 3.20, 4.02, 4.65, 5.36, 5.87, 6.0, 6.0])


def _pchip(x, xs, ys):
    """Monotone cubic, so the nose has no ripples."""
    h = np.diff(xs); d = np.diff(ys) / h
    m = np.zeros_like(ys)
    for i in range(1, len(xs) - 1):
        if d[i - 1] * d[i] > 0:
            w1 = 2 * h[i] + h[i - 1]; w2 = h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    m[0] = d[0]; m[-1] = d[-1]
    x = np.clip(x, xs[0], xs[-1])
    k = np.clip(np.searchsorted(xs, x) - 1, 0, len(xs) - 2)
    t = (x - xs[k]) / h[k]
    return ((1 + 2 * t) * (1 - t) ** 2 * ys[k] + t * (1 - t) ** 2 * h[k] * m[k]
            + t * t * (3 - 2 * t) * ys[k + 1] + t * t * (t - 1) * h[k] * m[k + 1])


def body_r(z):
    # interpolate r^2: a blunt tip has finite curvature there
    return np.sqrt(np.maximum(_pchip(Z_TIP - np.asarray(z, float), _D, _R ** 2), 0))


def droop(z):
    """The nose axis leans to windward, so the belly runs straighter than the back (CFD slide). Positive = windward."""
    t = np.clip((np.asarray(z, float) - Z_TAN) / (Z_TIP - Z_TAN), 0, 1)
    return 0.85 * t ** 2


def ridge(z):
    """Fairing crest radius and half-width at z."""
    z = np.asarray(z, float)
    up = RB + (R_RIDGE - RB) * (Z_R0 - z) / (Z_R0 - Z_R1)
    dn = RB + (R_RIDGE - RB) * (z - Z_R3) / (Z_R2 - Z_R3)
    R = np.minimum(np.minimum(up, dn), R_RIDGE)
    R = R_RIDGE - _softplus(R_RIDGE - R - .0, .10) + _softplus(np.zeros(()), .10)
    R = np.maximum(R, RB)
    return R, W_RIDGE * (R - RB) / (R_RIDGE - RB)


def _softplus(x, k):
    return k * np.log1p(np.exp(np.clip(x / k, -50, 50)))


def angles(z):
    """Corner and tangent azimuths (deg) of a fairing at z: crest is flat to pc, its side meets the body at pt."""
    R, w = ridge(z)
    pc = np.degrees(np.arctan2(w, R))
    rho = np.hypot(R, w)
    pt = pc + np.degrees(np.arccos(np.clip(RB / rho, -1, 1)))
    return np.maximum(pc, 1.2), np.clip(pt, 14, 59)


def section_r(az, z):
    """Outer radius at azimuth az (deg) about the (drooped) axis. Convex hull of body and fairings, corners eased."""
    az = np.asarray(az, float)
    th = np.abs((az + 60) % 120 - 60)
    R, w = ridge(z)
    b = body_r(z)
    rho = np.hypot(R, w)
    pc = np.arctan2(w, R)
    pt = pc + np.arccos(np.clip(RB / rho, -1, 1))
    t = np.radians(th)
    crest = R / np.cos(np.minimum(t, 1.2))
    side = np.where(t < pt, RB / np.cos(pt - t), RB)
    k = .09
    m = np.where(R > RB + .02, -k * np.logaddexp(-crest / k, -side / k), b)
    fair = np.maximum(m, RB)
    return np.where(np.asarray(z) > Z_TAN, np.maximum(b, np.where(R > RB + .02, b + (fair - RB), b)), fair)


def point(az, z, off=0.0):
    """Surface point in real metres (Blender axes), pushed out radially by off."""
    r = section_r(az, z) + off
    a = np.radians(az)
    return np.array([r * np.sin(a), -r * np.cos(a) + droop(z), np.broadcast_to(z, np.shape(r)) * 1.0])


def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def skirt_z(az):
    """Bottom edge of the skirt."""
    a = np.abs((np.asarray(az, float) + 180) % 360 - 180)
    return Z_LEE + (Z_WIND - Z_LEE) * _ss(82, 128, a)


def tps_az(z):
    """Half-azimuth where the white leeward paint meets the heat shield, per the renders."""
    z = np.asarray(z, float)
    zs = np.array([0, 6.0, 6.7, 9.0, 12.2, 15.0, 22, 30, 36.5, 43.0, 46.5, 48.2, 48.95, 49.25, 49.5])
    az = np.array([80, 80, 83, 92, 106, 111, 111, 109, 100, 92, 86, 74, 48, 5, 0])
    return _pchip(z, zs, az)


def paint_d(az, z):
    """Signed distance (real metres, positive inside) to the edge of the white paint: the leeward panel above the black
    skirt band, minus the trapezoid leg pod on the dorsal fairing (SpaceX's Enceladus render)."""
    a = np.abs((np.asarray(az, float) + 180) % 360 - 180); z = np.asarray(z, float)
    r = np.maximum(np.where(z > Z_TAN, body_r(z), RB), .3)
    d1 = np.radians(tps_az(z) - a) * r
    d2 = (z - 6.7)
    x = np.radians(a) * RB                          # pod: edge from (1.0, 14.0) to (3.9, 6.7)
    nx, nz = 7.3, 2.9
    d3 = ((x - 1.0) * nx + (z - 14.0) * nz) / np.hypot(nx, nz)
    d3 = np.maximum(d3, z - 14.0)
    k = .22
    return -k * np.logaddexp(np.logaddexp(-d1 / k, -d2 / k), -d3 / k)


def col_az(z, n=18):
    """Azimuth of every mesh column at z: columns follow the fairing corners. 6*n columns, closed."""
    pc, pt = angles(z)
    k = n
    out = []
    half = np.concatenate([[0, .55 * pc, .9 * pc, pc + .05 * (pt - pc), pc + .13 * (pt - pc)],
                           pc + (pt - pc) * np.linspace(.3, 1, k - 12),
                           pt + (60 - pt) * np.linspace(0, 1, 9)[1:-1]])
    half = half[:k]
    for c in RIDGE_AZ:
        out += list(c + half) + [c + 60] + list(c + 120 - half[::-1])[:-1]
    return np.array(out)


# ------------------------------------------------------------------ texture mapping
_zs = np.linspace(0, Z_TIP, 4001)
_rs = body_r(_zs)
_arc = np.concatenate([[0], np.cumsum(np.hypot(np.diff(_zs), np.diff(_rs)))])


def arc(z):
    return np.interp(z, _zs, _arc)


def arc_inv(s):
    return np.interp(s, _arc, _zs)


SHEET = {'aft': (Z_WIND - .2, Z_SPLIT), 'fwd': (Z_SPLIT, Z_TIP)}
PAD = 0.012


def uv(az, z, sheet):
    """Half-hull sheet, mirrored left/right: u = |az|/180, v = meridian arc."""
    z0, z1 = SHEET[sheet]
    a = np.abs((np.asarray(az, float) + 180) % 360 - 180)
    u = PAD + (1 - 2 * PAD) * a / 180
    v = PAD + (1 - 2 * PAD) * (arc(z) - arc(z0)) / (arc(z1) - arc(z0))
    return u, v


def grid(w, h, sheet):
    """az, z for every pixel of a sheet (row 0 at the image top)."""
    z0, z1 = SHEET[sheet]
    u = (np.arange(w) + .5) / w; v = 1 - (np.arange(h) + .5) / h
    a = (u - PAD) / (1 - 2 * PAD) * 180
    s = (v - PAD) / (1 - 2 * PAD) * (arc(z1) - arc(z0)) + arc(z0)
    return np.meshgrid(a, arc_inv(s))

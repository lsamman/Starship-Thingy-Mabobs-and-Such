"""Turns hull.py into meshes."""
import numpy as np
from sl import *
import hull as H


def ship_rows(z0, z1, extra=()):
    zs = {z0, z1}
    for a, b, n in ((0, 6.3, 3), (6.3, 14.2, 8), (14.2, 15.6, 5), (15.6, 34, 14), (34, 36.2, 4), (36.2, 43, 10), (43, 47, 9), (47, 48.8, 8), (48.8, 49.4, 6), (49.4, 49.5, 4)):
        for z in np.linspace(a, b, n + 1):
            if z0 < z < z1:
                zs.add(round(float(z), 4))
    zs |= {z for z in extra if z0 < z < z1}
    return sorted(zs)


def skin(z0, z1, sheet, origin, extra=(), keep=None, skirt=False, off=0.0, flip=False, zones=None):
    """Outer skin between z0 and z1 (real). keep(az, z) drops quads whose centre returns False."""
    g = Geo()
    rows = ship_rows(z0, z1, extra)
    if skirt:
        # rows below Z_R3 stretch down to the skirt's edge instead of stopping level
        rows = [r for r in rows if r > H.Z_R3]
        rows = [H.Z_R3] + rows if rows[0] > H.Z_R3 else rows
    grid = []
    def add_row(az, z):
        x, y, zz = H.point(az, z, off)
        ids = []
        for i in range(len(az)):
            ids.append(len(g.v)); g.v.append((x[i] * H.K, y[i] * H.K, (np.broadcast_to(z, az.shape)[i] - origin) * H.K))
        grid.append((ids, az, np.broadcast_to(z, az.shape)))
    if skirt:
        az = H.col_az(H.Z_R3)
        for t in (1.0, .75, .5, .25):
            add_row(az, H.skirt_z(az) * t + H.Z_R3 * (1 - t))
    for z in rows:
        az = H.col_az(z)
        add_row(az, np.full(az.shape, z))
    n = len(grid[0][0])
    for (ia, aa, za), (ib, ab, zb) in zip(grid, grid[1:]):
        for k in range(n):
            k2 = (k + 1) % n
            q = [ia[k], ia[k2], ib[k2], ib[k]]
            azs = [aa[k], aa[k2], ab[k2], ab[k]]; zz = [za[k], za[k2], zb[k2], zb[k]]
            if k2 == 0:
                azs[1] += 360; azs[2] += 360
            c = sum(azs) / 4; zc = sum(zz) / 4
            if keep and not keep(c % 360, zc):
                continue
            side = 1 if c % 360 <= 180 else -1
            uvs = []
            for a_, z_ in zip(azs, zz):
                a2 = a_ if c <= 180 else 360 - a_
                uvs.append(tuple(float(t) for t in H.uv(np.clip(abs(a2), 0, 180), z_, sheet)))
            if zb[k] >= H.Z_TIP - 1e-6:            # pole
                q, uvs = q[:2] + [ib[0]], uvs[:2] + [uvs[3]]
            if flip:
                q, uvs = q[::-1], uvs[::-1]
            g.face(q, uvs)
    return g


def hull_points(z0, z1, origin, n=3, zs=None, off=0.0):
    """Sparse points for a convex collider."""
    pts = []
    for z in (zs or (z0, z1)):
        az = np.concatenate([np.array([-9, 9, 35, 60, 85]) * 1.0 + c for c in H.RIDGE_AZ]) if n == 3 else np.linspace(0, 360, n, endpoint=False)
        x, y, _ = H.point(az, z, off)
        pts += [(x[i] * H.K, y[i] * H.K, (z - origin) * H.K) for i in range(len(az))]
    return pts

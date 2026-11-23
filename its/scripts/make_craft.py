"""Writes ready-to-fly craft files: full stacks for each ship variant, and the bare ship.
usage: make_craft.py <build/mu> <out dir>"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L
MU, OUT = sys.argv[1:3]
Vt = (1.8125, -0.92042923)


def node(part, n):
    if part.startswith('ITS_Ring'):
        return (0, 0, 0), (0, 1, 0)
    if part == 'ITS_RVac':
        return (0, Vt[0] * L.RV_SCALE, 0), (0, 1, 0)
    if part.startswith('SEP_26_R3'):
        return (0, Vt[0], 0), (0, 1, 0)
    j = json.load(open(os.path.join(MU, part + '.json')))['nodes'][n]
    return tuple(j['pos']), tuple(j['dir'])


NID = {'ITS_RVac': 'node_top_R3', 'SEP_26_R3_SL_C': 'node_top_R3'}
s_ = lambda v: '|'.join(('%.6g' % x) for x in v)


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def qrot(q, v):
    x, y, z, w = q
    t = [2 * (y * v[2] - z * v[1]), 2 * (z * v[0] - x * v[2]), 2 * (x * v[1] - y * v[0])]
    return tuple(v[i] + w * t[i] + c for i, c in enumerate((y * t[2] - z * t[1], z * t[0] - x * t[2], x * t[1] - y * t[0])))


class P:
    uid = 4290100000

    def __init__(self, part, **kw):
        P.uid += 1
        self.part, self.id = part, part.replace('_', '.') + '_%d' % P.uid
        self.kids, self.att, self.rot = [], [], (0, 0, 0, 1)
        self.pos = (0, 0, 0); self.parent = None; self.sym = []; self.st = dict(istg=-1, dstg=0, sidx=-1, sqor=-1, sepI=-1); self.st.update(kw)

    def put(self, child, mine, theirs, rot=(0, 0, 0, 1)):
        """Attach child: its node 'theirs' to my node 'mine'. rot is the child's rotation in my frame."""
        child.parent = self; child.rot = qmul(self.rot, rot)
        a, da = node(self.part, mine); b, db = node(child.part, theirs)
        wa = qrot(self.rot, a); wb = qrot(child.rot, b)
        child.pos = tuple(self.pos[i] + wa[i] - wb[i] for i in range(3))
        child.lrot = rot; self.kids.append(child)
        ids = lambda p, n: NID.get(p.part, n)
        self.att.append(f'{ids(self, mine)},{child.id}_{s_(a)}_{s_(da)}_{s_(a)}_{s_(da)}')
        child.att.append(f'{ids(child, theirs)},{self.id}_{s_(b)}_{s_(db)}_{s_(b)}_{s_(db)}')
        return child

    def walk(self):
        yield self
        for k in self.kids:
            yield from k.walk()


def sym(ps):
    for p in ps:
        p.sym = [q for q in ps if q is not p]


def stage(p, istg, sidx=0, dstg=None):
    p.st.update(istg=istg, sidx=sidx, sqor=istg, sepI=istg, dstg=istg if dstg is None else dstg)


def ship(fwd, gear=True):
    f = P(fwd); a = P('ITS_ShipAft'); f.put(a, 'bottom', 'top')
    sl = [a.put(P('SEP_26_R3_SL_C'), f'sl{i}', 'top') for i in (1, 2, 3)]; sym(sl)
    vac = [a.put(P('ITS_RVac'), f'vac{i}', 'top') for i in range(1, 7)]
    sym(vac[0::2]); sym(vac[1::2])
    for i, e in enumerate(sl + vac):
        stage(e, 0, i)
    if gear and os.path.exists(os.path.join(MU, 'ITS_Leg.json')):
        sym([a.put(P('ITS_Leg'), f'leg{i}', 'mount', yaw(-az)) for i, az in zip((1, 2, 3), (0, 120, 240))])
    if fwd == 'ITS_FwdCargo' and os.path.exists(os.path.join(MU, 'ITS_CargoBoom.json')):
        b = f.put(P('ITS_CargoBoom'), 'crane', 'top', yaw(-L.CR_AZ)); h = b.put(P('ITS_CargoHoist'), 'hoist', 'top'); h.put(P('ITS_CargoPlatform'), 'platform', 'top')
    if gear and os.path.exists(os.path.join(MU, 'ITS_FanArray.json')):
        sym([a.put(P('ITS_FanArray'), f'fan{i}', 'mount', yaw(-az)) for i, az in zip((1, 2), L.FAN_AZ)])
    return f, a


def yaw(deg):
    """Azimuth 0 is Blender -Y = Unity -Z; a Blender rotation of +az about +Z is a Unity rotation of -az about +Y."""
    t = math.radians(deg) / 2
    return (0, math.sin(t), 0, math.cos(t))


def booster(a):
    b = P('ITS_Booster'); a.put(b, 'bottom', 'top')
    rs = [b.put(P(n), n[4:].lower(), 'top') for n in ('ITS_Ring21', 'ITS_Ring14', 'ITS_Ring7')]
    for i, r in enumerate(rs):
        stage(r, 2, i)
    stage(b, 1, 0)
    if os.path.exists(os.path.join(MU, 'ITS_GridFin.json')):
        sym([b.put(P('ITS_GridFin'), f'fin{i + 1}', 'mount', yaw(-az)) for i, az in enumerate(L.GF_AZ)])
    return b


def write(title, root, desc, stages):
    o = [f'ship = {title}', 'version = 1.12.5', f'description = {desc}', 'type = VAB', 'size = 12,80,12', 'steamPublishedFileId = 0',
         'persistentId = %d' % (1500000000 + sum(map(ord, title)) * 7919 % 400000000), 'rot = 0,0,0,0', 'missionFlag = Squad/Flags/default', 'vesselType = Ship', 'OverrideDefault = False,False,False,False',
         'OverrideActionControl = 0,0,0,0', 'OverrideAxisControl = 0,0,0,0', 'OverrideGroupNames = ,,,']
    low = min(p.pos[1] for p in root.walk())
    Y = 30 - low if low < 0 else 15
    n = 0
    for p in root.walk():
        n += 1
        pos = (p.pos[0], p.pos[1] + Y, p.pos[2])
        if p.parent:
            inv = (-p.parent.rot[0], -p.parent.rot[1], -p.parent.rot[2], p.parent.rot[3])
            ap = qrot(inv, tuple(p.pos[i] - p.parent.pos[i] for i in range(3))); ar = p.lrot
        else:
            ap, ar = pos, (0, 0, 0, 1)
        c = lambda v: ','.join('%.7g' % x for x in v)
        o += ['PART', '{', f'\tpart = {p.id}', '\tpartName = Part', f'\tpersistentId = {int(p.id.split("_")[-1]) - 2600000000}', f'\tpos = {c(pos)}', '\tattPos = 0,0,0', f'\tattPos0 = {c(ap)}',
              f'\trot = {c(p.rot)}', f'\tattRot = 0,0,0,1', f'\tattRot0 = {c(ar)}', '\tmir = 1,1,1', '\tsymMethod = Radial', '\tautostrutMode = Off' if not p.parent or p.kids or p.part.startswith('ITS_Cargo') else '\tautostrutMode = Grandparent', '\trigidAttachment = False',
              f'\tistg = {p.st["istg"]}', '\tresPri = 0', f'\tdstg = {p.st["dstg"]}', f'\tsidx = {p.st["sidx"]}', f'\tsqor = {p.st["sqor"]}', f'\tsepI = {p.st["sepI"]}', '\tattm = 0', '\tsameVesselCollision = False', '\tmodCost = 0', '\tmodMass = 0', '\tmodSize = 0,0,0']
        o += [f'\tlink = {k.id}' for k in p.kids] + [f'\tsym = {k.id}' for k in p.sym] + [f'\tattN = {a}' for a in p.att]
        o += ['\tEVENTS', '\t{', '\t}', '\tACTIONS', '\t{', '\t}', '\tPARTDATA', '\t{', '\t}', '}']
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, title + '.craft'), 'w').write('\n'.join(o) + '\n')
    print('CRAFT', title, n, 'parts')


if __name__ == '__main__':
    for fwd, nm in (('ITS_FwdCrew', 'ITS Crew'), ('ITS_FwdCargo', 'ITS Cargo'), ('ITS_FwdTanker', 'ITS Tanker')):
        if not os.path.exists(os.path.join(MU, fwd + '.json')):
            continue
        f, a = ship(fwd); booster(a)
        write(nm, f, 'Stage 1: all three booster rings. Stage 2: separation. Stage 3: ship engines.', 3)

"""Lays the built mod (claude/hls layout: GameData/StarshipThingyMabobsAndSuch) over a release branch's GameData (main's layout, from
Recoleto's reorganisation: Assets/, Parts/<group>/, Patches/). Every file goes where the release already keeps it; new models and
textures go to Assets/, new patches to Patches/. Cfg paths into the old model folders become Assets/. Files the mod no longer has are
removed, except Recoleto's own: the Robotics split of SEP_CW_Parts.cfg, the @thumbs and the 1-byte `test` placeholders.
usage: python3 release_convert.py <src mod folder> <release GameData> [--dry] [-v]"""
import os, sys, re, shutil, collections
src, rel = sys.argv[1:3]; dry = '--dry' in sys.argv; verbose = '-v' in sys.argv
SKIP = {'SEP_CW_Parts.cfg'}                 # Recoleto split it into Parts/Robotics/SEP_CW_{Boom,Hoist,Platform}.cfg
KEEP = lambda d: d.startswith(('Parts/@thumbs/', 'Parts/Robotics/SEP_CW_')) or os.path.basename(d) == 'test'
where = collections.defaultdict(list)
for dp, dn, fn in os.walk(rel):
    for f in fn: where[f].append(os.path.relpath(os.path.join(dp, f), rel))
fix = lambda t: re.sub(r'StarshipThingyMabobsAndSuch/(ITS/Parts|Parts)/', 'StarshipThingyMabobsAndSuch/Assets/', t)
out = collections.Counter(); seen = set()
for dp, dn, fn in os.walk(src):
    r0 = os.path.relpath(dp, src)
    if r0.split(os.sep)[0] == 'docs': continue
    for f in fn:
        seen.add(f)
        if f in SKIP: continue
        s_ = os.path.join(dp, f); ex = where.get(f, [])
        if len(ex) > 1: ex = [e for e in ex if e.startswith('Patches' if 'Patches' in r0 else 'Parts')]
        if ex: d = ex[0]; kind = 'same'
        elif f.endswith(('.mu', '.dds', '.png')): d = os.path.join('Assets', f); kind = 'new asset'
        elif f.endswith('.cfg') and 'Patches' in r0: d = os.path.join('Patches', f); kind = 'new patch'
        else: print('UNPLACED', os.path.join(r0, f)); continue
        dst = os.path.join(rel, d)
        if f.endswith('.cfg'):
            t = fix(open(s_, encoding='utf-8', errors='surrogateescape').read())
            old = open(dst, encoding='utf-8', errors='surrogateescape').read() if os.path.exists(dst) else None
            st = 'unchanged' if old == t else ('changed' if old is not None else 'added')
            if not dry: open(dst, 'w', encoding='utf-8', errors='surrogateescape').write(t)
        else:
            st = 'unchanged' if os.path.exists(dst) and open(dst, 'rb').read() == open(s_, 'rb').read() else ('changed' if os.path.exists(dst) else 'added')
            if not dry: shutil.copyfile(s_, dst)
        out[(kind, st)] += 1
        if st != 'unchanged' and verbose: print(f'  {st:9s} {d}')
for f, ds in where.items():
    for d in ds:
        if f not in seen and not KEEP(d):
            out[('gone', 'removed')] += 1; print(f'  removed   {d}')
            if not dry: os.remove(os.path.join(rel, d))
print(dict(out))

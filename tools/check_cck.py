"""Every part in the package must be in STMS_CCK.cfg and the other way round. usage: check_cck.py <GameData/mod>"""
import glob, re, sys
t = lambda f: open(f, errors='replace').read(); fs = glob.glob(sys.argv[1] + '/**/*.cfg', recursive=True)
have = {n for f in fs for n in re.findall(r'^PART\s*\{\s*name\s*=\s*(\S+)', re.sub(r'//.*', '', t(f)), re.M)} | {n for f in fs for n in re.findall(r'^\+PART\[[^\n]*\s*\{\s*@name\s*=\s*(\S+)', t(f), re.M)}
listed = set(re.search(r'@PART\[([^\]]+)\]', t([f for f in fs if f.endswith('STMS_CCK.cfg')][0])).group(1).split('|'))
print('cck: %d parts' % len(have), 'missing', sorted(have - listed), 'unknown', sorted(listed - have)); sys.exit(have != listed)

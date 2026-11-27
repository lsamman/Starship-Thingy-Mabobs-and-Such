"""Milestone photos: loads a craft file (or single .mu files) with real textures, SEP's engines included, and renders it.
usage: blender -b -P photo.py -- out.png [--res WxH] [--view az,el,dist,tx,ty,tz] [--sun az,el] [--lens mm] [--sky day|space|studio]
       [--only part,part] [--hide name] [--pose part:clip[@frame]] [--mirror] [--livery Carbon] x.craft | part.mu[@x,y,z,yaw] ...
--livery: the B9 subtype whose TEXTURE swaps to show, read from each part's build/cfg/<part>.cfg (as B9 applies them).
A .mu path outside build/mu (SEP's nosecone, a v3 kit) is shown as it is, with --hide applied to it."""
import bpy, sys, os, math, re, glob, addon_utils
import numpy as np
from mathutils import Vector, Matrix, Quaternion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L
addon_utils.enable('io_object_mu', default_set=True)
a = sys.argv[sys.argv.index('--') + 1:]
out = a.pop(0); opt = dict(res='1400x1000', view='25,8,60,0,0,0', sun='60,35', lens='60', sky='studio', only='', hide='', pose='', samples='48', ortho='', livery='', tilt='0', extra='', fromcam='')
files = []
while a:
    x = a.pop(0)
    if x.startswith('--'): opt[x[2:]] = a.pop(0)
    else: files.append(x)
SEP = os.path.join(os.environ.get('KSP_DIR') or os.path.expanduser('~/.local/share/Steam/steamapps/common/Kerbal Space Program'), 'GameData/StarshipExpansionProject/Assets/BL3/SEP_26_RAPTOR_3.mu')
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
imgs, nimg = {}, {}


def load_tex(dirn, name):
    base = name.rsplit('.', 1)[0]
    for d_ in ((os.path.dirname(SEP),) if name.startswith('SEP_B3') else ()) + (dirn, os.path.join(dirn, '..', 'tex'), os.path.join(HERE, 'build/tex'), os.path.join(HERE, '../v3/build/tex')):
        for ext in ('.dds', '.png', '.DDS', '.tga'):
            p = os.path.join(d_, base + ext)
            if os.path.exists(p):
                if p not in imgs:
                    imgs[p] = bpy.data.images.load(p); imgs[p].alpha_mode = 'CHANNEL_PACKED'
                return imgs[p], ext
    return None, None


def nimage(im):
    if im.name in nimg: return nimg[im.name]
    im.colorspace_settings.name = 'Non-Color'
    w, h = im.size; px = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    nx = px[..., 3] * 2 - 1; ny = px[..., 1] * 2 - 1
    if abs(px[..., 0].mean() - 1) > .1: nx = px[..., 0] * 2 - 1
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    new = bpy.data.images.new(im.name + '_n', w, h); new.colorspace_settings.name = 'Non-Color'
    new.pixels.foreach_set(np.dstack([nx * .5 + .5, ny * .5 + .5, nz, np.ones_like(nz)]).ravel()); new.pack()
    nimg[im.name] = new
    return new


def swaps(part):
    """{currentTexture: texture} for the --livery subtype in the part's generated cfg."""
    p = os.path.join(HERE, 'build/cfg', part + '.cfg')
    if not opt['livery'] or not os.path.exists(p): return {}
    ls = [l.strip() for l in open(p)]; out = {}; depth = 0; sub = None; t = {}
    for i, l in enumerate(ls):
        if l == '{': depth += 1; continue
        if l == '}':
            if depth == sub: sub = None
            depth -= 1; continue
        if l == 'SUBTYPE' and i + 2 < len(ls) and ls[i + 2] == 'name = ' + opt['livery']: sub = depth + 1
        if sub is not None:
            k, _, v = l.partition(' = ')
            if k in ('texture', 'currentTexture'): t[k] = v
            if len(t) == 2: out[t['currentTexture']] = t['texture'].rsplit('/', 1)[-1]; t = {}
    return out


def setup(m, dirn, swap={}):
    if m is None or m.get('_d'): return
    m['_d'] = 1; mp = m.mumatprop
    tx = {t.name: t.tex for t in mp.texture.properties}; cols = {t.name: t.value for t in mp.color.properties}
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    sh = nt.nodes.new('ShaderNodeBsdfPrincipled'); ou = nt.nodes.new('ShaderNodeOutputMaterial')
    sh.inputs['Base Color'].default_value = (.16, .16, .17, 1); sh.inputs['Roughness'].default_value = .5; sh.inputs['Specular'].default_value = .45
    def coord(ext):
        n = nt.nodes.new('ShaderNodeUVMap')
        if ext.lower() == '.dds':
            k = nt.nodes.new('ShaderNodeMapping'); k.inputs['Scale'].default_value = (1, -1, 1); nt.links.new(n.outputs[0], k.inputs[0]); return k.outputs[0]
        return n.outputs[0]
    def img(key, f=lambda i: i):
        if key not in tx: return None
        b_ = tx[key].rsplit('.', 1)[0]
        im, ext = load_tex(dirn, swap.get(b_, b_) if key == '_MainTex' else tx[key])
        if not im: return None
        it = nt.nodes.new('ShaderNodeTexImage'); it.image = f(im); nt.links.new(coord(ext), it.inputs[0]); return it
    it = img('_MainTex')
    if it:
        nt.links.new(it.outputs[0], sh.inputs['Base Color'])
        inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = .9; nt.links.new(it.outputs[1], inv.inputs[1]); nt.links.new(inv.outputs[0], sh.inputs['Roughness'])
    it = img('_BumpMap', nimage)
    if it:
        nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(it.outputs[0], nm.inputs['Color']); nt.links.new(nm.outputs[0], sh.inputs['Normal'])
    it = img('_Emissive')
    if it and opt.get('lit'):
        nt.links.new(it.outputs[0], sh.inputs['Emission']); sh.inputs['Emission Strength'].default_value = float(opt['lit'])
    if 'Translucent' in mp.shaderName:
        sh.inputs['Alpha'].default_value = .35
    nt.links.new(sh.outputs[0], ou.inputs[0])


colls = {}


def base(o): return o.name.split('∧')[0].split('.')[0]


def model(path, skip=(), clip=None):
    key = (path, tuple(skip), clip)
    if key in colls: return colls[key]
    before = set(bpy.data.objects); bpy.ops.import_object.ksp_mu(filepath=path); bpy.context.view_layer.update()
    new = [o for o in bpy.data.objects if o not in before]
    if clip:
        clip, _, at = clip.partition('@')            # clip@frame: a pose part way through
        for o in new:
            ad = o.animation_data
            if not ad: continue
            for tr in list(ad.nla_tracks):
                for st in tr.strips:
                    act = st.action
                    for tr2 in list(ad.nla_tracks): tr2.mute = True
                    if tr.name.split('.')[0] == clip or act.name.split('.')[0] == clip or clip == '*':
                        ad.action = act; sc.frame_set(int(at) if at else int(act.frame_range[1]))
        bpy.context.view_layer.update()
    for o in new:
        if base(o) == 'tilt' and float(opt['tilt']): o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = o.rotation_quaternion @ Quaternion((1, 0, 0), math.radians(float(opt['tilt'])))      # arrays hanging down
    for o in new:                                    # freeze the pose, so another part's clip can't move it
        if o.animation_data:
            m = o.matrix_basis.copy(); o.animation_data_clear(); o.matrix_basis = m
    sc.frame_set(0); bpy.context.view_layer.update()
    def under(o):
        while o:
            if base(o) in skip: return True
            o = o.parent
        return False
    c = bpy.data.collections.new(os.path.basename(path)); colls[key] = c
    d = os.path.dirname(path); sw = swaps(os.path.basename(path)[:-3])
    for o in new:
        if o.type in ('CAMERA', 'LIGHT'): bpy.data.objects.remove(o); continue
        for cc in list(o.users_collection): cc.objects.unlink(o)
        if o.type != 'MESH' or o.muproperties.collider != 'MU_COL_NONE' or 'COLLIDER' in o.name or under(o):
            if o.type == 'MESH': o.hide_render = True
        else:
            for s in o.material_slots: setup(s.material, d, sw)
        c.objects.link(o)
    return c


PLACED = {}
def put(path, M, skip=(), clip=None):
    e = bpy.data.objects.new('i', None); e.instance_type = 'COLLECTION'; e.instance_collection = model(path, skip, clip); e.matrix_world = M
    sc.collection.objects.link(e); PLACED.setdefault(os.path.basename(path)[:-3], []).append(e)


# SEP's parts by their cfg's MODEL (the part names and the .mu names differ), and models our patches add to parts (--extra Part:Model,...)
SEPMU = {}
for f_ in glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(SEP))), 'Parts', '**', '*.cfg'), recursive=True):
    t_ = open(f_, errors='replace').read(); n_ = re.search(r'^\s*name\s*=\s*(\S+)', t_, re.M); m_ = re.search(r'model\s*=\s*(StarshipExpansionProject/\S+)', t_)
    if n_ and m_: SEPMU[n_.group(1)] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(SEP))), '..', m_.group(1) + '.mu')
EXTRA = {}
for x_ in opt['extra'].split(','):
    if x_: k_, v_ = x_.split(':'); EXTRA.setdefault(k_, []).append(v_)
def kitpath(n):
    for d_ in (os.path.join(HERE, 'build/mu'), os.path.join(HERE, '../v3/build/mu')):
        if os.path.exists(os.path.join(d_, n + '.mu')): return os.path.join(d_, n + '.mu')


poses = dict(p.split(':') for p in opt['pose'].split(',') if p)
hide = tuple(h for h in opt['hide'].split(',') if h); only = [h for h in opt['only'].split(',') if h]
BST = ('R3Vac_Stuff', 'R3C_Stuff', 'R3_Gimballing_Stuff'); CEN = ('R3Vac_Stuff',); VAC = ('R3_SL_Stuff', 'R3C_Stuff', 'R3_Gimballing_Stuff')


def place(part, M):
    if only and part not in only: return
    if (part in L.RINGS or part == 'ITS_RVac' or part.startswith('SEP_26')) and not os.path.exists(SEP): return   # no SEP here: no engines in the picture
    if part in L.RINGS:
        n, r, a0 = L.RINGS[part]
        for rr, az in [(r, a0 + 360 * i / n) for i in range(n)] + ([(0, 0)] if part == 'ITS_Ring7' else []):
            t = math.radians(az)
            put(SEP, M @ Matrix.Translation((rr * math.sin(t), -rr * math.cos(t), -L.R3_TOP)) @ Matrix.Rotation(math.radians(az + 180), 4, 'Z'), CEN if part == 'ITS_Ring7' else BST)
    elif part == 'ITS_RVac': put(SEP, M @ Matrix.Scale(L.RV_SCALE, 4), VAC)
    elif part == 'SEP_26_R3_VAC': put(SEP, M, VAC)
    elif part.startswith('SEP_26_R3'): put(SEP, M, CEN)
    elif part.startswith('SEP_26'): put(SEPMU.get(part) if part in SEPMU and os.path.exists(SEPMU[part]) else SEP.replace('SEP_26_RAPTOR_3', part), M, hide)
    else: put(os.path.join(HERE, 'build/mu', part + '.mu'), M, hide, poses.get(part))
    for k_ in EXTRA.get(part, []): put(kitpath(k_), M, hide)


for f in files:
    if '.craft' in f:
        f, _, dx = f.partition('@'); dx = float(dx or 0)
        for b in open(f).read().split('\nPART\n')[1:]:
            g = lambda k: re.search(r'^\t%s = (.*)$' % k, b, re.M).group(1)
            p = [float(v) for v in g('pos').split(',')]; q = [float(v) for v in g('rot').split(',')]
            part = g('part').rsplit('_', 1)[0].replace('.', '_')
            place(part, Matrix.Translation((p[0] + dx, p[2], p[1])) @ Quaternion((q[3], -q[0], -q[2], -q[1])).to_matrix().to_4x4())
    else:
        pos = (0, 0, 0); yaw = 0
        if '@' in f:
            f, t = f.split('@'); t = [float(v) for v in t.split(',')]; pos = t[:3]; yaw = t[3] if len(t) > 3 else 0
        M = Matrix.Translation(pos) @ Matrix.Rotation(math.radians(yaw), 4, 'Z')
        if os.path.isfile(f) and os.path.dirname(os.path.abspath(f)) != os.path.abspath(os.path.join(HERE, 'build/mu')):
            put(os.path.abspath(f), M, hide)       # any other .mu as it is, e.g. SEP's Block 3 nosecone or a v3 window kit
        else:
            place(os.path.basename(f)[:-3], M)

sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(opt['samples']); sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4
sc.render.resolution_x, sc.render.resolution_y = [int(v) for v in opt['res'].split('x')]
sc.view_settings.view_transform = 'Filmic'; sc.view_settings.look = 'Medium High Contrast'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; nt = w.node_tree; bg = nt.nodes['Background']
tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); rp = nt.nodes.new('ShaderNodeValToRGB'); mr = nt.nodes.new('ShaderNodeMapRange')
mr.inputs[1].default_value = -1; nt.links.new(tc.outputs['Generated'], sp.inputs[0]); nt.links.new(sp.outputs[2], mr.inputs[0]); nt.links.new(mr.outputs[0], rp.inputs[0]); nt.links.new(rp.outputs[0], bg.inputs[0])
sky = {'studio': ([(0, (.03, .035, .045)), (.45, (.12, .14, .17)), (.52, (.30, .34, .40)), (1, (.12, .16, .24))], 1.0, 4.0),
       'day': ([(0, (.16, .13, .10)), (.485, (.30, .25, .20)), (.5, (.75, .68, .60)), (.62, (.42, .52, .66)), (1, (.12, .22, .42))], .9, 4.2),
       'space': ([(0, (.05, .10, .18)), (.35, (.02, .04, .07)), (.5, (.004, .005, .007)), (1, (.002, .002, .003))], 1.0, 5.0)}[opt['sky']]
el = rp.color_ramp.elements
while len(el) > 1: el.remove(el[-1])
for i, (p, c) in enumerate(sky[0]):
    e = el[0] if i == 0 else el.new(p)
    e.position = p; e.color = (*c, 1)
bg.inputs[1].default_value = sky[1]
def light(az, elv, energy, ang=1.0):
    d = bpy.data.lights.new('s', 'SUN'); d.energy = energy; d.angle = math.radians(ang); o = bpy.data.objects.new('s', d); sc.collection.objects.link(o)
    t, e = math.radians(az), math.radians(elv)
    v = Vector((math.cos(e) * math.sin(t), -math.cos(e) * math.cos(t), math.sin(e))); o.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
saz, sel = [float(v) for v in opt['sun'].split(',')]
light(saz, sel, sky[2]); light(saz - 130, 10, .7, 20)
v = [float(x) for x in opt['view'].split(',')]; az, elv, dist = v[:3]; tgt = Vector(v[3:6] if len(v) > 5 else (0, 0, 0))
d = Vector((math.cos(math.radians(elv)) * math.sin(math.radians(az)), -math.cos(math.radians(elv)) * math.cos(math.radians(az)), math.sin(math.radians(elv))))
cd = bpy.data.cameras.new('c'); cd.lens = float(opt['lens']); cd.clip_end = 3000; cd.clip_start = .05
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = tgt + d * dist; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
if opt['fromcam']:                                   # --fromcam Model:transform: the view from one of our camera transforms (+Y looks, +Z up)
    k_, c_ = opt['fromcam'].split(':'); e_ = PLACED[k_][0]; o_ = next(o for o in e_.instance_collection.objects if base(o) == c_)
    Mw = e_.matrix_world @ o_.matrix_world; R_ = Mw.to_3x3().normalized(); Mc = Matrix((R_.col[0], R_.col[2], -R_.col[1])).transposed().to_4x4(); Mc.translation = Mw.translation
    cam.matrix_world = Mc; print('FROMCAM', tuple(round(x, 2) for x in Mw.translation), 'part at', tuple(round(x, 2) for x in e_.matrix_world.translation), 'looks', tuple(round(x, 2) for x in R_.col[1]))
if opt['ortho']: cd.type = 'ORTHO'; cd.ortho_scale = float(opt['ortho'])
sc.render.filepath = os.path.abspath(out); sc.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)

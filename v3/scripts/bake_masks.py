"""Bare-metal masks for the expendable V3 core. The hull under the tiles is painted black in the ambient occlusion
channel of SEP's masks because it never shows, so with the tiles gone the belly would render nearly black. This
whitens exactly the texels the windward hull triangles use and leaves the rest of each sheet as SEP made it.
usage: python3 -I bake_masks.py <SEP dir> <uvt.npz> <outdir>"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

sep, npz, out = sys.argv[1:4]
WINDWARD_Y = -0.6       # hull faces with y above this were under tiles or the ablative strip
d = np.load(npz)
sheets = {}
for key in d.files:
    sheets.setdefault(key.split('Ship_')[1].split('_BASE')[0], []).append(d[key])
os.makedirs(out, exist_ok=True)
for n, parts in sorted(sheets.items()):
    src = f'{sep}/Assets/BL3/SEP_B3_Ship_{n}_MASK.dds'
    im = np.array(Image.open(src).convert('RGBA'))
    H = im.shape[0]
    mask = Image.new('L', (H, H), 0); dr = ImageDraw.Draw(mask)
    ntri = 0
    for R in parts:
        R = R[((R[:, 3] * R[:, 0] + R[:, 4] * R[:, 1]) > 0) & (R[:, 1] > WINDWARD_Y)]
        for t in R:
            # DDS rows run with v: row 0 is v = 0, checked against where the black hull rows fall
            dr.polygon([(u * H, v * H) for u, v in t[6:12].reshape(3, 2)], fill=255)
            ntri += 1
    m = np.asarray(mask) > 0
    before = im[..., 1][m].mean() / 255
    has_b = im[..., 2].max() > 0
    im[..., 1][m] = 255
    if has_b:
        im[..., 2][m] = 255
    base = np.asarray(Image.open(f'{sep}/Assets/BL3/SEP_B3_Ship_{n}_BASE.dds').convert('RGB'), dtype=np.float32) / 255
    bm = np.asarray(mask.resize((base.shape[1], base.shape[0]), Image.NEAREST)) > 0
    red = (base[..., 0] - (base[..., 1] + base[..., 2]) / 2)[bm]
    lum = base.mean(-1)[bm]
    print(f'{n}: {ntri} tris, {100 * m.mean():.1f}% of sheet, AO {before:.3f} -> 1.0; colour under them: reddish {100 * np.mean(red > .04):.2f}% dark {100 * np.mean(lum < .3):.2f}%')
    png = os.path.join(out, f'SEP_B3_Ship_{n}_MASK_BARE.png')
    Image.fromarray(im[..., :3], 'RGB').save(png, compress_level=1)
    subprocess.run(['magick', png, '-define', 'dds:compression=dxt1', '-define', 'dds:mipmaps=11', png[:-4] + '.dds'], check=True)
    # read it back: format, size, and that the whitened texels survived compression
    r = np.asarray(Image.open(png[:-4] + '.dds').convert('RGB'))
    print('   readback', r.shape, 'AO over patched texels %.3f, elsewhere changed %.4f' % (r[..., 1][m].mean() / 255, np.abs(r[..., 1][~m].astype(int) - im[..., 1][~m].astype(int)).mean() / 255), os.path.getsize(png[:-4] + '.dds'))
    os.remove(png)

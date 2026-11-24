"""KSP's EVA hatch check (FlightEVA.HatchIsObstructed) on our own colliders, doors open: a ray from .5 m behind each airlock, along
the line from the part's origin, 1.5 m past it. usage: blender -b -P check_airlocks.py -- <mu>[:clip] ..."""
import bpy, sys, os, addon_utils
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
addon_utils.enable('io_object_mu', default_set=True); bad = 0
for arg in sys.argv[sys.argv.index('--') + 1:]:
    f, _, clip = arg.partition(':'); [bpy.data.objects.remove(o) for o in list(bpy.data.objects)]; bpy.ops.import_object.ksp_mu(filepath=f); obs = list(bpy.data.objects); end = 0
    for o in obs:
        ad = o.animation_data
        for tr in list(ad.nla_tracks) if ad else []:
            tr.mute = True; act = tr.strips[0].action
            if clip and clip in (act.name.split('.')[0], tr.name.split('.')[0]): ad.action = act; end = max(end, int(act.frame_range[1]))
    for fr in {0, end}:
        bpy.context.scene.frame_set(fr); bpy.context.view_layer.update()
        hulls = [(o.name, BVHTree.FromPolygons([o.matrix_world @ v.co for v in o.data.vertices], [list(p.vertices) for p in o.data.polygons])) for o in obs if o.type == 'MESH' and o.muproperties.collider != 'MU_COL_NONE' and not o.muproperties.isTrigger]
        for o in [o for o in obs if o.muproperties.tag == 'Airlock']:
            p = o.matrix_world.translation; d = p.normalized(); s = p - d * .5; hit = [n for n, t in hulls if t.ray_cast(s, d, 2.0)[0] is not None]
            print('  ', os.path.basename(f), o.name, 'closed' if fr == 0 and end else 'open', 'blocked by ' + ', '.join(hit) if hit else 'clear', '(%d colliders)' % len(hulls)); bad += bool(hit) and fr == end
print('check_airlocks:', bad, 'obstructed')

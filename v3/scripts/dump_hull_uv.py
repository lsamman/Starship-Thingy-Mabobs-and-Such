"""Dumps the outer hull triangles of the V3 core with their UVs, for bake_masks.py.
usage: blender -b -P dump_hull_uv.py -- <SEP dir> <outdir>"""
import bpy,sys,addon_utils
import numpy as np
addon_utils.enable("io_object_mu")
a=sys.argv[sys.argv.index('--')+1:]; G,S=a
bpy.ops.import_object.ksp_mu(filepath=G+'/Assets/BL3/SEP_26_SHIP_CORE.mu'); bpy.context.view_layer.update()
out={}
for name in ('Cylinder1','Rings_4','Rings_3','Rings_1','WeldLines'):
    o=[x for x in bpy.data.objects if x.name.split('∧')[0]==name and x.type=='MESH'][0]
    m=o.data.materials[0]; tn=[p.tex for p in m.mumatprop.texture.properties if p.name=='_MainTex'][0]
    me=o.data; uv=me.uv_layers[0].data; mw=o.matrix_world; R=[]
    for p in me.polygons:
        c=mw@p.center; n=(mw.to_3x3()@p.normal).normalized(); ids=list(p.loop_indices)
        for k in range(1,len(ids)-1):
            t=[uv[ids[0]].uv,uv[ids[k]].uv,uv[ids[k+1]].uv]
            R.append((c.x,c.y,c.z,n.x,n.y,n.z,*t[0],*t[1],*t[2]))
    out[name+'|'+tn]=np.array(R)
np.savez(S+'/uvt.npz',**out)

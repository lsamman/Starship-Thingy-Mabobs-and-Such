#!/bin/bash
# interior photo: ./ri.sh name STMS_IVA_HLS px,py,pz,tx,ty,tz[,lens]   (camera in the part's frame)
cd "$(dirname "$0")"; G="${KSP_DIR:-$HOME/.local/share/Steam/steamapps/common/Kerbal Space Program Modded SOL}/GameData"
nice -n 15 flock build/.render.lock "${BLENDER:-$HOME/Applications/blender-3.6/blender}" -b --factory-startup -P scripts/render_iva.py -- build/photos/$1.png build/iva/$2.cfg "$G" --cam $3 --res 1200x800 2>&1 | grep -E 'MISSING|Error|Saved|line'

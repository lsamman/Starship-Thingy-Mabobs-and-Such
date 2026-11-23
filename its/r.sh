#!/bin/bash
# quick render: ./r.sh out "az,el,dist[,x,y,z]" part.mu[@x,y,z] ...
cd "$(dirname "$0")"; o=$1; v=$2; shift 2
flock build/.render.lock "${BLENDER:-$HOME/Applications/blender-3.6/blender}" -b --factory-startup -P scripts/render_mu.py -- build/r/$o.png --res 1000x1000 --samples 32 --view "$v" "$@" 2>&1 | grep -E 'Error|NOTEX|BBOX'

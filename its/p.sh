#!/bin/bash
# photo: ./p.sh name [photo.py options] files...
cd "$(dirname "$0")"; mkdir -p build/photos; n=$1; shift
nice -n 15 flock build/.render.lock ~/Applications/blender-3.6/blender -b --factory-startup --python-exit-code 1 -P scripts/photo.py -- build/photos/$n.png "$@" 2>&1 | grep -E 'Error|Traceback|line [0-9]+, in|Saved'

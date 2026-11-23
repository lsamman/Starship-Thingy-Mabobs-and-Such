#!/bin/bash
# build one or more parts: ./b.sh fwdcrew booster
cd "$(dirname "$0")"; export SHAB_TEX=build/tex
for n in "$@"; do ~/Applications/blender-3.6/blender -b --factory-startup --python-exit-code 1 -P scripts/build_$n.py -- build/mu 2>&1 | grep -E "EXPORT|FACING|rror|Traceback|File .*scripts|assert|^KeyError|^Value"; done

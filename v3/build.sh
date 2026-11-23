#!/bin/bash
# Parts, textures and patches for SEP's V3 ship. SKIP_MODELS=1 / SKIP_TEX=1 reuse the last build.
set -eo pipefail
cd "$(dirname "$0")"
B="$HOME/Applications/blender-3.6/blender"
SEP="$HOME/.local/share/Steam/steamapps/common/Kerbal Space Program Modded SOL/GameData/StarshipExpansionProject"
export SHAB_TEX=build/tex
mkdir -p build/mu build/tex
if [ -z "$SKIP_MODELS" ]; then
    for p in boom hoist platform; do
        "$B" -b --factory-startup --python-exit-code 1 -P scripts/build_$p.py -- build/mu 2>&1 | grep -E "EXPORT|FACING|Error|Traceback"
    done
fi
if [ -z "$SKIP_TEX" ]; then
    python3 -I scripts/tex_winch.py | tail -1
    "$B" -b --python-exit-code 1 -P scripts/dump_hull_uv.py -- "$SEP" build 2>&1 | grep -E "Traceback|Error" || true
    python3 -I scripts/bake_masks.py "$SEP" build/uvt.npz build/tex
fi
D=../GameData/StarshipThingyMabobsAndSuch
mkdir -p "$D/Parts" "$D/Patches" "$D/Textures"
cp build/mu/*.mu build/tex/sep_cw_*.dds cfg/*.cfg "$D/Parts/"
cp build/tex/*_MASK_BARE.dds "$D/Textures/"
cp patches/*.cfg "$D/Patches/"

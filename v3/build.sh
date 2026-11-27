#!/bin/bash
# Parts, textures and patches for SEP's V3 ship. SKIP_MODELS=1 / SKIP_TEX=1 reuse the last build.
set -eo pipefail
cd "$(dirname "$0")"
B="${BLENDER:-$HOME/Applications/blender-3.6/blender}"
SEP="${KSP_DIR:-$HOME/.local/share/Steam/steamapps/common/Kerbal Space Program}/GameData/StarshipExpansionProject"
export SHAB_TEX=build/tex
mkdir -p build/mu build/tex build/patches
if [ -z "$SKIP_MODELS" ]; then
    for p in boom hoist platform; do
        "$B" -b --factory-startup --python-exit-code 1 -P scripts/build_$p.py -- build/mu 2>&1 | grep -E "EXPORT|FACING|Error|Traceback"
    done
    for v in crew crewcargo; do     # Block 3 nose window kits
        "$B" -b --factory-startup --python-exit-code 1 -P scripts/build_nosekit.py -- build/mu $v 2>&1 | grep -E "EXPORT|FACING|KIT|Error|Traceback"
    done
    "$B" -b --factory-startup --python-exit-code 1 -P scripts/build_camkit.py -- build/mu 2>&1 | grep -E "EXPORT|Error|Traceback"      # hull cameras for SEP's ship and the noses
fi
if [ -z "$SKIP_MODELS" ] && [ -f "$SEP/Assets/BL3/SEP_26_SHIP_NOSECONE.mu" ]; then       # cut copies of SEP's nose, into the ITS build (they share its detail atlas)
    mkdir -p ../its/build/mu
    for v in crew crewcargo; do "$B" -b --factory-startup --python-exit-code 1 -P scripts/derive_nose.py -- "$SEP/Assets/BL3" ../its/build/mu $v 2>&1 | grep -E "EXPORT|FACING|Error|Traceback"; done
    "$B" -b --factory-startup --python-exit-code 1 -P scripts/derive_stringers.py -- "$SEP/Assets/BL3" ../its/build/mu 2>&1 | grep -E "EXPORT|Error|Traceback"     # the expendable core's windward stringers
fi
if [ -z "$SKIP_TEX" ]; then
    python3 -I scripts/tex_winch.py | tail -1
    python3 -I scripts/tex_nosekit.py | tail -2
    if [ -d "$SEP" ]; then
        "$B" -b --python-exit-code 1 -P scripts/dump_hull_uv.py -- "$SEP" build 2>&1 | grep -E "Traceback|Error" || true
        python3 -I scripts/bake_masks.py "$SEP" build/uvt.npz build/tex
    else
        echo "SEP not found: expendable masks not baked"
    fi
fi
python3 -I scripts/make_nose_cfg.py build/patches/STMS_B3_Noses.cfg
if [ -f "$SEP/Assets/BL3/SEP_26_SHIP_NOSECONE.mu" ]; then
    "$B" -b --factory-startup --python-exit-code 1 -P scripts/check_nose.py -- "$SEP" build/mu 2>&1 | grep -E "^ok|^FAIL|^  |check_nose|Error|Traceback"
else
    echo "SEP not found: nose window fit not checked"
fi
D=../GameData/StarshipThingyMabobsAndSuch
mkdir -p "$D/Parts" "$D/Patches" "$D/Textures"
cp build/mu/*.mu build/tex/sep_cw_*.dds build/tex/stms_b3_*.dds build/tex/stms_cam_*.dds cfg/*.cfg "$D/Parts/"
cp build/tex/*_MASK_BARE.dds "$D/Textures/" 2>/dev/null || echo "WARNING: no expendable masks, so this build is not complete; build it on the PC before deploying"
cp patches/*.cfg build/patches/*.cfg "$D/Patches/"

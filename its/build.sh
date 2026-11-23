#!/bin/bash
# The 2016 ITS parts. SKIP_TEX=1 reuses textures, SKIP_MODELS=1 reuses models,
# ONLY="booster leg" rebuilds just those models. 
set -eo pipefail
cd "$(dirname "$0")"
export SHAB_TEX=build/tex
mkdir -p build/mu build/tex build/patches build/cfg
if [ -z "$SKIP_MODELS" ]; then
    for s in scripts/build_*.py; do n=$(basename "$s" .py); n=${n#build_}
        if [ -n "$ONLY" ]; then case " $ONLY " in *" $n "*) ;; *) continue ;; esac; fi
        ./b.sh "$n"; done
fi
if [ -z "$SKIP_TEX" ]; then for t in scripts/tex_*.py; do python3 "$t" | tail -2; done; fi
python3 scripts/make_rings.py build/patches/ITS_Rings.cfg
python3 scripts/make_cfg.py build/mu build/cfg
D=../GameData/StarshipThingyMabobsAndSuch/ITS
rm -rf "$D"; mkdir -p "$D/Parts" "$D/Patches" "$D/Extras"
cp build/mu/*.mu build/tex/*.dds build/cfg/*.cfg "$D/Parts/"
cp build/patches/*.cfg patches/*.cfg "$D/Patches/"
cp extras/* "$D/Extras/"
python3 scripts/make_craft.py build/mu ../Ships/VAB

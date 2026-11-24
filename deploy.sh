#!/bin/sh
# Copies the mod into the Sol install and the ITS craft into default3. New parts appear on the next KSP start.
# The new copy is put in place first and checked; only then are the folders it replaces removed.
set -e
cd "$(dirname "$0")"
if pgrep -x "KSP.x86_64" >/dev/null || pgrep -x KSP_x64 >/dev/null || pgrep -x KSP_x64.exe >/dev/null; then echo "KSP is running; not deploying"; exit 1; fi
K="${KSP_DIR:-$HOME/.local/share/Steam/steamapps/common/Kerbal Space Program Modded SOL}"
N=StarshipThingyMabobsAndSuch
[ -f "GameData/$N/ITS/Parts/ITS_Booster.mu" ] && [ -f "GameData/$N/Parts/SEP_CW_Boom.mu" ] && [ -f "GameData/$N/Textures/SEP_B3_Ship_Core_5_MASK_BARE.dds" ] && [ -f "GameData/$N/ITS/Parts/STMS_B3_HullCrew.mu" ] || { echo "build is incomplete; not deploying"; exit 1; }
rm -rf "$K/$N.new"; cp -a "GameData/$N" "$K/$N.new"
diff -rq "GameData/$N" "$K/$N.new" || { echo "copy failed"; exit 1; }
rm -rf "$K/GameData/$N"; mv "$K/$N.new" "$K/GameData/$N"
for old in SEPExtras StarshipITS; do rm -rf "$K/GameData/$old"; done      # this mod's two former folders: same part names
mkdir -p "$K/saves/default3/Ships/VAB"; cp Ships/VAB/*.craft "$K/saves/default3/Ships/VAB/"
echo "deployed to $K/GameData/$N"

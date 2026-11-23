#!/bin/bash
# Builds both halves into GameData/StarshipThingyMabobsAndSuch. SKIP_MODELS=1 / SKIP_TEX=1 reuse the last build.
set -eo pipefail
cd "$(dirname "$0")"
rm -rf GameData/StarshipThingyMabobsAndSuch
./v3/build.sh
./its/build.sh
D=GameData/StarshipThingyMabobsAndSuch
cp README.md LICENSE "$D/"; mkdir -p "$D/docs"; cp docs/*.md "$D/docs/"
python3 its/scripts/lint.py "$D"

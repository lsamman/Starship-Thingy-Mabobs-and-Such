#!/bin/bash
# Compiles the plugin against a KSP install: ./build.sh <out dir>
set -e
cd "$(dirname "$0")"; M="${KSP_DIR:-$HOME/.local/share/Steam/steamapps/common/Kerbal Space Program}/KSP_x64_Data/Managed"; mkdir -p "$1"
N=(); [ -f "$M/netstandard.dll" ] && N=("-r:$M/netstandard.dll")      # Retooled (Unity 6) needs it, stock 1.12 has none
csc -nologo -target:library -optimize+ -nostdlib+ -noconfig -out:"$1/STMS.dll" "${N[@]}" "-r:$M/mscorlib.dll" "-r:$M/System.dll" "-r:$M/System.Core.dll" "-r:$M/Assembly-CSharp.dll" "-r:$M/UnityEngine.dll" "-r:$M/UnityEngine.CoreModule.dll" "-r:$M/UnityEngine.AnimationModule.dll" ModuleSTMSArrayTilt.cs ModuleSTMSCable.cs

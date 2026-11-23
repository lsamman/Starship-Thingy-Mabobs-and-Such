#!/bin/bash
# Sets up a machine without the PC's tools: Blender 3.6.23, io_object_mu with our exporter fix, Python packages.
# Then: source tools/env.sh && ./build_all.sh. Needs network access to download.blender.org and github.com.
set -eo pipefail
cd "$(dirname "$0")"; T="${TOOLS_DIR:-$HOME/ksp-tools}"; HERE="$PWD"
SUDO=""; [ "$(id -u)" = 0 ] || SUDO="sudo"
if command -v apt-get >/dev/null; then
    $SUDO apt-get update -qq || true
    $SUDO apt-get install -y -qq imagemagick fonts-dejavu-core curl xz-utils git patch util-linux libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libsm6 libxkbcommon0 libegl1 || true
fi
python3 -c "import numpy, PIL" 2>/dev/null || pip install -q numpy pillow || pip install -q --break-system-packages numpy pillow
mkdir -p "$T"; cd "$T"
if [ ! -x blender-3.6/blender ]; then
    curl -fsSL -o b.tar.xz https://download.blender.org/release/Blender3.6/blender-3.6.23-linux-x64.tar.xz
    echo "0e9a18af4d0060b825e9617e24a775f759e0f9f67271c062f3d53a539030af00  b.tar.xz" | sha256sum -c --quiet
    tar xf b.tar.xz; rm b.tar.xz; mv blender-3.6.23-linux-x64 blender-3.6
fi
A=blender-3.6/3.6/scripts/addons/io_object_mu
if [ ! -d "$A" ]; then
    git clone -q https://github.com/taniwha/io_object_mu "$A"; git -C "$A" checkout -q ff04234
    patch -s -p1 -d "$A" < "$HERE/io_object_mu.patch"
fi
# The scripts call ImageMagick 7's `magick`; distro packages often ship only 6's `convert`.
mkdir -p "$T/bin"
if ! command -v magick >/dev/null && command -v convert >/dev/null; then
    printf '#!/bin/sh\nexec convert "$@"\n' > "$T/bin/magick"; chmod +x "$T/bin/magick"
fi
cat > "$HERE/env.sh" <<X
export BLENDER="$T/blender-3.6/blender" IO_OBJECT_MU="$T/$A" PATH="$T/bin:\$PATH"
X
"$T/blender-3.6/blender" --version | head -1
echo "ready: source tools/env.sh"

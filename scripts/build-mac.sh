#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
APP_NAME="Image Restore Studio"
VERSION="0.3.0"
ARCH="$(uname -m)"
export MACOSX_DEPLOYMENT_TARGET=10.13
python3 -m pip install -r requirements-build.txt
python3 scripts/prepare-legacy.py
python3 src/entry.py --self-test
python3 -m PyInstaller --noconfirm --clean --windowed --onedir \
  --name "$APP_NAME" \
  --osx-bundle-identifier uk.co.imagerestorestudio.app \
  --hidden-import=PIL._tkinter_finder \
  --collect-submodules PIL \
  --target-architecture x86_64 \
  src/entry.py
APP="dist/$APP_NAME.app"
test -f "$APP/Contents/MacOS/$APP_NAME"
"$APP/Contents/MacOS/$APP_NAME" --self-test
echo "Mach-O deployment load command:"
otool -l "$APP/Contents/MacOS/$APP_NAME" | grep -A5 -E 'LC_BUILD_VERSION|LC_VERSION_MIN_MACOSX' | head -15 || true
mkdir -p stage/Applications
ditto "$APP" "stage/Applications/$APP_NAME.app"
pkgbuild --root stage --install-location / \
  --identifier uk.co.imagerestorestudio.installer --version "$VERSION" \
  "Image-Restore-Studio-${VERSION}-Intel.pkg"
ls -lh Image-Restore-Studio-*.pkg

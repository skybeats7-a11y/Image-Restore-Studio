#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
APP_NAME="Image Restore Studio"
VERSION="0.2.0"
ARCH="$(uname -m)"
python3 -m pip install -r requirements-build.txt
python3 - <<'PY'
import tkinter, PIL, cv2, numpy
print("Dependencies loaded:", PIL.__version__, cv2.__version__, numpy.__version__)
PY
python3 -m PyInstaller --noconfirm --clean --windowed --onedir   --name "$APP_NAME" --collect-all cv2   --osx-bundle-identifier uk.co.imagerestorestudio.app   src/app.py
APP="dist/$APP_NAME.app"
test -f "$APP/Contents/MacOS/$APP_NAME"
mkdir -p stage/Applications
cp -R "$APP" stage/Applications/
pkgbuild --root stage --install-location /   --identifier uk.co.imagerestorestudio.installer --version "$VERSION"   "Image-Restore-Studio-${VERSION}-${ARCH}.pkg"
ls -lh Image-Restore-Studio-*.pkg

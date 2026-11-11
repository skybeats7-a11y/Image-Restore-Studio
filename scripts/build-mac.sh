#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
APP_NAME="Image Restore Studio"
VERSION="0.5.0"
export MACOSX_DEPLOYMENT_TARGET=10.13
python3 -m pip install -r requirements-build.txt
python3 scripts/prepare-legacy.py
python3 scripts/upgrade-v04.py
python3 scripts/upgrade-v05.py
python3 -m py_compile src/cloud_premium.py src/app.py
python3 src/entry.py --self-test

# Official Real-ESRGAN portable Mac build including trained AI models.
AI_URL="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-macos.zip"
mkdir -p tmp_ai
curl --fail --location --retry 3 --max-time 240 "$AI_URL" -o tmp_ai/engine.zip
unzip -q -o tmp_ai/engine.zip -d tmp_ai/unpacked
find tmp_ai/unpacked -maxdepth 3 -type f | head -30
AI_BIN="$(find tmp_ai/unpacked -type f -name realesrgan-ncnn-vulkan -print -quit)"
MODEL_PARAM="$(find tmp_ai/unpacked -type f -name realesrgan-x4plus.param -print -quit)"
test -n "$AI_BIN" || { echo "AI executable missing"; exit 1; }
test -n "$MODEL_PARAM" || { echo "AI photo model missing"; exit 1; }
AI_MODELS="$(dirname "$MODEL_PARAM")"
chmod +x "$AI_BIN"
file "$AI_BIN"
mkdir -p ai/models
cp "$AI_BIN" ai/realesrgan-ncnn-vulkan
cp -R "$AI_MODELS"/. ai/models/
test -f ai/models/realesrgan-x4plus.bin

python3 -m PyInstaller --noconfirm --clean --windowed --onedir \
  --name "$APP_NAME" \
  --osx-bundle-identifier uk.co.imagerestorestudio.app \
  --hidden-import=PIL._tkinter_finder \
  --hidden-import=cloud_premium \
  --collect-submodules PIL \
  --target-architecture x86_64 \
  src/entry.py

APP="dist/$APP_NAME.app"
test -f "$APP/Contents/MacOS/$APP_NAME"
mkdir -p "$APP/Contents/Resources/ai"
ditto ai "$APP/Contents/Resources/ai"
test -x "$APP/Contents/Resources/ai/realesrgan-ncnn-vulkan"
test -f "$APP/Contents/Resources/ai/models/realesrgan-x4plus.param"
"$APP/Contents/MacOS/$APP_NAME" --self-test
codesign --force --deep --sign - "$APP"
codesign --verify --deep "$APP"
mkdir -p stage/Applications
ditto "$APP" "stage/Applications/$APP_NAME.app"
pkgbuild --root stage --install-location / \
  --identifier uk.co.imagerestorestudio.installer --version "$VERSION" \
  "Image-Restore-Studio-${VERSION}-Intel.pkg"
ls -lh Image-Restore-Studio-*.pkg

# Image Restore Studio

Standalone macOS image editor packaging. Builds native macOS .app bundles and .pkg installers on GitHub Actions.

## Use

Open **Actions → Build standalone macOS installers** to find the build. Download the appropriate installer artefact after a successful run.

- Intel: macOS Intel (newer macOS runner). High Sierra compatibility is **not** verified.
- Apple Silicon: native arm64 build, where the runner is available.
- Image processing includes conventional 2×/4×/8× Lanczos enlargement, sharpening and OpenCV inpainting, **not** bundled AI upscaling or generative reconstruction.
- Unsigned and unnotarised installer: Apple's Gatekeeper may require additional approval.

The checked-in `src/app.py.zlib.b64` is the zlib-compressed original Python prototype source. The build decodes it into `src/app.py` before packaging. This is temporary source transport, not encryption.

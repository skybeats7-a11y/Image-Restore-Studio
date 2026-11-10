# Image Restore Studio — Intel 0.3

This repository builds a standalone Intel-only .pkg with GitHub Actions. The previous 0.2 Intel build included an OpenCV binary with **macOS 12** minimum compatibility and could install but fail to open on older Macs.

The v0.3 Intel build uses Python 3.8, Pillow 9.5 and PyInstaller 5.13, removes OpenCV and NumPy from the bundle, and includes an application startup log at `~/Library/Logs/Image Restore Studio/startup.log`.

The repair brush now uses **basic Pillow-only diffusion filling**, **not** advanced OpenCV or AI inpainting. Upscaling is ordinary Lanczos interpolation, not AI super-resolution. Optional external Real-ESRGAN has not been bundled.

High Sierra (10.13) launch compatibility is a **target, not a verified claim**: the build runs on a newer hosted Intel Mac and must still be tested on a physical High Sierra Mac. PyInstaller bootloader compatibility, bundled Tk and the actual Python/Pillow binary deployment targets all matter.

The .pkg is unsigned and unnotarised. Retrieve it from **Actions → Build Intel standalone installer → latest successful run → Artifacts**.

If macOS will not open the app, share the macOS version and the contents of `~/Library/Logs/Image Restore Studio/startup.log` (if created). A missing log could indicate a loader or compatibility failure before Python starts.

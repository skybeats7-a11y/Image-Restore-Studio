"""Modify the prototype to avoid newer OpenCV/NumPy shared libraries on older Intel Macs.
The Pillow-only repair is a basic fallback, not equivalent to AI or OpenCV inpainting.
"""
from pathlib import Path
p=Path("src/app.py")
src=p.read_text()
start=src.index("    def repair(self):\n")
stop=src.index("    def choose_ai(self):\n",start)
replacement='''    def repair(self):
        if self.work is None:return
        if not self.mask.getbbox():
            messagebox.showinfo('Select area','Paint over the area to repair first.')
            return
        try:
            # Local Pillow-only diffusion fill for macOS legacy compatibility.
            # This approximates nearby colour; heavily detailed areas may need manual repair.
            from PIL import ImageChops
            mask=self.mask.point(lambda v:255 if v>=128 else 0)
            # Seed missing pixels from the nearest surrounding areas using
            # iterative masked blur; preserve all unselected original pixels.
            valid=ImageOps.invert(mask)
            image=self.work.convert('RGB')
            filled=Image.composite(image,Image.new('RGB',image.size),valid)
            remaining=mask
            for _ in range(100):
                if not remaining.getbbox():break
                next_valid=valid.filter(ImageFilter.MaxFilter(5))
                front=ImageChops.subtract(next_valid,valid)
                if not front.getbbox():break
                # Blend colour from known pixels towards the missing area.
                smooth=filled.filter(ImageFilter.BoxBlur(3))
                filled.paste(smooth,(0,0),front)
                valid=next_valid
                remaining=ImageChops.subtract(mask,valid)
            self.work=Image.composite(filled,image,mask)
            self.clear_mask()
            self.status.set('Basic repair applied (legacy compatible).')
        except Exception as e:
            messagebox.showerror('Repair failed',str(e))
'''
src=src[:start]+replacement+src[stop:]
# No claim that OpenCV inpainting is still available.
src=src.replace("Offline · Repair needs OpenCV · AI requires a compatible executable and models",
                "Offline · Basic local repair · Optional external AI engine")
src=src.replace("self.title('Image Restore Studio · 0.1')","self.title('Image Restore Studio · 0.3 Intel')")
p.write_text(src)
print("Prepared legacy app, size",p.stat().st_size)

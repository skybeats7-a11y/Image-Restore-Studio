"""Upgrade v0.4 editor to hosted Topaz Premium while retaining optional local AI."""
from pathlib import Path
p=Path("src/app.py")
src=p.read_text()

# Add a premium engine with defaults chosen for low-resolution portraits.
old="self.mode=tk.StringVar(value='AI Super Resolution (Real-ESRGAN)')"
assert old in src, "v0.4 engine default not located"
src=src.replace(old,"self.mode=tk.StringVar(value='Premium Portrait (Topaz Cloud)')",1)
old="values=['AI Super Resolution (Real-ESRGAN)','Standard resize (no AI)']"
assert old in src, "v0.4 engine menu not located"
src=src.replace(old,"values=['Premium Portrait (Topaz Cloud)','Premium High Fidelity (Topaz Cloud)', 'Local Real-ESRGAN (GPU)', 'Standard resize (no AI)']",1)
src=src.replace("self.lab(head,'INTEL EDITION  ·  REAL AI UPSCALING',9,MUTED)",
 "self.lab(head,'INTEL EDITION · PREMIUM CLOUD OR LOCAL AI',9,MUTED)")
src=src.replace("self.lab(left,'AI model included in installer (GPU required)',9,MUTED).pack(fill='x',pady=(2,9))",
"""self.lab(left,'Premium cloud: paid account + internet; photos uploaded only with consent',9,MUTED).pack(fill='x',pady=(2,7))
        self.btn(left,'Premium account & photo-upload consent',self.set_premium_access)""")
assert "self.set_premium_access" in src, "premium control not added"

before="    def process(self,im,scale,engine):"
assert before in src
new= '''    def set_premium_access(self):
        from tkinter import simpledialog
        if not messagebox.askyesno('Premium cloud processing',
               'Premium processing uploads your selected photograph to Replicate/Topaz for AI processing. '
               'This requires an internet connection and a paid Replicate account. '
               'Charges may apply for each image. Photos may include private personal information.\\n\\n'
               'Do you consent to uploading the photos you choose to process?'):
            self._premium_allowed=False
            return
        token=simpledialog.askstring('Premium account','Enter your Replicate API token (kept only in memory):',
                                     parent=self,show='*')
        if token and token.strip():
            self._premium_token=token.strip()
            self._premium_allowed=True
            self.status.set('Premium account enabled. Images will be uploaded for AI processing.')
        else:
            self._premium_allowed=False
            self.status.set('Premium cloud not enabled. Local processing remains available.')

'''
src=src.replace(before,new+before,1)
marker="        if engine.startswith('AI'):\n"
assert marker in src
cloud='''        if engine.startswith('Premium'):
            if not getattr(self,'_premium_allowed',False):
                raise RuntimeError('Premium cloud is not enabled. Click Premium account and give photo-upload consent first.')
            token=getattr(self,'_premium_token','')
            from cloud_premium import upscale
            profile='High Fidelity V2' if 'High Fidelity' in engine else 'Low Resolution V2'
            return upscale(im,scale,token,profile=profile,face=True)
        if engine.startswith('Local'):
'''
src=src.replace(marker,cloud,1)
src=src.replace("self.title('Image Restore Studio · 0.4 Intel')",
                "self.title('Image Restore Studio · 0.5 Intel Premium')")
src=src.replace("Offline · Bundled Real-ESRGAN · Repair is basic (not generative)",
                "Premium cloud is paid/online · Local AI optional · Repair is basic")
# Disable 8x in premium deliberately; 8x local remains possible, but isn't additional AI restoration.
p.write_text(src)
compile(src,str(p),'exec')
print("Updated to v0.5:",len(src))

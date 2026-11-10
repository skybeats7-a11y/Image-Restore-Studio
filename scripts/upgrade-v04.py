"""Update legacy editor with native-Mac readable controls, stable comparison and bundled AI."""
from pathlib import Path

p=Path("src/app.py")
src=p.read_text()

def replace_method(name, following, replacement):
    global src
    begin=src.index("    def "+name+"(")
    end=src.index("    def "+following+"(",begin)
    src=src[:begin]+replacement.rstrip()+"\n"+src[end:]

# Mac's Aqua Tk ignores custom Button background colours; use real interactive labels.
replace_method("btn","section",'''
    def btn(self,parent,text,command,accent=False):
        bg=ACCENT if accent else '#344253'
        fg='#092522' if accent else '#ffffff'
        holder=tk.Frame(parent,bg=bg,highlightbackground='#536274',
                        highlightthickness=1)
        holder.pack(fill='x',pady=(0,9))
        text_label=tk.Label(holder,text=text,fg=fg,bg=bg,
                            font=('Helvetica',12,'bold'),anchor='center',
                            padx=11,pady=11,cursor='hand2')
        text_label.pack(fill='x')
        def click(event): command()
        for widget in (holder,text_label):
            widget.bind('<Button-1>',click)
        return holder
''')

# Scrolling sidebar, so controls never disappear below the window.
src=src.replace("self.geometry('1180x770'); self.minsize(860,580)",
                "self.geometry('1280x850'); self.minsize(980,630)")
src=src.replace("self.scale=tk.StringVar(value='4×'); self.mode=tk.StringVar(value='Balanced (Lanczos)')",
                "self.scale=tk.StringVar(value='4×'); self.mode=tk.StringVar(value='AI Super Resolution (Real-ESRGAN)')")
src=src.replace("self.lab(head,'LOCAL EDITING  ·  OPTIONAL AI ENGINE',9,MUTED)",
                "self.lab(head,'INTEL EDITION  ·  REAL AI UPSCALING',9,MUTED)")
src=src.replace(
    "left=tk.Frame(body,bg=PANEL,width=258,padx=15,pady=13);left.pack(side='left',fill='y');left.pack_propagate(False)\n        self.sidebar=left",
    """left_outer=tk.Frame(body,bg=PANEL,width=306)
        left_outer.pack(side='left',fill='y')
        left_outer.pack_propagate(False)
        left_canvas=tk.Canvas(left_outer,bg=PANEL,highlightthickness=0,bd=0)
        left_scroll=tk.Scrollbar(left_outer,orient='vertical',command=left_canvas.yview)
        left_scroll.pack(side='right',fill='y')
        left_canvas.pack(side='left',fill='both',expand=True)
        left_canvas.configure(yscrollcommand=left_scroll.set)
        left=tk.Frame(left_canvas,bg=PANEL,padx=15,pady=15)
        left_id=left_canvas.create_window((0,0),window=left,anchor='nw')
        left.bind('<Configure>',lambda e:left_canvas.configure(scrollregion=left_canvas.bbox('all')))
        left_canvas.bind('<Configure>',lambda e:left_canvas.itemconfigure(left_id,width=e.width))
        self.sidebar=left""")
src=src.replace("values=['Balanced (Lanczos)','AI Real-ESRGAN (external)']",
                "values=['AI Super Resolution (Real-ESRGAN)','Standard resize (no AI)']")
src=src.replace("self.lab(left,'Real-ESRGAN executable (optional)',9,MUTED).pack(fill='x')\n        self.btn(left,'Choose AI engine…',self.choose_ai)",
                "self.lab(left,'AI model included in installer (GPU required)',9,MUTED).pack(fill='x',pady=(2,9))")
src=src.replace("self.lab(left,'Paint over unwanted areas on image',9,MUTED)",
                "self.lab(left,'Brush unwanted marks on your own photos',9,MUTED)")
src=src.replace("text='Compare original (hold)'","text='Show original (hold)'")
src=src.replace("self.lab(foot,'Offline · Basic local repair · Optional external AI engine',9,MUTED)",
                "self.lab(foot,'Offline · Bundled Real-ESRGAN · Repair is basic (not generative)',9,MUTED)")
src=src.replace("self.lab(foot,'Offline · Repair needs OpenCV · AI requires a compatible executable and models',9,MUTED)",
                "self.lab(foot,'Offline · Bundled Real-ESRGAN · Repair is basic (not generative)',9,MUTED)")

# Compare must use the SAME canvas dimensions for original and enhanced.
replace_method("draw_preview","image_pt",'''
    def draw_preview(self):
        self.canvas.delete('all')
        if self.work is None:
            self.canvas.create_text(max(180,self.canvas.winfo_width()//2),max(150,self.canvas.winfo_height()//2),
                                    text='OPEN A PHOTO TO BEGIN',fill=MUTED,font=('Helvetica',18,'bold'))
            return
        cw=max(200,self.canvas.winfo_width()-28)
        ch=max(180,self.canvas.winfo_height()-28)
        # Geometry is always derived from the processed version, even when comparing.
        w,h=self.work.size
        s=min(float(cw)/w,float(ch)/h,1.0)
        pw=max(1,int(w*s)); ph=max(1,int(h*s))
        im=self.original if self.compare.get() else self.work
        temp=im.resize((pw,ph),Image.LANCZOS).convert('RGBA')
        if not self.compare.get() and self.mask is not None and self.mask.getbbox():
            small=self.mask.resize((pw,ph))
            red=Image.new('RGBA',(pw,ph),(255,58,80,0))
            red.putalpha(small.point(lambda v:min(130,int(v*.55))))
            temp=Image.alpha_composite(temp,red)
        self.photo=ImageTk.PhotoImage(temp)
        x=(self.canvas.winfo_width()-pw)//2
        y=(self.canvas.winfo_height()-ph)//2
        self.preview_box=(x,y,pw,ph)
        self.canvas.create_image(x,y,image=self.photo,anchor='nw')
        self.canvas.create_rectangle(x,y,x+pw,y+ph,outline='#4a596c')
        if self.compare.get():
            self.canvas.create_text(x+12,y+12,anchor='nw',text='ORIGINAL',
                                    fill='#ffffff',font=('Helvetica',12,'bold'))
''')

replace_method("process","work_async",'''
    def process(self,im,scale,engine):
        if im.width*scale*im.height*scale>135_000_000:
            raise RuntimeError('Output would exceed 135 megapixels. Select a lower scale.')
        if engine.startswith('AI'):
            if getattr(sys,'frozen',False):
                resources=Path(sys.executable).resolve().parent.parent / 'Resources'
                base=resources/'ai'
            else:
                base=Path(__file__).resolve().parent.parent/'ai'
            candidates=[base/'realesrgan-ncnn-vulkan',
                        base/'realesrgan-ncnn-vulkan'/'realesrgan-ncnn-vulkan']
            binary=next((v for v in candidates if v.is_file()),None)
            if binary is None:
                raise RuntimeError('Bundled AI engine missing from this installer. '
                                   'This operation cannot run as AI upscaling.')
            model_candidates=[base/'models',base/'realesrgan-ncnn-vulkan'/'models']
            model_dir=next((v for v in model_candidates
                            if (v/'realesrgan-x4plus.param').exists()),None)
            if model_dir is None:
                raise RuntimeError('Real-ESRGAN model files are missing from the installer.')
            with tempfile.TemporaryDirectory() as d:
                inp=Path(d)/'input.png'
                out=Path(d)/'output.png'
                im.save(str(inp))
                # 4x trained model: output can subsequently be resized to 2x.
                cmd=[str(binary),'-i',str(inp),'-o',str(out),
                     '-m',str(model_dir),'-n','realesrgan-x4plus','-s','4','-t','100']
                proc=subprocess.run(cmd,capture_output=True,text=True,timeout=1800,
                                    cwd=str(binary.parent))
                if proc.returncode or not out.is_file():
                    detail=(proc.stderr or proc.stdout or 'No output file was generated')[-1700:]
                    raise RuntimeError('Real-ESRGAN could not run on this Mac or GPU. '
                        'Check GPU support / macOS requirements. Details:\\n'+detail)
                with Image.open(str(out)) as out_im:
                    ai=out_im.convert('RGB')
                target=(im.width*scale,im.height*scale)
                if ai.size!=target:
                    ai=ai.resize(target,Image.LANCZOS)
                return ai
        return im.resize((im.width*scale,im.height*scale),Image.LANCZOS)
''')
# Use a button-like text colour consistently on Mac native Tk.
src=src.replace("self.title('Image Restore Studio · 0.3 Intel')",
                "self.title('Image Restore Studio · 0.4 Intel')")
src=src.replace("self.title('Image Restore Studio · 0.1')",
                "self.title('Image Restore Studio · 0.4 Intel')")
p.write_text(src)
compile(src,str(p),'exec')
print("v0.4 patched source, size",len(src))

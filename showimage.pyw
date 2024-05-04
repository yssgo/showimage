#!python3
import time
import PIL.Image
import PIL.ImageTk
import tkinter
import tkinter.scrolledtext
import scrollimage
import itertools
import os,sys,platform,re

help_lang = "ko"
help_msg = {
    'en': r"""[Usage]
pyw -3 "path/to/showimage.pyw" [/b {rgb}|/b check] [/n] [/z {factor}| /s {factor}] [ /r {method} ] {imagefilename}
   /b {rgb}, /bg {rgb}, -b {rgb}, --backgorund {rgb}:
       background color
       255:255:255 : rgb(255,255,255)
       #FFFFFF : rgb(0xFF,0xFF,0xFF)
   /b check, /bg check, -b check, --background check:
       checkerboard background (defaut)
   /n, /noanim, -n, --noanim :
       treat a .web, or .gif file as a still image
   /z {[-]factor}, /zoom {[-]factor}, -z {[-]factor}, --zoom {[-]factor}:
       (* NOT for GIF files *)
       factor: number a real number (aka float).
           zoom up to size * factor
           if negative sign (-) is used zoom out to size / factor
       This option use 'Lanczos' resampling method (high quality. a little blurry).
       (* the tooltip will show the original width and height *)
   /s {[-]factor}, /scale {[-]factor}, -s {[-]factor}, --scale {[-]factor}:
       just the same as /zoom
       Except that this option use 'Nearest' resampling method (low quality).
   /r {method}, /resmaple {method},
   -r {method}, --resmaple {method}:
       Choose resampling method for /zoom or /scale option.
       resampling method: Nearest, Box, Bilinear, Hamming, Bicubic, Lanczos
                          You may use only the first 3 letters.

    For /z, /s, /r options the last option decides the resampling method.
    Otherwise, the order of options is not important.
""",
    'ko':  r"""[Usage]
pyw -3 "path/to/showimage.pyw" [/b {rgb}|/b check] [/n] [/z {factor}| /s {factor}] [ /r {method} ] {imagefilename}
   /b {rgb}, /bg {rgb}, -b {rgb}, --backgorund {rgb}:
       배경색
       255:255:255 : rgb(255,255,255)
       #FFFFFF : rgb(0xFF,0xFF,0xFF)
   /b check, /bg check, -b check, --background check:
       체커보드 배경 (기본)
   /n, /noanim, -n, --noanim :
       .web 또는 .gif 파일을 스틸 이미지로 처리
   /z {[-]factor}, /zoom {[-]factor}, -z {[-]factor}, --zoom {[-]factor}:
       (* GIF 파일은 미해당 *)
       factor: 실수 (float 타입)
           size * factor 로 확대
           음수 부호(-)를 사용하면 size / factor 로 축소
       이 옵션은 'Lanczos' 리샘플링 방법 사용 (고화질. 약간 흐려짐).
       (* 도구팁은 원래의 폭, 너비를 보여줌 *)
   /s {factor}, /scale {factor}, -s {factor}, --scale {factor}:
       /zoom 과 같음.
       단, 이 옵션은 'Nearest' 리샘플링 방법 사용 (저화질).
   /r {method}, /resmaple {method},
   -r {method}, --resmaple {method}:
       리샘플링 방법 선택. /zoom 또는 /scale 용 옵션.
       리샘플링 방법: Nearest, Box, Bilinear, Hamming, Bicubic, Lanczos
                      앞 3 글자만 사용해도 됨.

    /z, /s, /r 옵션은 마지막 옵션이 리샘플링 방법 결정.
    다른 경우, 옵션의 순서는 중요하지 않음.
"""
}

def ShowErrorAndExit(s):
    from tkinter.messagebox import showerror
    showerror("에러", s)
    sys.exit()


# https://stackoverflow.com/a/56749167  
class ToolTip(object):

    def __init__(self, widget):
        self.widget=widget
        self.tipwindow = None
        self.label = None
        self.id = None

    def showtip(self, text, mx, my):
        "Display text in tooltip window"
        self.text = text        
        if self.tipwindow or not text:
            return
        if self.tipwindow:
            tw = self.tipwindow
            tw.wm_geometry("+%d+%d" % (mx+10, my+10))
            self.label.configure(text=text)
            label.pack(ipadx=1)
        else:
            self.tipwindow = tkinter.Toplevel(self.widget)
            self.tipwindow.wm_overrideredirect(1)
            x = self.widget.winfo_rootx() + mx
            y = self.widget.winfo_rooty() + my
            self.tipwindow.wm_geometry("+%d+%d" % (x+10, y+10))
            
            self.label = tkinter.Label(self.tipwindow, text=self.text, justify=tkinter.LEFT,
                          background="#ffffe0", relief=tkinter.SOLID, borderwidth=1,
                          font=("D2Coding", "12", "normal"))
            self.label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        if tw:
            tw.destroy()
        self.tipwindow = None

def CreateToolTip(image_frame, canvas, scale=1.0):
    toolTip = ToolTip(canvas)
    def _maketip(event):
        if scale==1.0:            
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            return f"{x}, {y}"
        else:
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            return f"{x/scale:.3f}, {y/scale:.3f}"

    def enter(event):
        toolTip.hidetip()
        toolTip.showtip(_maketip(event), event.x, event.y)
    def leave(event):
        toolTip.hidetip()
    def motion(event):
        toolTip.hidetip()
        toolTip.showtip(_maketip(event), event.x, event.y)

    canvas.bind('<Enter>', enter)
    canvas.bind('<Leave>', leave)
    # https://stackoverflow.com/a/63485797
    canvas.bind("<Motion>", motion)
    return toolTip

def make_photoimage(theImage, bgtype, scale=1.0, resampling='Lanczos'):
    if type(theImage)==str:
        source_pil_image = PIL.Image.open(theImage).convert("RGBA")
    elif type(theImage)==PIL.ImageTk.PhotoImage:
        source_pil_image = PIL.ImageTk.getimage(theImage)
    elif type(theImage)==PIL.Image.Image:
        source_pil_image = theImage
    else:
        
        ShowErrorAndExit(f'{theImage=},\n{type(theImage)=}\n'
                          "ShowImage: unsupported format")

    source_pil_image = source_pil_image.convert("RGBA")
    
    resampling_method={
        'Nearest': PIL.Image.Resampling.NEAREST,
        'Box': PIL.Image.Resampling.BOX,
        'Bilinear': PIL.Image.Resampling.BILINEAR,
        'Hamming' : PIL.Image.Resampling.HAMMING,
        'Bicubic': PIL.Image.Resampling.BICUBIC,
        'Lanczos': PIL.Image.Resampling.LANCZOS,
    }
    
    orgw,orgh = source_pil_image.size
    if scale != 1:
        scaw, scah = int(orgw * scale+0.5), int(orgh*scale+0.5)
        source_pil_image = source_pil_image.resize(
            (scaw, scah),
            resampling_method.get(
                resampling.title(),
                PIL.Image.Resampling.LANCZOS))

    if bgtype=="check":
        base_pil_img = PIL.Image.new("RGBA", source_pil_image.size, color=(180,180,180,255))
        cksize=10
        darkcell = PIL.Image.new("RGBA", (cksize,cksize), color=(220,220,220,255))
        for x in range(0,source_pil_image.size[0],cksize):
            for y in range(0,source_pil_image.size[1],cksize):
                if ((x//cksize)+(y//cksize))%2==0:
                    base_pil_img.paste(darkcell,(x, y))
        base_pil_img.paste(source_pil_image, mask=source_pil_image)
        photoimg = PIL.ImageTk.PhotoImage(image=base_pil_img)
    else:
        if bgtype=="white":
            r,g,b=255,255,255
        else:
            r, g, b = map(int, bgtype.split(","))
        base_pil_img = PIL.Image.new("RGBA", source_pil_image.size, color=(r, g, b,255))
        base_pil_img.paste(source_pil_image, mask=source_pil_image)
        photoimg = PIL.ImageTk.PhotoImage(image=base_pil_img)
    return photoimg

ishexdigit = lambda s: bool(s and set(s) <= set('0123456789ABCDEFabcdef'))

def normalize_bgtype(bgtype):
    if not bgtype:
        bgtype = f"255,255,255"
    elif bgtype=="check":
        bgtype ="check"
    else:
        if bgtype.count(',')==2:
            sa_rgb = bgtype.split(',')
            if len(sa_rgb)!=3:
                r,g,b=255,255,255
            else:
                rgb = [255,255,255]
                for i in range(3):
                    e = sa_rgb[i]
                    if e and e[0]=='#':
                        if 2==len(e[1:]) and ishexdigit(e[1:]):
                            rgb[i] = int(e[1:], 16)
                        elif 1==len(e[1:]) and ishexdigit(e[1:]):
                            rgb[i] = int(e[1:], 16)*0x11
                        else:
                            ShowErrorAndExit("ShowImage: invalid bgtype")
                    else:
                        if e.isdigit() and 0<=int(e,10)<=255:
                            rgb[i] = int(e,10)
                        else:
                            ShowErrorAndExit("ShowImage: bgtype color out of range")
                r, g, b = rgb
        elif bgtype[0]=='#' and len(bgtype[1:])==6 and ishexdigit(bgtype[1:]):
            rgb = [int(bgtype[i:i+2],16) for i in range(1,7,2)]
            r,g,b=rgb
        elif bgtype[0]=='#' and len(bgtype[1:])==3 and ishexdigit(bgtype[1:]):
            rgb = [int(bgtype[i:i+1],16)*0x11 for i in range(1,4,1)]
            r,g,b=rgb
        else:
            ShowErrorAndExit(f"ShowImage: invalid bg : {bgtype}")
        bgtype = f"{r},{g},{b}"
    return bgtype


def ShowImage(theImage, agroot=None, title=None, bgtype="check", scale=1.0, resampling='Lanczos'):
    if agroot == None:
        master = tkinter.Tk()
        master.withdraw()
    else:
        master = agroot

    if title and type(master)==tkinter.Tk:
        master.title(title);

    bgtype = normalize_bgtype(bgtype)

    my_image = make_photoimage(theImage, bgtype, scale=scale, resampling=resampling)

    image_frame = scrollimage.ScrollableImageFrame(master,
        image=my_image, scrollbarwidth=20,
        width=min(800,my_image.width()+6),
        height=min(600,my_image.height()+6))
    image_frame.pack(expand=True, fill='both')

    if agroot == None:
        master.deiconify()
        image_frame.focus_force()

    toolTip = CreateToolTip(image_frame, image_frame.canvas, scale=scale)

    master.mainloop()

class ImageLabel(tkinter.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL PIL.Image instance or a string filename
    """
    MININUM_DURATION = 20
    def load(self, im,  bgtype="check", scale=1.0, resampling='Lanczos'):
        if isinstance(im, str):
            im = PIL.Image.open(im)
        frames = []
        duration = []
        try:
            for i in itertools.count(1):
                # imcopy = im.copy()
                # if imcopy.mode=='P':
                    # if imcopy.info.get('transparency',False)==False:
                        # imcopy = imcopy.convert("RGB")
                        # imcopy = imcopy.convert("RGBA")
                    # else:
                        # imcopy = imcopy.convert("RGBA")
                # else:
                    # imcopy = imcopy.convert("RGBA")
                # imphoto = make_photoimage(imcopy, bgtype, scale)
                imphoto = make_photoimage(im.copy(), bgtype, scale=scale, resampling=resampling)
                frames.append(imphoto)
                try:
                    duration.append(im.info['duration'])
                    if duration[-1] == 0:
                        duration[-1] = ImageLabel.MININUM_DURATION
                except:
                    duration.append(100)
                im.seek(i)
        except EOFError:
            pass
        self.frames = itertools.cycle(frames)
        self.duration = itertools.cycle(duration)
        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(next(self.duration), self.next_frame)

def ShowGifAnim(gif,title=None, bgtype="check", scale=1.0, resampling='Lanczos'):
    '''gif: A PIL PIL.Image instance or a string filename'''

    bgtype = normalize_bgtype(bgtype)
    root = tkinter.Tk()
    if title:
        root.title(title)
    lbl = ImageLabel(root)
    lbl.pack()

    lbl.load(gif, bgtype, scale=scale, resampling=resampling)
    # toolTip = CreateToolTip(lbl)
    root.mainloop()

def get_nframes(fname):
    im = PIL.Image.open(fname)
    return im.n_frames

if __name__ == "__main__":
    GIF_AS_STILL = False
    SCALE_FACTOR = 1
    RESAMPLING='Lanczos'
    if len(sys.argv)==1 or any((x in ["/?" , "-?", "-h", "--help"]) for x in sys.argv):
        class Help(tkinter.Frame):
            def __init__(self, root):
                super().__init__(root)
                self.st=tkinter.scrolledtext.ScrolledText(self, width=125, height=30)
                self.st.insert(tkinter.INSERT, help_msg[help_lang])
                self.st.configure(state='disabled', spacing1=5, spacing2=5, spacing3=5)
                self.st.pack(expand=True, fill='both', side='left')
                self.pack(expand=True, fill='both')
        root = tkinter.Tk()
        h = Help(root)
        root.mainloop()
    else:
        fname = ''
        bgtype = 'check'
        usage_error = False
        SKIP_ARG=0
        for arg_i, arg in enumerate(sys.argv[1:], start=1):
            if SKIP_ARG != 0:
                SKIP_ARG -= 1
                if SKIP_ARG >=0:
                    continue            
            if arg == '-py':
                # if arg_i+1 < len(sys.argv):
                    # requested_python_version = sys.argv[arg_i+1]
                SKIP_ARG=1
            elif arg in ['/b','/bg','-b','--backgorund']:
                if arg_i + 1 < len(sys.argv):
                    if sys.argv[arg_i+1]=='check':
                        bgtype = 'check'
                        SKIP_ARG=1
                    else:
                        x_bgtype = sys.argv[arg_i+1]
                        if x_bgtype[0]=='#':
                            r = int(x_bgtype[1:3],16)
                            g = int(x_bgtype[3:5],16)
                            b = int(x_bgtype[5:7],16)
                            bgtype = ','.join(map(str, [r,g,b]))
                            SKIP_ARG=1
                        elif x_bgtype.count(':')==2:
                            bgtype = x_bgtype.replace(':',',')
                            SKIP_ARG=1
                        else:
                            ShowErrorAndExit("ShowImage: invalid bg type")
                else:
                    ShowErrorAndExit("ShowImage: missing bg type")
            elif arg in ('/n', '/noanim','-n','--noanim'):
                GIF_AS_STILL = True
            elif arg in ('/z','/zoom','-z','--zoom','/s','/scale','-s','--scale'):
                if arg in ('/z','/zoom','-z','--zoom'):
                    RESAMPLING='Lanczos'
                    argtype='ZOOM'
                else:
                    RESAMPLING='Nearest'
                    argtype='SCALE'
                if arg_i+1 < len(sys.argv):
                    m = re.match(r'^([-+]?[.0-9]+)$', sys.argv[arg_i+1])
                    if m:
                        sFactor = m.group(1)
                        fFactor = float(sFactor)
                        if fFactor > 0:
                            SCALE_FACTOR = fFactor
                        else:
                            SCALE_FACTOR = 1/abs(fFactor)
                    else:
                        raise Exception(f"ShowImage: invalid factor {sys.argv[arg_i+1]} factor for /zoom argument")
                    SKIP_ARG=1
                else:
                    ShowErrorAndExit(f"ShowImage: missing {argtype.lower()} factor for /zoom argument")
            elif arg in ('/r','/resample','-r','--resample'):
                if arg_i+1 < len(sys.argv):
                    m = re.match(r'(?i)(Nea(?:rest)?|Box|Bil(?:inear)?|Ham(?:ming)|Bic(?:ubic)?|Lan(?:czos)?)$', sys.argv[arg_i+1])
                    if m:
                        abbrev={
                            'Nea': 'Nearest',
                            'Bil': 'Bilinear',
                            'Box': 'Box',
                            'Ham': 'Hamming',
                            'Bic': 'Bicubic',
                            'Lan': 'Lanczos'
                        }                        
                        RESAMPLING=abbrev.get(m.group(1).title()[:3],'Lanczos')
                    else:
                        ShowErrorAndExit(f"ShowImage: Invalid method {sys.argv[arg_i+1]} for /resample argument")
                    SKIP_ARG=1
                else:
                    ShowErrorAndExit(f"ShowImage: missing {method} for /resample argument")
            else:
                fname = arg
        if not fname:
            ShowErrorAndExit("ShowImage: filename not given")

        image_ext = os.path.splitext(fname)[1]
        if ( not GIF_AS_STILL
          and (os.path.splitext(fname)[1].lower() in (".gif", ".webp"))
          and get_nframes(fname) > 1 ):
            SCALE_FACTOR = 1
            ShowGifAnim(fname, bgtype=bgtype, title = "showimage --"+os.path.basename(fname), scale=SCALE_FACTOR, resampling=RESAMPLING)
        else:
            ShowImage(fname, bgtype=bgtype, title = "showimage --"+os.path.basename(fname), scale=SCALE_FACTOR, resampling=RESAMPLING)



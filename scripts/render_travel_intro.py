from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import subprocess, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'videos'
OUT.mkdir(exist_ok=True)
W,H=1920,1080
BG=(232,237,240)
def photo(name, box):
    im=ImageOps.exif_transpose(Image.open(ROOT/name)).convert('RGB')
    im=ImageOps.contain(im,box,Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',box,BG)
    canvas.paste(im,((box[0]-im.width)//2,(box[1]-im.height)//2))
    return canvas
# Whole photographs; uniform scaling only, no retouching or cropping.
left=photo('20261101122054.JPEG',(1080,1080))
plane=photo('20261101121846.JPEG',(840,540))
# Original hotel illustration, drawn in Python without lettering.
s=3
hotel=Image.new('RGB',(840*s,540*s),(218,231,239))
d=ImageDraw.Draw(hotel)
def rect(b,c): d.rectangle(tuple(int(x*s) for x in b),fill=c)
def poly(p,c): d.polygon([(int(x*s),int(y*s)) for x,y in p],fill=c)
def ellipse(b,c): d.ellipse(tuple(int(x*s) for x in b),fill=c)
ellipse((54,40,246,98),(239,244,246))
ellipse((591,53,776,111),(239,244,246))
rect((0,433,840,540),(207,215,208))
poly([(0,490),(840,451),(840,540),(0,540)],(191,201,202))
ellipse((120,437,731,489),(177,190,190))
rect((184,133,626,439),(239,232,215))
poly([(626,133),(698,171),(698,439),(626,439)],(200,201,190))
rect((171,122,636,141),(78,100,116))
poly([(636,122),(709,162),(698,175),(626,141)],(58,82,98))
rect((204,154,605,169),(215,209,193))
for y in (190,254,318):
    for x in (214,286,358,430,502,574):
        rect((x,y,x+35,y+43),(77,106,124))
        rect((x+4,y+4,x+31,y+39),(139,169,186))
        rect((x+16,y+4,x+19,y+39),(215,221,214))
for y in (192,256,320):
    for x in (645,674):
        poly([(x,y),(x+14,y+7),(x+14,y+48),(x,y+41)],(103,130,142))
rect((205,378,604,439),(221,216,200))
rect((361,372,469,439),(66,94,111))
rect((370,380,410,435),(150,175,187))
rect((420,380,460,435),(150,175,187))
poly([(323,364),(493,364),(516,385),(302,385)],(81,107,122))
rect((313,385,319,440),(109,121,119))
rect((499,385,505,440),(109,121,119))
rect((342,440,488,448),(233,231,218))
rect((327,448,503,456),(224,224,212))
for x in (129,725):
    rect((x-5,358,x+5,449),(113,117,98))
    ellipse((x-43,302,x+43,388),(123,149,131))
    ellipse((x-34,279,x+34,351),(139,163,144))
rect((90,444,163,460),(153,162,146))
rect((690,444,761,460),(153,162,146))
hotel=hotel.resize((840,540),Image.Resampling.LANCZOS)
base=Image.new('RGB',(W,H),BG)
base.paste(left,(0,0))
base.save(OUT/'travel_base.png')
plane.save(OUT/'travel_plane.png')
hotel.save(OUT/'hotel_illustration.png')
final=base.copy();final.paste(plane,(1080,0));final.paste(hotel,(1080,540))
final.save(OUT/'travel_preview.png')
target=OUT/'travel_intro_8s.mp4'
cmd=['ffmpeg','-y','-v','error','-loop','1','-framerate','30','-i',str(OUT/'travel_base.png'),'-loop','1','-framerate','30','-i',str(OUT/'travel_plane.png'),'-loop','1','-framerate','30','-i',str(OUT/'hotel_illustration.png'),'-filter_complex','[1:v]format=rgba,fade=t=in:st=2:d=2:alpha=1[p];[2:v]format=rgba,fade=t=in:st=4:d=2:alpha=1[h];[0:v][p]overlay=1080:0:format=auto[b];[b][h]overlay=1080:540:format=auto,format=yuv420p[v]','-map','[v]','-an','-t','8','-r','30','-c:v','libx264','-preset','slow','-crf','17','-profile:v','high','-level:v','4.1','-pix_fmt','yuv420p','-movflags','+faststart','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-threads','2',str(target)]
subprocess.run(cmd,check=True)
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]))
assert len(info['streams'])==1
v=info['streams'][0]
assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==('h264',1920,1080,'30/1','240')
assert abs(float(info['format']['duration'])-8)<.001
# Decoded last two seconds must remain still.
hashes=subprocess.check_output(['ffmpeg','-v','error','-ss','6','-i',str(target),'-f','framemd5','-']).decode()
values=[l.split(',')[-1].strip() for l in hashes.splitlines() if not l.startswith('#')]
# Lossy inter-frame encoding can cause small reconstruction differences.
(OUT/'travel_validation.json').write_text(json.dumps({'codec':v['codec_name'],'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':v['nb_frames'],'duration':info['format']['duration'],'audio':False,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2))
for name in ('travel_base.png','travel_plane.png'):
    (OUT/name).unlink()
print(target)

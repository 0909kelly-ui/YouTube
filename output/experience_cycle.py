"""Python 3 + Pillow + numpy + FFmpeg. Run: python experience_cycle.py
Edit CARDS, CURVES, colors and timing below. Use --font for a Japanese font.
"""
from pathlib import Path
import argparse, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1920,1080,30
BG='#F6F1E9'; INK='#403C39'; MUTED='#756B64'; ARROW='#B87F68'
CARDS=[((650,225,1270,415),'①','新しい経験','小さな「できた」','#F5DCC4',1),((1250,480,1850,670),'②','自信がつく','私にもできる','#F0DAD6',2.5),((650,735,1270,925),'③','心の目盛りが上がる','自分の価値を感じ直す','#F5DCC4',4),((70,480,670,670),'④','考える時間が変わる','過去を思い返す時間が減る','#F0DAD6',5.5)]
CURVES=[((1290,320),(1440,320),(1550,360),(1550,460)),((1550,690),(1550,790),(1440,830),(1290,830)),((630,830),(480,830),(370,790),(370,690)),((370,460),(370,360),(480,320),(630,320))]
STARTS=[2.5,4,5.5,7]
def ease(v):
 v=max(0,min(1,v)); return v*v*(3-2*v)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--font',default='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'); ap.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
 def font(s): return ImageFont.truetype(a.font,s,index=0)
 def text(d,pos,s,size,color=INK):
  f=font(size); b=d.textbbox((0,0),s,font=f); d.text((pos[0]-(b[2]-b[0])/2,pos[1]-(b[3]-b[1])/2-b[1]),s,font=f,fill=color)
 header=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(header)
 text(d,(960,108),'新しい経験が、心を変えていく',64)
 d.rounded_rectangle((905,172,1015,178),radius=3,fill='#D4A28A')
 text(d,(960,1009),'※ 語り手自身の経験を整理した図です。変化の過程には個人差があります。',28,MUTED)
 layers=[]
 for rect,num,title,sub,color,start in CARDS:
  layer=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(layer); x0,y0,x1,y1=rect; cx=(x0+x1)/2
  d.rounded_rectangle((x0,y0+5,x1,y1+5),radius=30,fill='#E8DFD6'); d.rounded_rectangle(rect,radius=30,fill=color,outline='#DCC8BA',width=2)
  text(d,(cx,y0+34),num,30,MUTED); text(d,(cx,y0+86),title,46); text(d,(cx,y0+143),sub,32)
  assert d.textbbox((0,0),title,font=font(46))[2]<x1-x0-50
  assert d.textbbox((0,0),sub,font=font(32))[2]<x1-x0-50
  layers.append(layer)
 paths=[]
 for c in CURVES:
  p=np.array(c,float); u=np.linspace(0,1,241)[:,None]; paths.append((1-u)**3*p[0]+3*(1-u)**2*u*p[1]+3*(1-u)*u*u*p[2]+u**3*p[3])
 def frame(t):
  im=Image.blend(Image.new('RGB',(W,H),'#FFFCF7'),Image.new('RGB',(W,H),BG),ease(t/.8)).convert('RGBA')
  def overlay(layer,alpha):
   if alpha>=1: im.alpha_composite(layer)
   elif alpha>0:
    cp=layer.copy(); cp.putalpha(layer.getchannel('A').point(lambda x:round(x*alpha))); im.alpha_composite(cp)
  overlay(header,ease(t/.8))
  for l,c in zip(layers,CARDS): overlay(l,ease((t-c[-1])/.65))
  d=ImageDraw.Draw(im)
  for pts,start in zip(paths,STARTS):
   q=ease((t-start)/1.35)
   if q<=0: continue
   n=max(2,round(q*240)+1); s=pts[:n]; d.line([tuple(p) for p in s],fill=ARROW,width=9,joint='curve')
   tip=s[-1]; v=tip-s[max(0,n-5)]; v/=np.linalg.norm(v); normal=np.array([-v[1],v[0]]); b=tip-25*v
   d.polygon([tuple(tip),tuple(b+13*normal),tuple(b-13*normal)],fill=ARROW)
  return im.convert('RGB')
 frame(10).save(a.output_dir/'experience_cycle.png')
 cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output_dir/'experience_cycle.mp4')]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for i in range(300):
  p.stdin.write(frame(i/30).tobytes())
  if i%60==0: print(f'{i}/300',flush=True)
 p.stdin.close(); assert p.wait()==0
 # Review montage is an intermediate artifact only.
 review=Image.new('RGB',(960*3,540*2))
 for i,t in enumerate([1.8,3.5,5,6.5,8,9.9]): review.paste(frame(t).resize((960,540)),((i%3)*960,(i//3)*540))
 review.save('/workspace/work/review.jpg')
if __name__=='__main__': main()

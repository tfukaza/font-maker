"""Compiled ligature comparison proofs. All artwork comes from actual font bytes."""
import copy,json,sys,hashlib
from pathlib import Path
from xml.etree import ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from font_maker.preview import shape_font,svg_to_png
from font_maker.store import ProjectStore
OUT=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else OUT/'ligature-review/font'
DEST=Path(sys.argv[2]) if len(sys.argv)>2 else OUT/'ligature-review/proofs'
DEST.mkdir(exist_ok=True,parents=True)
fontpath=ROOT/'build/fonts/PartyBlob-Regular.ttf'
store=ProjectStore(ROOT);revision=store.revision()
CASES={'ec':['Rec','record','collect'],'in':['Engine','spinning','inside'],'na':['Snap','banana','natural'],'oo':['moon','balloon','groovy'],'rt':['Party','started','artwork']}
KERN={'ec':-30,'in':-20,'na':-50,'oo':-30,'rt':-25}
NS='{http://www.w3.org/2000/svg}';ET.register_namespace('',NS[1:-1]);records=[]
font=TTFont(fontpath);glyphs=font.getGlyphSet()
def canvas(w,h):
 s=ET.Element(NS+'svg',{'width':str(w),'height':str(h),'viewBox':f'0 0 {w} {h}'})
 ET.SubElement(s,NS+'rect',{'width':'100%','height':'100%','fill':'#f7f5ef'})
 return s
def label(s,text,x,y):
 ET.SubElement(s,NS+'text',{'x':str(x),'y':str(y),'fill':'#67655c','font-family':'Arial','font-size':'12'}).text=text
def draw(s,text,x,y,size,on,adjust=None,kern=True):
 run=shape_font(fontpath,text,{'kern':kern,'liga':False,'dlig':on})
 if adjust:
  run=copy.deepcopy(run)
  for a,b in zip(run['glyphs'],run['glyphs'][1:]):
   seq=a['glyph_name']+b['glyph_name']
   if seq in adjust:a['x_advance']+=adjust[seq];run['total_advance']+=adjust[seq]
 cursor=x;scale=size/1000
 for g in run['glyphs']:
  pen=SVGPathPen(glyphs);glyphs[g['glyph_name']].draw(pen)
  ET.SubElement(s,NS+'path',{'d':pen.getCommands(),'fill':'#101010','transform':f'translate({cursor+g["x_offset"]*scale} {y-g["y_offset"]*scale}) scale({scale} {-scale})'})
  cursor+=g['x_advance']*scale
 records.append({'text':text,'size':size,'features':run['features'],'kerning_only_adjustment':adjust,'shaping':run})
 return run
def save(s,name,scale):
 data=ET.tostring(s);(DEST/(name+'.svg')).write_bytes(data);(DEST/(name+'.png')).write_bytes(svg_to_png(data,pixel_scale=scale))
for pair,words in CASES.items():
 s=canvas(700,250)
 label(s,pair+' / current',20,30);label(s,'kerning only '+str(KERN[pair]),245,30);label(s,'ligature',470,30)
 draw(s,pair,20,200,160,False);draw(s,pair,245,200,160,False,{pair:KERN[pair]});draw(s,pair,470,200,160,True)
 save(s,pair+'-construction',3)
 s=canvas(760,470);label(s,'DLIG OFF / KERN ON',22,25);label(s,'DLIG ON / KERN ON',402,25)
 for index,word in enumerate(words):
  y=135+index*135;draw(s,word,22,y,96,False);draw(s,word,402,y,96,True)
 save(s,pair+'-words',3)
 s=canvas(760,180);label(s,'Actual 32 px / off then on',20,20)
 draw(s,' '.join(words),20,60,32,False);draw(s,' '.join(words),20,120,32,True);save(s,pair+'-small',1)
 # Isolated replacement detail at native 160 px, scale 4.
 s=canvas(210,230);draw(s,pair,20,170,160,True);save(s,pair+'-detail',4)
 # Repeat and punctuation boundaries, with replacement-boundary kern comparison.
 s=canvas(760,320);text=f'({pair}) {pair}{pair} a{pair}a'
 label(s,'DLIG ON / KERN OFF',20,25);draw(s,text,20,125,96,True,kern=False)
 label(s,'DLIG ON / KERN ON',20,180);draw(s,text,20,280,96,True,kern=True);save(s,pair+'-boundaries',3)
s=canvas(760,320)
for on,y in [(False,120),(True,270)]:
 label(s,'DLIG '+str(on),20,y-80);draw(s,'final banana Engine',20,y,80,on)
save(s,'overlaps',3)
kerning_deltas={}
for page,words in enumerate([['Rec','Snap','Food'],['Pool','Tool','Tech']],1):
 s=canvas(760,535)
 label(s,'KERN OFF / DLIG ON',22,25);label(s,'KERN ON / DLIG ON',402,25)
 for index,word in enumerate(words):
  y=135+index*160
  off=draw(s,word,22,y,96,True,kern=False)
  on=draw(s,word,402,y,96,True,kern=True)
  delta=on['total_advance']-off['total_advance']
  assert delta != 0,(word,'comparison does not exercise a kerning rule')
  kerning_deltas[word]=delta
  label(s,f'{delta} font units / {delta*96/1000:.2f} px at 96 px',402,y+42)
 save(s,f'kerning-active-{page}',3)
(DEST/'kerning-deltas.json').write_text(json.dumps(kerning_deltas,indent=2))
s=canvas(1120,980)
label(s,'PARTY BLOB / CREATIVE LIGATURES',24,30)
label(s,'PAIR',24,64);label(s,'CURRENT / KERN ON',100,64);label(s,'LIGATURE / KERN ON',360,64);label(s,'IN WORDS',620,64)
for index,(pair,word) in enumerate([('En','Engine'),('ec','record'),('in','inside'),('na','banana'),('oo','balloon'),('rt','Party')]):
 y=195+index*145
 label(s,pair,24,y-35)
 draw(s,pair,100,y,160,False);draw(s,pair,360,y,160,True);draw(s,word,620,y,100,True)
save(s,'overview',2)
(DEST/'index.json').write_text(json.dumps({'revision':revision,'font_sha256':hashlib.sha256(fontpath.read_bytes()).hexdigest(),'cases':CASES,'records':records},indent=2))
print(DEST,revision)

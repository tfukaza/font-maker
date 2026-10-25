from pathlib import Path
import hashlib,json,shutil,html
from xml.etree import ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
from font_maker.service import FontMakerService
D=Path(__file__).resolve().parent;O=D.parents[1]
s=FontMakerService();i=s.open_project(str(O));p=s._store_project(i['project_id'])[1]
B=O/'revisions/before-consistency-audit'
if not B.exists():
 B.mkdir()
 for f in ['font.yaml','design.json','build-report.json','browser-review.json','quality-report.json','specimen.html','specimen.png','HakilandDisplay-Package.zip','review-notes.md']:
  shutil.copy2(O/f,B/f)
 for f in ['glyphs','refined','build/fonts','references']:shutil.copytree(O/f,B/f)
font=B/'build/fonts/HakilandDisplay-Regular.ttf'
corpus={
'rounds':['Oo0 CcGg Qq','BbDdPpRr 689','CeOe GgQq 0O'],
'verticals':['HhIiJjLlTt 1Il','bdfhkl bdqp','minimum parallel'],
'diagonals':['AaVvWwXxYyZz','KkRrNnMm 247','Vivid waves zigzag'],
'details':['i j . , : ; ! ? …','ftrg “Quoted”','AaRrGg QO'],
'words':['Angular grace','Quiet geometry.','Shape & proportion','We align. We refine.'],
'figures':['0123456789','1.25 / 7.50 / 9.99','09:47 — 17.09.2026'],
}
records=[]
for group,texts in corpus.items():
 for size,scale in [(64,3),(24,1)]:
  y=15;w=0;parts=[]
  for t in texts:
   shape=shape_font(font,t,{'kern':True,'liga':False});r=ET.fromstring(compose_preview_svg(font,p,shape,font_size=size,guides=False));r.set('y',str(y));w=max(w,int(r.attrib['width']));parts.append(ET.tostring(r,encoding='unicode'));y+=int(r.attrib['height'])+6
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{y}"><rect width="100%" height="100%" fill="white"/>'+''.join(parts)+'</svg>'
  stem=f'{group}-{size}';(D/f'{stem}.svg').write_text(svg);(D/f'{stem}.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=scale))
  records.append(dict(proof=stem,texts=texts,size=size,pixel_scale=scale,features={'kern':True,'liga':False},font_sha256=hashlib.sha256(font.read_bytes()).hexdigest(),revision=i['revision']))
f=TTFont(font);g=f.getGlyphSet();bounds={}
for cp,name in f.getBestCmap().items():
 pen=BoundsPen(g);g[name].draw(pen);bounds[chr(cp)]=dict(bounds=pen.bounds,advance=f['hmtx'][name][0],lsb=f['hmtx'][name][1])
(D/'bounds.json').write_text(json.dumps(bounds,indent=2));(D/'records.json').write_text(json.dumps(records,indent=2))
print(json.dumps({'revision':i['revision'],'proofs':len(records),'baseline':str(B)}))

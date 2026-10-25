from pathlib import Path
import shutil,json,hashlib
from fontTools.ttLib import TTFont
from font_maker.service import FontMakerService
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
from xml.etree import ElementTree as ET
D=Path(__file__).resolve().parent; O=D.parent
s=FontMakerService();i=s.open_project(str(O));store,p=s._store_project(i['project_id'])
assert p.font.version=='0.112',p.font.version
selected={'7':D/'figures/seven-C.svg','d':D/'lower/d-778.svg'}
for folder in ['caps','marks']:
 for path in (D/folder/'candidate-svg').glob('glyph-U*.svg'):selected[chr(int(path.stem[7:],16))]=path
assert set(selected)==set('7dS$!,. :;?…'.replace(' ','')),selected
items=[]
for c,path in selected.items():
 cp=f'U+{ord(c):04X}'; name=next(n for n,g in p.glyphs.items() if cp in g.codepoints);g=p.glyphs[name]
 dst=O/f'refined/glyph-U{ord(c):04X}.svg';shutil.copy2(path,dst)
 item=dict(name=name,svg_path=str(dst),codepoints=g.codepoints,advance_width=g.advance_width,left_side_bearing=g.left_side_bearing,right_side_bearing=g.right_side_bearing);items.append(item)
p.font.version='0.113';rev=store.save(p,i['revision']);mutation=s.upsert_glyphs(i['project_id'],rev,items)
built=s.build(i['project_id'],['ttf','otf','woff2']);(O/'build-report.json').write_text(json.dumps(built,indent=2,default=str));(O/'last-build.log').write_text(json.dumps(built,indent=2,default=str))
font=O/'build/fonts/HakilandDisplay-Regular.ttf';before=O/'revisions/before-weight-audit/build/fonts/HakilandDisplay-Regular.ttf'
f=TTFont(font);b=TTFont(before);changed=[]
assert f.getBestCmap()==b.getBestCmap()
assert f.getGlyphOrder()==b.getGlyphOrder()
for name in f.getGlyphOrder():
 assert f['hmtx'][name][0]==b['hmtx'][name][0],name
 if f['glyf'][name].compile(f['glyf'])!=b['glyf'][name].compile(b['glyf']):changed.append(name)
assert set(changed)=={item['name'] for item in items},changed
for tag in ['GPOS','GSUB']:assert f.getTableData(tag)==b.getTableData(tag),tag
for text in ['We Welcome','0123456789 17:47 $77.70','SHAPES bad dad','Yes. No, wait; 12:30!','fl fk fb fh office']:
 old=shape_font(before,text,{'kern':True,'liga':False});new=shape_font(font,text,{'kern':True,'liga':False});assert old==new,text
p=s._store_project(i['project_id'])[1]
record=dict(revision=mutation.revision,version=p.font.version,changed=changed,selected_sources={c:str(path) for c,path in selected.items()},sha256=hashlib.sha256(font.read_bytes()).hexdigest(),unchanged={'advance_widths':True,'cmap':True,'GPOS':True,'GSUB':True,'all_other_outlines':True},diagnostics=built['diagnostics'])
(D/'integration.json').write_text(json.dumps(record,indent=2,ensure_ascii=False))
def line(ft,t,x,y,size):
 svg=ET.fromstring(compose_preview_svg(ft,p,shape_font(ft,t,{'kern':True,'liga':False}),font_size=size,guides=False));m=max(16,int(size*.25));base=m+size*.8
 return f'<g transform="translate({x-m} {y-base})">'+''.join(ET.tostring(e,encoding='unicode') for e in svg if e.tag.endswith('path'))+'</g>'
for size,scale in [(72,2),(24,1)]:
 parts=[];y=24;width=1050 if size==72 else 700
 for label,t in [('Figures','0123456789 147 777'),('Curves','SHAPES bad dad adapted'),('Punctuation','Yes. No, wait; $77.70?!')]:
  for ft,tag in [(before,'Before — 0.112'),(font,'After — 0.113')]:
   parts.append(f'<text x="24" y="{y}" font-family="Arial" font-size="12" fill="#70685e">{label} / {tag}</text>');y+=size+14
   parts.append(line(ft,t,24,y,size));y+=32
  y+=14
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y}"><rect width="100%" height="100%" fill="#f8f6ef"/>'+''.join(parts)+'</svg>'
 (D/f'final-comparison-{size}.svg').write_text(svg);(D/f'final-comparison-{size}.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=scale))
d=json.loads((O/'design.json').read_text());d['revision']=mutation.revision;d['user_refinements'].append('Perceived-weight audit: lighter7, S/$ middle band and d lower bowl; stronger small punctuation diamonds.');(O/'design.json').write_text(json.dumps(d,indent=2))
print(json.dumps(record,indent=2,ensure_ascii=False))

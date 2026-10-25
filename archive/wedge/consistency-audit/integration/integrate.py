from pathlib import Path
import json,shutil,hashlib
from xml.etree import ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from font_maker.service import FontMakerService
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
D=Path(__file__).resolve().parent;A=D.parent;O=A.parent;B=O/'revisions/before-consistency-audit'
s=FontMakerService();i=s.open_project(str(O));store,p=s._store_project(i['project_id']);assert p.font.version=='0.113'
selected={'7':D/'seven-T2.svg'}
for c in 'EFLNY':selected[c]=A/f'caps/glyph-U{ord(c):04X}.svg'
for c in 'fu':selected[c]=A/f'lower/glyph-U{ord(c):04X}.svg'
for c in '14':selected[c]=A/f'marks/candidate-svg/glyph-U{ord(c):04X}.svg'
items=[]
for c,src in selected.items():
 cp=f'U+{ord(c):04X}';name=next(n for n,g in p.glyphs.items() if cp in g.codepoints);g=p.glyphs[name];dst=O/f'refined/glyph-U{ord(c):04X}.svg';shutil.copy2(src,dst)
 items.append(dict(name=name,codepoints=g.codepoints,advance_width=g.advance_width,left_side_bearing=g.left_side_bearing,right_side_bearing=g.right_side_bearing,svg_path=str(dst)))
p.font.version='0.114';rev=store.save(p,i['revision']);res=s.upsert_glyphs(i['project_id'],rev,items);built=s.build(i['project_id'],['ttf','otf','woff2'])
for name in ['build-report.json','last-build.log']:(O/name).write_text(json.dumps(built,indent=2,default=str))
font=O/'build/fonts/HakilandDisplay-Regular.ttf';before=B/'build/fonts/HakilandDisplay-Regular.ttf';f,b=TTFont(font),TTFont(before)
assert f.getBestCmap()==b.getBestCmap();assert f.getGlyphOrder()==b.getGlyphOrder();changed=[]
for name in f.getGlyphOrder():
 assert f['hmtx'][name][0]==b['hmtx'][name][0],name
 if f['glyf'][name].compile(f['glyf'])!=b['glyf'][name].compile(b['glyf']):changed.append(name)
assert set(changed)=={item['name'] for item in items},changed
for tag in ['GPOS','GSUB']:assert f.getTableData(tag)==b.getTableData(tag),tag
metricdiff={n:[b['hmtx'][n],f['hmtx'][n]] for n in f.getGlyphOrder() if b['hmtx'][n]!=f['hmtx'][n]};assert metricdiff=={'u':[(588,26),(588,25)]},metricdiff
checks=['0123456789 147 747 777','HEFLNYI useful uniform','Angular grace 17:47','fl fk fb fh flower','We Welcome Wednesday']
for text in checks:assert shape_font(before,text,{'kern':True,'liga':False})==shape_font(font,text,{'kern':True,'liga':False})
p=s._store_project(i['project_id'])[1]
def line(ft,t,x,y,size):
 root=ET.fromstring(compose_preview_svg(ft,p,shape_font(ft,t,{'kern':True,'liga':False}),font_size=size,guides=False));m=max(16,int(size*.25));base=m+size*.8
 return f'<g transform="translate({x-m} {y-base})">'+''.join(ET.tostring(e,encoding='unicode') for e in root if e.tag.endswith('path'))+'</g>'
for size,scale in [(80,2),(24,1)]:
 parts=[];y=25;w=1100 if size==80 else 700
 for t in ['0123456789 147 747','HEFLNYI useful uniform','Angular grace 17:47']:
  for ft,label in [(before,'Before — 0.113'),(font,'After — 0.114')]:
   parts.append(f'<text x="24" y="{y}" font-family="Arial" font-size="12" fill="#726b62">{label}</text>');y+=size+12;parts.append(line(ft,t,24,y,size));y+=33
  y+=10
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{y}"><rect width="100%" height="100%" fill="#f8f6ef"/>'+''.join(parts)+'</svg>'
 (O/f'consistency-comparison-{size}.svg').write_text(svg);(O/f'consistency-comparison-{size}.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=scale))
# Compact 7 proof makes the taper and its relationship to 4 directly reviewable.
parts=[]
for y,label,ft in [(28,'Before — uniform width',before),(246,'After — finer entry, fuller lower stroke',font)]:
 parts.append(f'<text x="28" y="{y}" font-family="Arial" font-size="14" fill="#726b62">{label}</text>');parts.append(line(ft,'147 747 777',28,y+155,180))
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="465"><rect width="100%" height="100%" fill="#f8f6ef"/>'+''.join(parts)+'</svg>'
(O/'seven-taper-comparison.svg').write_text(svg);(O/'seven-taper-comparison.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=1))
design=json.loads((O/'design.json').read_text());design['revision']=res.revision;design['user_refinements'].append('Consistency pass: related upright serif cuts aligned; f/u wedge family harmonized;1/4 feet aligned and4 top on cap line;7 deliberately tapered toward a fuller base per user direction.');(O/'design.json').write_text(json.dumps(design,indent=2))
record=dict(version='0.114',revision=res.revision,font_sha256=hashlib.sha256(font.read_bytes()).hexdigest(),changed=changed,selected_sources={c:str(src) for c,src in selected.items()},invariants={'all_advances_unchanged':True,'cmap_unchanged':True,'GPOS_unchanged':True,'GSUB_unchanged':True,'all_other_outlines_unchanged':True},metric_differences=metricdiff,diagnostics=built['diagnostics'])
(D/'integration.json').write_text(json.dumps(record,indent=2,ensure_ascii=False));print(json.dumps(record,indent=2,ensure_ascii=False))

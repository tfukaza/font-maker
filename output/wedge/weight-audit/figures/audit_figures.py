from pathlib import Path
import shutil, uuid, json, hashlib, html, math
from xml.etree import ElementTree as ET
from fontTools.ttLib import TTFont
from font_maker.service import FontMakerService
from font_maker.preview import shape_font, compose_preview_svg, svg_to_png
D=Path(__file__).resolve().parent; O=D.parents[1]
s=FontMakerService(); info=s.open_project(str(O)); _,p=s._store_project(info['project_id'])
B=O/'revisions/before-weight-audit'
if not B.exists():
 B.mkdir()
 for f in ['font.yaml','build-report.json','browser-review.json','design.json','quality-report.json','specimen.html','specimen.png','HakilandDisplay-Package.zip']:
  if (O/f).exists(): shutil.copy2(O/f,B/f)
 for f in ['glyphs','refined','build/fonts','references']: shutil.copytree(O/f,B/f)
base=B/'build/fonts/HakilandDisplay-Regular.ttf'
records=[]
def sheet(name,rows,size=96,scale=2):
 parts=[]; w=0;y=0
 for label,text,font in rows:
  shape=shape_font(font,text,{'kern':True,'liga':False})
  el=ET.fromstring(compose_preview_svg(font,p,shape,font_size=size,guides=False));el.set('x','0');el.set('y',str(y+24))
  parts.append(f'<text x="16" y="{y+18}" font-family="Arial" font-size="13">{html.escape(label)}</text>')
  parts.append(ET.tostring(el,encoding='unicode'));w=max(w,int(el.attrib['width']));y+=int(el.attrib['height'])+30
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{y}"><rect width="100%" height="100%" fill="white"/>'+''.join(parts)+'</svg>'
 (D/f'{name}.svg').write_text(svg);(D/f'{name}.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=scale))
 records.append(dict(proof=name,font_size=size,pixel_scale=scale,rows=[dict(label=l,text=t,font=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for l,t,f in rows]))
paths={}
for c in '0123456789':
 path=O/f'refined/glyph-U{ord(c):04X}.svg'
 if not path.exists(): path=O/f'drawings/glyph-U{ord(c):04X}.svg'
 paths[c]=dict(path=str(path),svg=path.read_text())
(D/'paths.json').write_text(json.dumps(paths,indent=2))
variants={'Before':base}; measures={}
for name,thick,bar in [('A',116,109),('B',116,92),('C',108,92)]:
 slope=235/677; left=276-thick*math.sqrt(1+slope*slope); top=100+bar; inner=left+slope*(800-top)
 # Preserve 45-degree wedge cut as the top bar rises.
 corner=36+308-top
 path=D/f'seven-{name}.svg'
 path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1040" data-fontmaker-baseline-y="800"><g id="glyph" fill="#000"><path d="M39 100H511V123L276 800H{left:.4f}L{inner:.4f} {top}H{corner}L36 308L39 100Z"/></g></svg>')
 trial=D/f'trial-{name}';trial.mkdir(exist_ok=True)
 shutil.copy2(B/'font.yaml',trial/'font.yaml');shutil.copytree(B/'glyphs',trial/'glyphs',dirs_exist_ok=True);shutil.copytree(B/'references',trial/'references',dirs_exist_ok=True)
 svc=FontMakerService(); ti=svc.open_project(str(trial));store,pr=svc._store_project(ti['project_id']);pr.project_id=str(uuid.uuid4());rev=store.save(pr,ti['revision']);ti=svc.open_project(str(trial))
 rev=svc.upsert_glyphs(ti['project_id'],ti['revision'],[dict(name='seven',svg_path=str(path),codepoints=['U+0037'],advance_width=546)]).revision
 built=svc.build(ti['project_id'],['ttf']); font=trial/built['artifacts'][0]['path'];variants[name]=font
 measures[name]=dict(normal_diagonal=thick,top_bar=bar,baseline_left=left,inner_top_x=inner,source=str(path),font=str(font),revision=rev)
sheet('seven-options',[(f'{name}'+(' — original' if name=='Before' else f' — diagonal {measures[name]["normal_diagonal"]}, top bar {measures[name]["top_bar"]}'),'0123456789',font) for name,font in variants.items()],110,2)
sheet('seven-detail',[(name,'147 777',font) for name,font in variants.items()],170,2)
sheet('seven-native',[(name,'0123456789 17:47 $77.70 777',font) for name,font in variants.items()],24,1)
for i,text in enumerate(['0011223344','5566778899','H1H 147 471 714','06 68 89 98 23 35','Edition 07 / 17.09.2026']):
 sheet(f'figure-baseline-{i+1}',[('Current figures — 0.112',text,base)],110,2)
(D/'measurements.json').write_text(json.dumps(measures,indent=2));(D/'proof-records.json').write_text(json.dumps(records,indent=2))
print(json.dumps(measures,indent=2))

from pathlib import Path
import shutil,uuid,json,math,html,hashlib
from xml.etree import ElementTree as ET
from font_maker.service import FontMakerService
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
D=Path(__file__).resolve().parent;O=D.parents[1];B=O/'revisions/before-consistency-audit'
s=FontMakerService();info=s.open_project(str(O));p=s._store_project(info['project_id'])[1]
fonts={'Current':B/'build/fonts/HakilandDisplay-Regular.ttf'};measures={}
for label,normal,bar in [('A',96,76),('B',88,68),('C',80,60)]:
 slope=235/677;left=276-normal*math.sqrt(1+slope*slope);y=100+bar;inner=left+slope*(800-y);corner=36+308-y
 path=D/f'seven-{label}.svg';path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1040" data-fontmaker-baseline-y="800"><g id="glyph" fill="#000"><path d="M39 100H511V123L276 800H{left:.4f}L{inner:.4f} {y}H{corner}L36 308L39 100Z"/></g></svg>')
 trial=D/f'trial-{label}';trial.mkdir(exist_ok=True)
 (trial/'font.yaml').write_text((B/'font.yaml').read_text().replace('project_id: d75e345b-b8f4-4b8f-a7d2-b0c1c7cbfb18',f'project_id: {uuid.uuid4()}'))
 for folder in ['glyphs','references']:shutil.copytree(B/folder,trial/folder,dirs_exist_ok=True)
 svc=FontMakerService();ti=svc.open_project(str(trial));res=svc.upsert_glyphs(ti['project_id'],ti['revision'],[dict(name='seven',codepoints=['U+0037'],advance_width=546,svg_path=str(path))]);built=svc.build(ti['project_id'],['ttf']);fonts[label]=trial/built['artifacts'][0]['path'];measures[label]={'diagonal':normal,'bar':bar,'left_baseline':left,'source':str(path),'font':str(fonts[label])}
def proof(name,text,size,scale):
 w=0;y=0;parts=[]
 for label,font in fonts.items():
  r=ET.fromstring(compose_preview_svg(font,p,shape_font(font,text,{'kern':True,'liga':False}),font_size=size,guides=False));r.set('x','0');r.set('y',str(y+22));w=max(w,int(r.attrib['width']))
  detail='108 / 92 — current' if label=='Current' else f'{measures[label]["diagonal"]} / {measures[label]["bar"]}'
  parts.append(f'<text x="16" y="{y+16}" font-family="Arial" font-size="12">{label} — diagonal / bar: {detail}</text>');parts.append(ET.tostring(r,encoding='unicode'));y+=int(r.attrib['height'])+26
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{y}"><rect width="100%" height="100%" fill="white"/>'+''.join(parts)+'</svg>'
 (D/f'{name}.svg').write_text(svg);(D/f'{name}.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=scale))
proof('seven-options','0123456789',100,2)
proof('seven-context','147 777 $77.70',92,2)
proof('seven-native','0123456789 17:47 777',24,1)
(D/'seven-trials.json').write_text(json.dumps(measures,indent=2));print(json.dumps(measures,indent=2))

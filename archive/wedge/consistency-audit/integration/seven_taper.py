from pathlib import Path
import shutil,uuid,json,math
from xml.etree import ElementTree as ET
from font_maker.service import FontMakerService
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
D=Path(__file__).resolve().parent;O=D.parents[1];B=O/'revisions/before-consistency-audit'
s=FontMakerService();i=s.open_project(str(O));p=s._store_project(i['project_id'])[1]
fonts={'Current':B/'build/fonts/HakilandDisplay-Regular.ttf'};measures={}
for label,upper,lower,bar,curved in [('T1',44,104,38,False),('T2',44,112,38,True),('T3',56,120,44,True)]:
 slope=235/677;n=math.sqrt(1+slope*slope);top=100+bar;dy=800-top;righttop=511-(top-123)*slope;lefttop=righttop-upper*n;leftbottom=276-lower*n;corner=36+308-top
 # Quadratic width progression w(t)=upper+(lower-upper)*t^2, with y(t) linear,
 # expressed as an exact cubic. Main right edge retains the source slope.
 dx=-slope*dy;delta=(lower-upper)*n
 c1=(lefttop+dx/3,top+dy/3);c2=(lefttop+2*dx/3-delta/3,top+2*dy/3)
 inner=f'C{c2[0]:.4f} {c2[1]:.4f} {c1[0]:.4f} {c1[1]:.4f} {lefttop:.4f} {top}' if curved else f'L{lefttop:.4f} {top}'
 path=D/f'seven-{label}.svg';path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1040" data-fontmaker-baseline-y="800"><g id="glyph" fill="#000"><path d="M39 100H511V123L276 800H{leftbottom:.4f}{inner}H{corner}L36 308L39 100Z"/></g></svg>')
 trial=D/f'trial-{label}';trial.mkdir(exist_ok=True);(trial/'font.yaml').write_text((B/'font.yaml').read_text().replace('project_id: d75e345b-b8f4-4b8f-a7d2-b0c1c7cbfb18',f'project_id: {uuid.uuid4()}'))
 for folder in ['glyphs','references']:shutil.copytree(B/folder,trial/folder,dirs_exist_ok=True)
 svc=FontMakerService();ti=svc.open_project(str(trial));res=svc.upsert_glyphs(ti['project_id'],ti['revision'],[dict(name='seven',codepoints=['U+0037'],advance_width=546,svg_path=str(path))]);built=svc.build(ti['project_id'],['ttf']);fonts[label]=trial/built['artifacts'][0]['path'];measures[label]=dict(upper_width=upper,lower_width=lower,top_bar=bar,profile='quadratic' if curved else 'linear',svg=str(path),font=str(fonts[label]),lefttop=lefttop,leftbottom=leftbottom,controls=[c1,c2] if curved else [])
def proof(name,text,size,scale):
 y=0;w=0;parts=[]
 for label,font in fonts.items():
  r=ET.fromstring(compose_preview_svg(font,p,shape_font(font,text,{'kern':True,'liga':False}),font_size=size,guides=False));r.set('y',str(y+24));w=max(w,int(r.attrib['width']))
  detail='108 uniform / 92 bar' if label=='Current' else f'{measures[label]["upper_width"]} to {measures[label]["lower_width"]} / {measures[label]["top_bar"]} bar / {measures[label]["profile"]}'
  parts.append(f'<text x="16" y="{y+17}" font-family="Arial" font-size="12">{label} — {detail}</text>');parts.append(ET.tostring(r,encoding='unicode'));y+=int(r.attrib['height'])+28
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{y}"><rect width="100%" height="100%" fill="white"/>'+''.join(parts)+'</svg>'
 (D/f'{name}.svg').write_text(svg);(D/f'{name}.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=scale))
proof('taper-options','0123456789',100,2);proof('taper-context','147 747 777',126,2);proof('taper-native','0123456789 17:47 $77.70',24,1)
(D/'taper-trials.json').write_text(json.dumps(measures,indent=2));print(json.dumps(measures,indent=2))

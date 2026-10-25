from pathlib import Path
import shutil,uuid,json,hashlib
from font_maker.service import FontMakerService
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
from fontTools.ttLib import TTFont
from xml.etree import ElementTree as ET
OUT=Path(__file__).parent.resolve();ROOT=OUT.parents[1]
trial=OUT/'trial-project';trial.mkdir(exist_ok=True)
if not (trial/'font.yaml').exists():
 shutil.copy2(ROOT/'font.yaml',trial/'font.yaml');shutil.copytree(ROOT/'glyphs',trial/'glyphs');shutil.copytree(ROOT/'references',trial/'references')
 s=FontMakerService();info=s.open_project(str(trial));store,p=s._store_project(info['project_id']);p.project_id=str(uuid.uuid4());p.font.family_name='Hakiland Display Weight Study';store.save(p,info['revision'])
s=FontMakerService();info=s.open_project(str(trial));pid=info['project_id'];rev=info['revision'];p=s._store_project(pid)[1]
source=(ROOT/'refined/glyph-U0064.svg').read_text()
fonts=[('Current d',OUT/'baseline.ttf')]
records=[]
for label,low,innerhandle,end in [('d-770',770,691,703),('d-778',778,699,709)]:
 txt=source.replace('160.0 677.0 205.0 753.0 287.0 753.0C333.0 753.0 362.0 734.0 392.0 690.0',f'160.0 {innerhandle}.0 205.0 {low}.0 287.0 {low}.0C333.0 {low}.0 362.0 {low-19}.0 392.0 {end}.0')
 assert txt!=source
 src=OUT/(label+'.svg');src.write_text(txt)
 rev=s.upsert_glyphs(pid,rev,[dict(name='d',svg_path=str(src),codepoints=['U+0064'],advance_width=582)]).revision
 result=s.build(pid,['ttf']);built=trial/result['artifacts'][0]['path'];dest=OUT/(label+'.ttf');shutil.copy2(built,dest);fonts.append((label,dest));records.append({'candidate':label,'revision':rev,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
def proof(name,texts,size,scale):
 width=1050;height=(len(texts)*len(fonts))*(size+45)+15;svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="#faf8f2"/>'];y=12
 for txt in texts:
  for label,font in fonts:
   svg.append(f'<text x="20" y="{y+13}" font-family="sans-serif" font-size="12">{label}</text>');base=y+28+size*.8
   tree=ET.fromstring(compose_preview_svg(font,p,shape_font(font,txt,{'kern':True,'liga':False}),font_size=size,guides=False));m=max(16,int(size*.25));oldbase=m+size*.8
   body=''.join(ET.tostring(e,encoding='unicode') for e in tree if e.tag.endswith('path'));svg.append(f'<g transform="translate({20-m} {base-oldbase})">{body}</g>');y+=size+45
 svg.append('</svg>');data=''.join(svg).encode();(OUT/(name+'.svg')).write_bytes(data);(OUT/(name+'.png')).write_bytes(svg_to_png(data,pixel_scale=scale))
proof('d-comparison',['b d q o d d','bad dad adapted paddle'],90,2)
proof('d-native',['bad dad adapted paddle','odod bdbd pqpq'],24,1)
(OUT/'d-trial.json').write_text(json.dumps(records,indent=2))

from pathlib import Path
import json, math, shutil, uuid
from xml.etree import ElementTree as ET
from font_maker.service import FontMakerService
from font_maker.preview import shape_font, compose_preview_svg, svg_to_png

D = Path(__file__).resolve().parent
O = D.parents[1]
s = FontMakerService()
info = s.open_project(str(O))
p = s._store_project(info['project_id'])[1]
fonts = {'Tapered 0.114': O/'build/fonts/HakilandDisplay-Regular.ttf'}
measurements = {}
for label, width, bar in [('108 / 24',108,24), ('108 / 20',108,20), ('114 / 24',114,24)]:
    slug = label.replace(' / ','-')
    top = 100+bar
    # Preserve the established outside edge and parallel full-width diagonal.
    # A 20-unit bar requires its outside knee at y=120 rather than y=123.
    knee = min(123,top)
    slope = (511-276)/(800-knee)
    offset = width*math.sqrt(1+slope*slope)
    leftbottom = 276-offset
    lefttop = 511-(top-knee)*slope-offset
    corner = 36+308-top
    path = D/f'seven-contrast-{slug}.svg'
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1040" data-fontmaker-baseline-y="800"><g id="glyph" fill="#000"><path d="M39 100H511V{knee}L276 800H{leftbottom:.4f}L{lefttop:.4f} {top}H{corner}L36 308L39 100Z"/></g></svg>')
    trial = D/f'trial-contrast-{slug}'
    trial.mkdir(exist_ok=True)
    import yaml
    manifest = yaml.safe_load((O/'font.yaml').read_text())
    manifest['project_id'] = str(uuid.uuid4())
    (trial/'font.yaml').write_text(yaml.safe_dump(manifest,sort_keys=False))
    for folder in ['glyphs','references']:
        shutil.copytree(O/folder,trial/folder,dirs_exist_ok=True)
    svc = FontMakerService()
    ti = svc.open_project(str(trial))
    svc.upsert_glyphs(ti['project_id'],ti['revision'],[dict(name='seven',codepoints=['U+0037'],advance_width=546,svg_path=str(path))])
    built = svc.build(ti['project_id'],['ttf'])
    fonts[label] = trial/built['artifacts'][0]['path']
    measurements[label] = dict(diagonal=width,bar=bar,svg=str(path),font=str(fonts[label]))

for name,text,size,scale in [('contrast-options','147 747 777',150,2),('contrast-figures','0123456789',90,3),('contrast-native','0123456789 17:47 $77.70',24,1)]:
    y=0; width=0; parts=[]
    for label,font in fonts.items():
        r=ET.fromstring(compose_preview_svg(font,p,shape_font(font,text,{'kern':True,'liga':False}),font_size=size,guides=False))
        r.set('y',str(y+26)); width=max(width,int(r.attrib['width']))
        parts.append(f'<text x="16" y="{y+19}" font-family="Arial" font-size="13">{label}</text>')
        parts.append(ET.tostring(r,encoding='unicode')); y+=int(r.attrib['height'])+35
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y}"><rect width="100%" height="100%" fill="#f8f6ef"/>'+''.join(parts)+'</svg>'
    (D/f'{name}.svg').write_text(svg)
    (D/f'{name}.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=scale))
(D/'contrast-trials.json').write_text(json.dumps(measurements,indent=2))
print(json.dumps(measurements,indent=2))

from pathlib import Path
from xml.etree import ElementTree as ET
from font_maker.service import FontMakerService
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
OUT=Path(__file__).parent.resolve();s=FontMakerService();i=s.open_project(str(OUT/'trial-project'));p=s._store_project(i['project_id'])[1]
for c,txt in [('f','l f i f'),('u','n u d u')]:
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="550" height="380"><rect width="100%" height="100%" fill="#faf8f2"/>']
 for j,(label,file) in enumerate([('Before0.113','baseline.ttf'),('Aligned wedge candidate','candidate.ttf')]):
  font=OUT/file;size=160;m=40;base=168;y=20+j*180
  svg.append(f'<text x="20" y="{y}" font-family="sans-serif" font-size="11">{label}</text>')
  tree=ET.fromstring(compose_preview_svg(font,p,shape_font(font,txt,{'kern':True,'liga':False}),font_size=size,guides=False))
  body=''.join(ET.tostring(e,encoding='unicode') for e in tree if e.tag.endswith('path'));svg.append(f'<g transform="translate(-20 {y+145-base})">{body}</g>')
 svg.append('</svg>');data=''.join(svg).encode();(OUT/f'{c}-detail.svg').write_bytes(data);(OUT/f'{c}-detail.png').write_bytes(svg_to_png(data,pixel_scale=3))

from pathlib import Path
from xml.etree import ElementTree as ET
from font_maker.service import FontMakerService
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];s=FontMakerService();p=s._store_project(s.open_project(str(ROOT))['project_id'])[1]
fonts=[('Current 0.113',OUT/'baseline.ttf'),('Aligned figure wedges',OUT/'trial/build/fonts/HakilandDisplay-Regular.ttf')]
lines=['H1I  1414  H4H  4545  4747','0123456789  $14.41', '11:44  1914  41%  No. 14']
for size in [96,56,24]:
 width=1600 if size==96 else 1100 if size==56 else 620;lineheight=size*1.5+15;height=(len(lines)*2)*(lineheight+25)+50
 chunks=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#faf8f2"/>']
 row=0
 for line in lines:
  for label,font in fonts:
   y=35+row*(lineheight+25);chunks.append(f'<text x="24" y="{y}" font-family="Arial" font-size="12" fill="#766d62">{label}</text>')
   tree=ET.fromstring(compose_preview_svg(font,p,shape_font(font,line,{'kern':True,'liga':False}),font_size=size,guides=False));margin=max(16,int(size*.25));base=margin+.8*size
   paths=''.join(ET.tostring(e,encoding='unicode') for e in tree if e.tag.endswith('path'))
   chunks.append(f'<g transform="translate({24-margin} {y+size+10-base})">{paths}</g>');row+=1
 chunks.append('</svg>');data=''.join(chunks).encode();(OUT/f'compare-{size}.svg').write_bytes(data);(OUT/f'compare-{size}.png').write_bytes(svg_to_png(data,pixel_scale=1 if size==24 else 2))

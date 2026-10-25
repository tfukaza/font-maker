from pathlib import Path
import json,hashlib,shutil,html
from xml.etree import ElementTree as ET
from font_maker.service import FontMakerService
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
service=FontMakerService();info=service.open_project(str(ROOT));project=service._store_project(info['project_id'])[1]
font=OUT/'baseline.ttf';shutil.copy2(ROOT/'build/fonts/HakilandDisplay-Regular.ttf',font)
cmap=TTFont(font).getBestCmap();chars=list('abcdefghijklmnopqrstuvwxyz')
records=[];sources=[]
for index,c in enumerate(chars):
    name=cmap[ord(c)];glyph=project.glyphs[name]
    override=ROOT/'refined'/f'glyph-U{ord(c):04X}.svg';draw=ROOT/'drawings'/f'glyph-U{ord(c):04X}.svg';source=override if override.exists() else draw if draw.exists() else ROOT/glyph.source
    records.append({'character':c,'codepoint':f'U+{ord(c):04X}','glyph':name,'source':str(source.relative_to(ROOT)),'advance':glyph.advance_width,'sheet':index//10+1,'visual':'pending','geometry':'pending','observation':''})
    sources.append(f'\n{ord(c):04X} {repr(c)} {source.relative_to(ROOT)} advance {glyph.advance_width}\n{source.read_text()}')
for sheet in range((len(chars)+9)//10):
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="540" viewBox="0 0 1100 540"><rect width="100%" height="100%" fill="#faf8f2"/>']
    for cell,c in enumerate(chars[sheet*10:sheet*10+10]):
        x=20+(cell%5)*220;y=32+(cell//5)*260
        svg.append(f'<text x="{x}" y="{y}" font-family="Arial" font-size="14" fill="#655f55">U+{ord(c):04X} / {html.escape(repr(c))}</text>')
        size=160;tree=ET.fromstring(compose_preview_svg(font,project,shape_font(font,c,{'kern':True,'liga':False}),font_size=size,guides=False))
        m=40;base=m+800*.16
        svg.append(f'<path d="M{x} {y+166}h190" stroke="#e0dbd0"/>')
        body=''.join(ET.tostring(e,encoding='unicode') for e in tree if e.tag.endswith('path'))
        svg.append(f'<g transform="translate({x-m+18} {y+166-base})">{body}</g>')
    svg.append('</svg>');data=''.join(svg).encode();(OUT/f'sheet-{sheet+1}.svg').write_bytes(data);(OUT/f'sheet-{sheet+1}.png').write_bytes(svg_to_png(data,pixel_scale=2))
(OUT/'paths.txt').write_text('\n'.join(sources));(OUT/'review.json').write_text(json.dumps({'revision':info['revision'],'font_sha256':hashlib.sha256(font.read_bytes()).hexdigest(),'font_size':160,'pixel_scale':2,'glyphs':records},indent=2,ensure_ascii=False))
print(len(records),'glyphs')

lines=['nonono minimum maximum', 'navigating middle window', 'avid waxy vivify swaying', 'bad dad adapted paddle', 'joining joyful inquiry', 'rough graphic figure', 'successful frisky stories', 'abcdefghijklmnopqrstuvwxyz']
for size,scale in [(56,2),(24,1)]:
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="680" viewBox="0 0 1400 680"><rect width="100%" height="100%" fill="#faf8f2"/>']
    for i,text in enumerate(lines):
        tree=ET.fromstring(compose_preview_svg(font,project,shape_font(font,text,{'kern':True,'liga':False}),font_size=size,guides=False))
        m=max(16,int(size*.25));base=m+800*size/1000
        body=''.join(ET.tostring(e,encoding='unicode') for e in tree if e.tag.endswith('path'))
        svg.append(f'<g transform="translate({24-m} {50+i*78-base})">{body}</g>')
    svg.append('</svg>');data=''.join(svg).encode();(OUT/f'context-{size}.svg').write_bytes(data);(OUT/f'context-{size}.png').write_bytes(svg_to_png(data,pixel_scale=scale))

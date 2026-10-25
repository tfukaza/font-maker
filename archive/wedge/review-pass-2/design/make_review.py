from pathlib import Path
import string,json,hashlib
from xml.etree import ElementTree as ET
from font_maker.preview import compose_preview_svg,shape_font,svg_to_png
from font_maker.service import FontMakerService
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
OUT=Path('output/wedge');DEST=OUT/'review-pass-2/design'
font=OUT/'build/fonts/HakilandDisplay-Regular.ttf'
s=FontMakerService();info=s.open_project(str(OUT.resolve()));p=s._store_project(info['project_id'])[1]
def line(t,x,y,size):
 svg=compose_preview_svg(font,p,shape_font(font,t,{'kern':True,'liga':False}),font_size=size,guides=False)
 r=ET.fromstring(svg);margin=max(16,int(size*.25));base=margin+800*size/1000
 body=''.join(ET.tostring(e,encoding='unicode') for e in r if e.tag.endswith('path'))
 return f'<g transform="translate({x-margin} {y-base})">{body}</g>'
chars=string.ascii_uppercase+string.ascii_lowercase
records={};tt=TTFont(font);gs=tt.getGlyphSet();cm=tt.getBestCmap()
for start in range(0,len(chars),6):
 group=chars[start:start+6]
 pieces=['<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="850" viewBox="0 0 1140 850"><rect width="1140" height="850" fill="#f8f6ef"/>']
 for i,c in enumerate(group):
  x=30+(i%3)*380;y=30+(i//3)*410
  pieces.append(f'<text x="{x}" y="{y+18}" font-family="sans-serif" font-size="15" fill="#777">{c} · U+{ord(c):04X} · 220 / 36 / 24px</text>')
  pieces.append(line(c,x+20,y+206,220))
  control='H'+c+'OH' if c.isupper() else 'n'+c+'on'
  pieces.append(line(control,x+20,y+300,36));pieces.append(line(control,x+20,y+338,24))
  pieces.append(f'<path d="M{x} {y+376}h340" stroke="#ccc"/>')
 pieces.append('</svg>');svg=''.join(pieces).encode();n=f'alphabet-{start//6+1:02}'
 (DEST/'proofs'/f'{n}.svg').write_bytes(svg);(DEST/'proofs'/f'{n}.png').write_bytes(svg_to_png(svg,pixel_scale=1))
for c in chars:
 candidate=OUT/f'refined/glyph-U{ord(c):04X}.svg'
 if not candidate.exists():candidate=OUT/f'drawings/glyph-U{ord(c):04X}.svg'
 bp=BoundsPen(gs);gs[cm[ord(c)]].draw(bp)
 records[c]={'authoritative_source':str(candidate),'source_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'compiled_bounds':bp.bounds,'advance_lsb':tt['hmtx'][cm[ord(c)]],'proof':f'proofs/alphabet-{chars.index(c)//6+1:02}.png'}
(DEST/'manifest.json').write_text(json.dumps({'font_sha256':hashlib.sha256(font.read_bytes()).hexdigest(),'revision':info['revision'],'glyphs':records},indent=2))
for n,t in {'caps-use':'HAKILAND DISPLAY. QUIET WOVEN GEOMETRY.','lower-use':'Angular grace. A woven world. Sharp rhythm.','details-use':'aadd bdqp agag ijij minimum QOQQ RARA','diagonals-use':'WAVY WAX VOW XX vvwwxx yy'}.items():
 svg=compose_preview_svg(font,p,shape_font(font,t,{'kern':True,'liga':False}),font_size=32,guides=False)
 (DEST/'proofs'/f'{n}.svg').write_bytes(svg);(DEST/'proofs'/f'{n}.png').write_bytes(svg_to_png(svg,pixel_scale=1))

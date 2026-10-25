from pathlib import Path
import string,json,hashlib
from xml.etree import ElementTree as ET
from font_maker.preview import compose_preview_svg,shape_font,svg_to_png
from font_maker.service import FontMakerService
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
OUT=Path('output/wedge');DEST=OUT/'weight-audit/caps';(DEST/'proofs').mkdir(exist_ok=True)
font=OUT/'build/fonts/HakilandDisplay-Regular.ttf'
s=FontMakerService();info=s.open_project(str(OUT.resolve()));p=s._store_project(info['project_id'])[1]
def line(t,x,y,size):
 svg=compose_preview_svg(font,p,shape_font(font,t,{'kern':True,'liga':False}),font_size=size,guides=False)
 r=ET.fromstring(svg);margin=max(16,int(size*.25));base=margin+800*size/1000
 body=''.join(ET.tostring(e,encoding='unicode') for e in r if e.tag.endswith('path'))
 return f'<g transform="translate({x-margin} {y-base})">{body}</g>'
words=['ANGULAR','BOLD','CURVE','DISPLAY','EDGE','FINE','GRACE','HARD','INK','JOIN','KINK','LINE','MINIMAL','NARROW','OVAL','PARALLEL','QUIET','RHYTHM','SHAPE','TYPE','UNITY','VIVID','WOVEN','EXACT','YELLOW','ZIGZAG']
records={};tt=TTFont(font);gs=tt.getGlyphSet();cm=tt.getBestCmap()
for start in range(0,26,4):
 group=string.ascii_uppercase[start:start+4]
 pieces=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="860" viewBox="0 0 1100 860"><rect width="1100" height="860" fill="#f8f6ef"/>']
 for i,c in enumerate(group):
  x=24+(i%2)*550;y=24+(i//2)*420
  pieces.append(f'<text x="{x}" y="{y+18}" font-family="sans-serif" font-size="15" fill="#777">{c} apparent weight: 180 / 56 / native 24px</text>')
  pieces.append(line('H'+c+'O',x+10,y+178,180))
  pieces.append(line('H'+c+'O'+c+'V',x+10,y+270,56))
  pieces.append(line('H'+c+'O'+c+'V '+words[start+i],x+10,y+320,24))
  pieces.append(f'<path d="M{x} {y+374}h500" stroke="#ccc"/>')
 pieces.append('</svg>');svg=''.join(pieces).encode();n=f'caps-{start//4+1:02}'
 (DEST/'proofs'/f'{n}.svg').write_bytes(svg);(DEST/'proofs'/f'{n}.png').write_bytes(svg_to_png(svg,pixel_scale=1))
for c in string.ascii_uppercase:
 source=OUT/f'refined/glyph-U{ord(c):04X}.svg'
 if not source.exists():source=OUT/f'drawings/glyph-U{ord(c):04X}.svg'
 bp=BoundsPen(gs);gs[cm[ord(c)]].draw(bp)
 records[c]={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'compiled_bounds':bp.bounds,'advance_lsb':tt['hmtx'][cm[ord(c)]],'proof':f'proofs/caps-{string.ascii_uppercase.index(c)//4+1:02}.png'}
(DEST/'manifest.json').write_text(json.dumps({'font_sha256':hashlib.sha256(font.read_bytes()).hexdigest(),'revision':info['revision'],'sizes_px':[180,56,24],'pixel_scale':1,'glyphs':records},indent=2))
for size in [56,24]:
 pieces=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600"><rect width="100%" height="100%" fill="#f8f6ef"/>']
 for i,text in enumerate(['HAKILAND DISPLAY','ANGULAR GRACE','BOLD MINIMAL SHAPES','QUIET WOVEN GEOMETRY','VIVID RHYTHM EXACT JOINS','ABCDEFGHIJKLMNOPQRSTUVWXYZ']):pieces.append(line(text,24,70+i*88,size))
 pieces.append('</svg>');svg=''.join(pieces).encode();(DEST/'proofs'/f'context-{size}.svg').write_bytes(svg);(DEST/'proofs'/f'context-{size}.png').write_bytes(svg_to_png(svg,pixel_scale=1))

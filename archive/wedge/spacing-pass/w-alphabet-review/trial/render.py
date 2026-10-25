from pathlib import Path
import string,html,json,hashlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from font_maker.preview import shape_font,svg_to_png
P=Path('output/wedge/spacing-pass/w-alphabet-review/trial'); F=P/'trial.ttf'
font=TTFont(F); gs=font.getGlyphSet(); order=font.getGlyphOrder()
pairs=list(dict.fromkeys(['W'+c for c in string.ascii_uppercase+string.ascii_lowercase]+[c+'W' for c in string.ascii_uppercase+string.ascii_lowercase]))
def paths(text,x,y,size):
 s=shape_font(F,text); out=[]; scale=size/1000
 for g in s['glyphs']:
  n=g['glyph_name'] if g['glyph_name'] in gs else order[g['glyph_id']]
  pen=SVGPathPen(gs); gs[n].draw(pen)
  out.append(f'<path d="{pen.getCommands()}" fill="#141310" transform="translate({x+g["x_offset"]*scale} {y-g["y_offset"]*scale}) scale({scale} {-scale})"/>')
  x+=g['x_advance']*scale
 return ''.join(out)
review=[]
for page in range((len(pairs)+27)//28):
 ps=pairs[page*28:(page+1)*28]
 pieces=['<svg xmlns="http://www.w3.org/2000/svg" width="1360" height="1230" viewBox="0 0 1360 1230"><rect width="100%" height="100%" fill="#faf8f1"/>',f'<text x="20" y="30" font-size="19" font-family="sans-serif">Hakiland Display — trial W permutations — sheet {page+1}/4</text>']
 for i,pair in enumerate(ps):
  x=20+(i%4)*335;y=52+(i//4)*166
  on=shape_font(F,pair)['total_advance']; off=shape_font(F,pair,{'kern':False})['total_advance']; k=on-off
  review.append({'pair':pair,'kern':k})
  pieces.append(f'<text x="{x}" y="{y+14}" font-size="15" font-family="sans-serif">{pair}  kern {k:+}</text>')
  pieces.append(paths(pair,x,y+100,100))
  pieces.append(paths('nn'+pair+'nn',x,y+142,28))
 pieces.append('</svg>');svg=''.join(pieces).encode();(P/f'sheet-{page+1}.svg').write_bytes(svg);(P/f'sheet-{page+1}.png').write_bytes(svg_to_png(svg,pixel_scale=1))
(P/'pairs.json').write_text(json.dumps({'font_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'pair_count':len(pairs),'pairs':review},indent=2))
print(f'Rendered {len(pairs)} pairs, 4 sheets')

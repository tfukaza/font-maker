from pathlib import Path
from xml.etree import ElementTree as ET
import shutil,json,hashlib
from font_maker.service import FontMakerService
from font_maker.preview import compose_preview_svg,shape_font,svg_to_png
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
ROOT=Path('output/wedge/weight-audit/caps').resolve();OUT=ROOT.parents[1];d=ROOT/'candidate-svg';d.mkdir(exist_ok=True)
src=(ROOT/'glyph-U0053-minus8.svg').read_text();(d/'glyph-U0053.svg').write_text(src)
bar='M290.0 899.0V14.0H317.0V899.0H290.0Z '
(d/'glyph-U0024.svg').write_text(src.replace('Z "/></g>','Z '+bar+'"/></g>'))
assert bar in (d/'glyph-U0024.svg').read_text()
s=FontMakerService();info=s.open_project(str(ROOT/'trial-project'));pid=info['project_id'];p=s._store_project(pid)[1]
items=[]
for c,name in [('S','S'),('$','dollar')]:
 items.append({'name':name,'codepoints':[f'U+{ord(c):04X}'],'advance_width':p.glyphs[name].advance_width,'svg_path':str(d/f'glyph-U{ord(c):04X}.svg')})
change=s.upsert_glyphs(pid,info['revision'],items);result=s.build(pid,['ttf']);font=ROOT/'trial-project'/result['artifacts'][0]['path'];shutil.copy2(font,ROOT/'S-dollar-final.ttf');font=ROOT/'S-dollar-final.ttf';base=OUT/'build/fonts/HakilandDisplay-Regular.ttf'
b=TTFont(base);a=TTFont(font);bgs=b.getGlyphSet();ags=a.getGlyphSet();changed=[]
for name in bgs.keys():
 bp=RecordingPen();ap=RecordingPen();bgs[name].draw(bp);ags[name].draw(ap)
 if bp.value!=ap.value:changed.append(name)
assert set(changed)=={'S','dollar'},changed
assert b['hmtx'].metrics==a['hmtx'].metrics
assert b.getBestCmap()==a.getBestCmap()
assert b['GPOS'].compile(b)==a['GPOS'].compile(a)
assert b['GSUB'].compile(b)==a['GSUB'].compile(a)
for name in ['S','dollar']:
 for attr in ['xMin','xMax','yMin','yMax']:assert getattr(b['glyf'][name],attr)==getattr(a['glyf'][name],attr)
def line(t,x,y,size,ft):
 svg=compose_preview_svg(ft,p,shape_font(ft,t,{'kern':True,'liga':False}),font_size=size,guides=False);r=ET.fromstring(svg);margin=max(16,int(size*.25));baseline=margin+800*size/1000
 body=''.join(ET.tostring(e,encoding='unicode') for e in r if e.tag.endswith('path'))
 return f'<g transform="translate({x-margin} {y-baseline})">{body}</g>'
for size,scale in [(120,1),(24,1)]:
 step=size*1.5+70;pieces=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1250" height="{step*2+20}"><rect width="100%" height="100%" fill="#f8f6ef"/>']
 for i,(label,ft) in enumerate([('Before',base),('S and dollar waist refined',font)]):
  y=24+i*step;pieces.append(f'<text x="24" y="{y}" font-family="sans-serif" font-size="15">{label} — {size}px</text>');pieces.append(line('S$S $12.50 $50.00',24,y+size+30,size,ft))
 pieces.append('</svg>');svg=''.join(pieces).encode();(ROOT/'proofs'/f'S-dollar-{size}.svg').write_bytes(svg);(ROOT/'proofs'/f'S-dollar-{size}.png').write_bytes(svg_to_png(svg,pixel_scale=scale))
report={'trial_font':str(font),'sha256':hashlib.sha256(font.read_bytes()).hexdigest(),'changed_outlines':changed,'hmtx_unchanged':True,'cmap_unchanged':True,'GPOS_unchanged':True,'GSUB_unchanged':True,'bounds_unchanged':True,'validation':result.get('validation',result.get('findings',[]))}
(ROOT/'candidate-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

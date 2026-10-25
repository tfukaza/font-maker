from pathlib import Path
import shutil,uuid,json,hashlib
from xml.etree import ElementTree as ET
from font_maker.preview import compose_preview_svg,shape_font,svg_to_png
from font_maker.service import FontMakerService
OUT=Path('output/wedge').resolve();ROOT=OUT/'weight-audit/caps'
font=OUT/'build/fonts/HakilandDisplay-Regular.ttf';s=FontMakerService();info=s.open_project(str(OUT));p=s._store_project(info['project_id'])[1]
trial=ROOT/'trial-project';trial.mkdir(exist_ok=True)
(trial/'font.yaml').write_text((OUT/'font.yaml').read_text().replace('d75e345b-b8f4-4b8f-a7d2-b0c1c7cbfb18',str(uuid.uuid4())))
shutil.copytree(OUT/'glyphs',trial/'glyphs',dirs_exist_ok=True);shutil.copytree(OUT/'references',trial/'references',dirs_exist_ok=True)
variants=[('Current',font)]
for delta in [8,12]:
 path=ROOT/f'glyph-U0053-minus{delta}.svg'
 src=(OUT/'drawings/glyph-U0053.svg').read_text()
 for old,new in [
 ('174.0 286.0 221.0 321.0 327.0 369.0',f'174.0 286.0 221.0 {321+delta}.0 327.0 {369+delta}.0'),
 ('L393.0 399.0',f'L393.0 {399+delta}.0'),
 ('505.0 450.0 568.0 510.0',f'505.0 {450+delta}.0 568.0 {510+delta/2:.1f}'),
 ('459.0 601.0 411.0 565.0 312.0 520.0',f'459.0 {601-delta/2:.1f} 411.0 {565-delta}.0 312.0 {520-delta}.0'),
 ('L241.0 487.0',f'L241.0 {487-delta}.0'),
 ('129.0 436.0 70.0 372.0',f'129.0 {436-delta}.0 70.0 {372-delta/2:.1f}')]:
  assert old in src;src=src.replace(old,new)
 path.write_text(src)
 ts=FontMakerService();ti=ts.open_project(str(trial));pr=ts._store_project(ti['project_id'])[1]
 changed=ts.upsert_glyphs(ti['project_id'],ti['revision'],[{'name':'S','svg_path':str(path),'codepoints':['U+0053'],'advance_width':pr.glyphs['S'].advance_width}])
 result=ts.build(ti['project_id'],['ttf']);built=trial/result['artifacts'][0]['path'];copy=ROOT/f'S-minus{delta}.ttf';shutil.copy2(built,copy);variants.append((f'S lighter waist {delta}',copy))

def line(t,x,y,size,ft):
 svg=compose_preview_svg(ft,p,shape_font(ft,t,{'kern':True,'liga':False}),font_size=size,guides=False)
 r=ET.fromstring(svg);margin=max(16,int(size*.25));base=margin+800*size/1000
 body=''.join(ET.tostring(e,encoding='unicode') for e in r if e.tag.endswith('path'))
 return f'<g transform="translate({x-margin} {y-base})">{body}</g>'
for size,scale in [(140,1),(64,3),(24,1)]:
 width=1400 if size==140 else 1100;height=3*(size*1.5+60)+25
 pieces=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="#f8f6ef"/>']
 for i,(label,ft) in enumerate(variants):
  y=25+i*(size*1.5+60)
  pieces.append(f'<text x="20" y="{y+15}" font-family="sans-serif" font-size="15" fill="#777">{label} — {size}px / {scale}x</text>')
  text='HSSOS ZSXS' if size==140 else 'HSSOS SHAPES DISPLAY STRESS'
  pieces.append(line(text,24,y+size*1.1+30,size,ft))
 pieces.append('</svg>');svg=''.join(pieces).encode();(ROOT/'proofs'/f'S-comparison-{size}.svg').write_bytes(svg);(ROOT/'proofs'/f'S-comparison-{size}.png').write_bytes(svg_to_png(svg,pixel_scale=scale))
print(json.dumps({'variants':[(a,str(b),hashlib.sha256(b.read_bytes()).hexdigest()) for a,b in variants]},indent=2))

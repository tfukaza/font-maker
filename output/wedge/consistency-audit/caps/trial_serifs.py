from pathlib import Path
import shutil,uuid,json,hashlib
from xml.etree import ElementTree as ET
from font_maker.preview import compose_preview_svg,shape_font,svg_to_png
from font_maker.service import FontMakerService
O=Path('output/wedge').resolve();R=O/'consistency-audit/caps';trial=R/'trial-project';trial.mkdir(exist_ok=True)
font=O/'build/fonts/HakilandDisplay-Regular.ttf';s=FontMakerService();info=s.open_project(str(O));p=s._store_project(info['project_id'])[1]
(trial/'font.yaml').write_text((O/'font.yaml').read_text().replace(p.project_id,str(uuid.uuid4())))
shutil.copytree(O/'glyphs',trial/'glyphs',dirs_exist_ok=True);shutil.copytree(O/'references',trial/'references',dirs_exist_ok=True)
changes={
'E':[('90.0 751.0','90.0 746.0'),('V147.0','V154.0')],
'F':[('V751.0','V746.0'),('90.0 751.0','90.0 746.0'),('V147.0','V154.0')],
'L':[('206.0 147.0','206.0 154.0'),('90.0 751.0','90.0 746.0'),('V147.0','V154.0')],
'N':[('641.0 616.0V148.0','641.0 616.0V154.0'),('665.0 148.0','665.0 155.0'),('118.0 177.0V752.0','118.0 177.0V746.0'),('94.0 752.0','94.0 746.0'),('94.0 752.0','94.0 746.0'),('94.0 746.0V150.0','94.0 746.0V154.0')],
'Y':[('421.0 479.0V751.0','421.0 479.0V746.0'),('305.0 751.0','305.0 746.0')]
}
# precise token replacement, with explicit correction for repeated N replacement above
changes['N'].pop(4)
inputs=[]
for c,repls in changes.items():
 path=O/f'drawings/glyph-U{ord(c):04X}.svg';src=path.read_text()
 for a,b in repls:
  assert a in src,(c,a);src=src.replace(a,b)
 dst=R/f'glyph-U{ord(c):04X}.svg';dst.write_text(src)
 rec=p.glyphs[c];inputs.append({'name':c,'svg_path':str(dst),'codepoints':[f'U+{ord(c):04X}'],'advance_width':rec.advance_width})
ts=FontMakerService();ti=ts.open_project(str(trial));changed=ts.upsert_glyphs(ti['project_id'],ti['revision'],inputs);result=ts.build(ti['project_id'],['ttf']);built=trial/result['artifacts'][0]['path'];candidate=R/'serif-candidate.ttf';shutil.copy2(built,candidate)
def line(t,x,y,size,ft):
 svg=compose_preview_svg(ft,p,shape_font(ft,t,{'kern':True,'liga':False}),font_size=size,guides=False)
 r=ET.fromstring(svg);m=max(16,int(size*.25));body=''.join(ET.tostring(e,encoding='unicode') for e in r if e.tag.endswith('path'))
 return f'<g transform="translate({x-m} {y-m-800*size/1000})">{body}</g>'
for size,scale,text in [(160,1,'H E F L N Y I'),(56,3,'HELENE FLY FINE YIELD'),(24,1,'HELENE FLY FINE YIELD HAKILAND DISPLAY')]:
 h=2*(size*1.2+60)+20;w=1100 if size!=24 else 800
 a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="100%" height="100%" fill="#f8f6ef"/>']
 for i,(label,f) in enumerate([('Current 0.113',font),('45 degree attached straight-stem serif cuts',candidate)]):
  y=25+i*(size*1.2+60);a.append(f'<text x="20" y="{y}" font-family="sans-serif" font-size="14" fill="#777">{label}: {size}px, {scale}x</text>');a.append(line(text,20,y+size*.9+10,size,f))
 a.append('</svg>');svg=''.join(a).encode();base=R/'proofs'/f'serif-comparison-{size}';base.with_suffix('.svg').write_bytes(svg);base.with_suffix('.png').write_bytes(svg_to_png(svg,pixel_scale=scale))
# source detail 1:1 1000px em produces honest join enlargement, with crop only around left heads/feet
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="680"><rect width="100%" height="100%" fill="#f8f6ef"/>']
for i,(lab,f) in enumerate([('Current',font),('Candidate',candidate)]):
 for j,c in enumerate('HEFLNY'):
  x=30+j*182;y=60+i*320
  svg.append(f'<text x="{x}" y="{y-20}" font-family="sans-serif" font-size="14">{lab} {c}</text>')
  # compile paths in masked little viewport, enlarged3x with actual glyph leftmost attachment source coordinates
  raw=compose_preview_svg(f,p,shape_font(f,c,{'kern':False,'liga':False}),font_size=1000,guides=False)
  r=ET.fromstring(raw);body=''.join(ET.tostring(e,encoding='unicode') for e in r if e.tag.endswith('path'))
  # all paths raw origin margin250, top350. Crop head for H E F L N; foot Y
  xcrop=250+(235 if c=='Y' else 20);ycrop=250+(700 if c=='Y' else 80)
  svg.append(f'<svg x="{x}" y="{y}" width="155" height="250" viewBox="{xcrop} {ycrop} 155 250">{body}</svg>')
svg.append('</svg>');b=''.join(svg).encode();(R/'proofs/serif-detail.svg').write_bytes(b);(R/'proofs/serif-detail.png').write_bytes(svg_to_png(b,pixel_scale=1))
(R/'trial.json').write_text(json.dumps({'result':result,'changes':changes,'candidate':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest()},indent=2))
print(result)

from pathlib import Path
import shutil,uuid,json,hashlib
from font_maker.service import FontMakerService
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
from fontTools.ttLib import TTFont
from xml.etree import ElementTree as ET
OUT=Path(__file__).parent.resolve();ROOT=OUT.parents[1]
trial=OUT/'trial-project';trial.mkdir(exist_ok=True)
if not (trial/'font.yaml').exists():
 txt=(ROOT/'font.yaml').read_text().replace('project_id: d75e345b-b8f4-4b8f-a7d2-b0c1c7cbfb18','project_id: '+str(uuid.uuid4())).replace('family_name: Hakiland Display','family_name: Hakiland Consistency Study')
 (trial/'font.yaml').write_text(txt);shutil.copytree(ROOT/'glyphs',trial/'glyphs');shutil.copytree(ROOT/'references',trial/'references')
s=FontMakerService();info=s.open_project(str(trial));pid=info['project_id'];rev=info['revision'];p=s._store_project(pid)[1]
source_u=(ROOT/'drawings/glyph-U0075.svg').read_text()
u=source_u.replace('M26.0 366.0 187.0 320.0','M25.0 374.0 187.0 320.0').replace('V408.0L347.0 366.0L508.0 320.0V752.0H559.0L402.0 810.0','V430.0L346.0 374.0L508.0 320.0V758.0H564.0L402.0 812.0').replace('V407.0L26.0 366.0','V430.0L25.0 374.0')
source_f=(ROOT/'drawings/glyph-U0066.svg').read_text()
f=source_f.replace('V758.0L258.0 800.0H34.0L89.0 758.0','V746.0L249.0 800.0H35.0L89.0 746.0')
assert f!=source_f and u!=source_u
(OUT/'glyph-U0075.svg').write_text(u);(OUT/'glyph-U0066.svg').write_text(f)
changes=[dict(name=c,svg_path=str(OUT/f'glyph-U{ord(c):04X}.svg'),codepoints=[f'U+{ord(c):04X}'],advance_width=p.glyphs[c].advance_width) for c in 'fu']
rev=s.upsert_glyphs(pid,rev,changes).revision
validation=s.validate(pid,temporary_build=True)
result=s.build(pid,['ttf']);built=trial/result['artifacts'][0]['path'];dest=OUT/'candidate.ttf';shutil.copy2(built,dest)
fonts=[('Before — 0.113',OUT/'baseline.ttf'),('Candidate — aligned wedge families',dest)]
def proof(name,texts,size,scale):
 width=1050;height=(len(texts)*len(fonts))*(size+40)+15;svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="#faf8f2"/>'];y=12
 for txt in texts:
  for label,font in fonts:
   svg.append(f'<text x="20" y="{y+13}" font-family="sans-serif" font-size="12">{label}</text>');base=y+27+size*.8
   tree=ET.fromstring(compose_preview_svg(font,p,shape_font(font,txt,{'kern':True,'liga':False}),font_size=size,guides=False));m=max(16,int(size*.25));oldbase=m+size*.8
   body=''.join(ET.tostring(e,encoding='unicode') for e in tree if e.tag.endswith('path'));svg.append(f'<g transform="translate({20-m} {base-oldbase})">{body}</g>');y+=size+40
 svg.append('</svg>');data=''.join(svg).encode();(OUT/(name+'.svg')).write_bytes(data);(OUT/(name+'.png')).write_bytes(svg_to_png(data,pixel_scale=scale))
proof('uf-comparison',['n u h u d u','l f i f h f','useful uniform truthful'],96,2)
proof('uf-native',['n u h u d u  l f i f h f','useful uniform truthful','full fluid furthest unique'],24,1)
old,new=[TTFont(font) for _,font in fonts]
from fontTools.pens.recordingPen import RecordingPen
oldset,newset=old.getGlyphSet(),new.getGlyphSet();diff=[]
for c,name in old.getBestCmap().items():
 a,b=RecordingPen(),RecordingPen();oldset[name].draw(a);newset[new.getBestCmap()[c]].draw(b)
 if a.value!=b.value:diff.append(chr(c))
assert diff==['f','u'],diff
metric_diffs={n:[v,new['hmtx'].metrics[n]] for n,v in old['hmtx'].metrics.items() if new['hmtx'].metrics[n]!=v}
assert metric_diffs=={'u':[(588,26),(588,25)]},metric_diffs
assert all(v[0]==new['hmtx'].metrics[n][0] for n,v in old['hmtx'].metrics.items())
assert old.getTableData('GPOS')==new.getTableData('GPOS')
(OUT/'trial.json').write_text(json.dumps({'revision':rev,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'changed':diff,'same_advances':True,'metric_diffs':metric_diffs,'same_GPOS':True,'validation':[d.model_dump(mode='json') for d in validation],'build':result},indent=2))
print('Compiled f/u candidate; contours changed only f/u, advances/GPOS preserved; u LSB26 to25 follows new extremum')

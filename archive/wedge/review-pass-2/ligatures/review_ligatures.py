from pathlib import Path
import hashlib,json,html,shutil,uuid
from xml.etree import ElementTree as ET
from fontTools.ttLib import TTFont
from font_maker.preview import shape_font,compose_preview_svg,svg_to_png
from font_maker.service import FontMakerService
from font_maker.models import KerningPair
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]
FONT=SOURCE/'build/fonts/HakilandDisplay-Regular.ttf'
s=FontMakerService(); opened=s.open_project(str(SOURCE)); project=s._store_project(opened['project_id'])[1]
original_rev=opened['revision']; original_hash=hashlib.sha256(FONT.read_bytes()).hexdigest()
records=[]
def sheet(stem,rows,size=64,scale=3):
 pieces=[]; y=12; width=0
 for label,text,font,features,revision in rows:
  shape=shape_font(font,text,features)
  svg=ET.fromstring(compose_preview_svg(font,project,shape,font_size=size,guides=False))
  svg.set('x','0');svg.set('y',str(y+18))
  pieces.append(f'<text x="16" y="{y+10}" font-family="sans-serif" font-size="10">{html.escape(label)}</text>')
  pieces.append(ET.tostring(svg,encoding='unicode'));width=max(width,int(svg.attrib['width']));y+=int(svg.attrib['height'])+34
  records.append(dict(label=label,text=text,revision=revision,font=str(font),sha256=hashlib.sha256(font.read_bytes()).hexdigest(),features=features,size=size,scale=scale,shaping=shape,proof=stem,status='generated'))
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y}"><rect width="100%" height="100%" fill="white"/>'+''.join(pieces)+'</svg>'
 (ROOT/(stem+'.svg')).write_text(svg);(ROOT/(stem+'.png')).write_bytes(svg_to_png(svg.encode(),pixel_scale=scale))
OFF={'kern':False,'liga':False,'rlig':False,'dlig':False};ON={**OFF,'kern':True}
for group,lines in {
'f-family':['fi fl ff ffi ffl ft fj fk','profile flower office official','difficult affluent offline fifty','after oft fjord offkey'],
'font-specific':['Qu Qa Qo Qy Queue Quartz','ra ri ro rr rare river error','tt st ct letter pasta actor','nn mm nm minimum manner','AV VA AW WA wave away']}.items():
 for n,text in enumerate(lines):
  sheet(f'baseline-{group}-{n+1}',[("No kerning",text,FONT,OFF,original_rev),("Current kerning",text,FONT,ON,original_rev)])
 sheet(f'baseline-{group}-native',[("Current kerning — native 24 px",text,FONT,ON,original_rev) for text in lines],24,1)
(ROOT/'source.json').write_text(json.dumps(dict(source=opened,sha256=original_hash),indent=2))
(ROOT/'records.json').write_text(json.dumps(records,indent=2))
print(ROOT)
trial=ROOT/'trial-project'
if not trial.exists():
 trial.mkdir()
 shutil.copy2(SOURCE/'font.yaml',trial/'font.yaml')
 shutil.copytree(SOURCE/'glyphs',trial/'glyphs')
 shutil.copytree(SOURCE/'references',trial/'references')
 clone=FontMakerService(); ci=clone.open_project(str(trial)); store,p=clone._store_project(ci['project_id'])
 p.project_id=str(uuid.uuid4());p.font.family_name='Hakiland Display Ligature Spacing Study'
 rev=store.save(p,ci['revision'])
clone=FontMakerService();ci=clone.open_project(str(trial)); pid=ci['project_id']; rev=ci['revision']
proposal={seq:24 for seq in ['fb','fh','fk','fl']}
rev=clone.set_kerning(pid,rev,upsert_pairs=[KerningPair(left=k[0],right=k[1],value=v) for k,v in proposal.items()]).revision
build=clone.build(pid,['ttf']); trial_font=trial/build['artifacts'][0]['path']
base_font=TTFont(FONT); alt_font=TTFont(trial_font)
assert set(base_font.getGlyphOrder())==set(alt_font.getGlyphOrder())
for g in base_font.getGlyphOrder():
 assert base_font['glyf'][g].compile(base_font['glyf'])==alt_font['glyf'][g].compile(alt_font['glyf']),g
 assert base_font['hmtx'][g]==alt_font['hmtx'][g],g
for n,text in enumerate(['fl fk fb fh','flower flow offline affluent','offkey offbeat offhand','aflo efko ffh (fl) flfl.','fi fj ff ffi ft difficult']):
 sheet(f'spacing-trial-{n+1}', [('Current kerning',text,FONT,ON,original_rev),('Spacing-only +24 units: fb fh fk fl',text,trial_font,ON,rev)],64,3)
 if n in [1,2]:
  sheet(f'spacing-trial-native-{n+1}', [('Current kerning — 24 px',text,FONT,ON,original_rev),('Spacing-only +24 — 24 px',text,trial_font,ON,rev)],24,1)
# f_l/f_k upper terminal detail distinguishes a designed join from accidental contact.
sheet('spacing-terminal-detail',[('Current kerning','fl fk',FONT,ON,original_rev),('Spacing-only +24','fl fk',trial_font,ON,rev)],180,4)
for text in ['fl','fk','fb','fh','flfl','affluent','offhand','difficult']:
 orig=shape_font(FONT,text,ON); alt=shape_font(trial_font,text,ON)
 assert [(g['glyph_name'],g['cluster']) for g in orig['glyphs']]==[(g['glyph_name'],g['cluster']) for g in alt['glyphs']]
 assert alt['total_advance']-orig['total_advance']==24*sum(text.count(seq) for seq in proposal)
(root_report:=ROOT/'trial.json').write_text(json.dumps(dict(project=ci,revision=rev,font=str(trial_font),sha256=hashlib.sha256(trial_font.read_bytes()).hexdigest(),scoped_differences={'family':'isolated study','kerning':proposal},outlines_and_metrics_identical=True,ligatures=0),indent=2))
(ROOT/'records.json').write_text(json.dumps(records,indent=2))

from pathlib import Path
import uuid,shutil,json,re
from font_maker.service import FontMakerService
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
trial=OUT/'trial';trial.mkdir(exist_ok=True)
for name in ['glyphs','references']:
 shutil.copytree(ROOT/name,trial/name,dirs_exist_ok=True)
s=(ROOT/'font.yaml').read_text();s=re.sub(r'project_id: .*',f'project_id: {uuid.uuid4()}',s);(trial/'font.yaml').write_text(s)
CAND=OUT/'candidate-svg';CAND.mkdir(exist_ok=True)
svc=FontMakerService();info=svc.open_project(str(trial));project=svc._store_project(info['project_id'])[1]
items=[]
for c in '14':
 cp=ord(c);name=next(n for n,g in project.glyphs.items() if f'U+{cp:04X}' in g.codepoints);g=project.glyphs[name]
 src=ROOT/'drawings'/f'glyph-U{cp:04X}.svg';content=src.read_text()
 if c=='1':
  content=content.replace('V752.0L326.0 800.0H79.0L146.0 752.0','V734.0L326.0 800.0H80.0L146.0 734.0')
 else:
  content=content.replace('346.0 88.0','346.0 100.0').replace('V757.0L514.0','V746.0L514.0').replace('L346.0 757.0','L346.0 746.0').replace('V139.0','V143.1847')
 assert content!=src.read_text()
 dest=CAND/f'glyph-U{cp:04X}.svg';dest.write_text(content)
 items.append({'name':name,'codepoints':[f'U+{cp:04X}'],'advance_width':g.advance_width,'svg_path':str(dest)})
res=svc.upsert_glyphs(info['project_id'],info['revision'],items);result=svc.build(info['project_id'],['ttf'])
(OUT/'candidate-build.json').write_text(json.dumps(result,indent=2,default=str));print(result)

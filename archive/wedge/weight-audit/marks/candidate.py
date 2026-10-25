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
def dot(x,bottom=800):
 return f'M{x} {bottom-92} {x+46} {bottom-46} {x} {bottom} {x-46} {bottom-46}Z'
def comma(x):
 return f'M{x} 708 {x+46} 754C{x+46} 824 {x+14} 879 {x-51} 915L{x-61} 903C{x-14} 864 {x-1} 829 {x} 800L{x-46} 754Z'
items=[]
for c in '!,. :;?…'.replace(' ',''):
 cp=ord(c);name=next(n for n,g in project.glyphs.items() if f'U+{cp:04X}' in g.codepoints);g=project.glyphs[name]
 src=ROOT/'drawings'/f'glyph-U{cp:04X}.svg';content=src.read_text();d=re.search(r'<path d="([^"]+)"',content).group(1)
 if c=='!':d=d[:d.index('M126.0 722.0')]+dot(126)
 elif c=='?':d=d[:d.index('M235.0 722.0')]+dot(235)
 elif c==',':d=comma(100)
 elif c==';':d=comma(109)+dot(109,485)
 elif c==':':d=dot(109)+dot(109,485)
 elif c=='.':d=dot(100)
 elif c=='…':d=''.join(dot(x) for x in [100,300,500])
 content=re.sub(r'<path d="[^"]+"',lambda m:f'<path d="{d}"',content,count=1)
 dest=CAND/f'glyph-U{cp:04X}.svg';dest.write_text(content)
 items.append({'name':name,'codepoints':[f'U+{cp:04X}'],'advance_width':g.advance_width,'svg_path':str(dest)})
res=svc.upsert_glyphs(info['project_id'],info['revision'],items)
result=svc.build(info['project_id'],['ttf'])
(OUT/'candidate-build.json').write_text(json.dumps(result,indent=2,default=str))
print(result)

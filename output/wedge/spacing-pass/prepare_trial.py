from pathlib import Path
import shutil,json
from ruamel.yaml import YAML
root=Path(__file__).parent
src=root/'baseline-project'
dst=root/'trial-project'
if not dst.exists():shutil.copytree(src,dst)
y=YAML(); p=y.load((dst/'font.yaml').read_text())
k={'AV':-95,'AW':-90,'AY':-105,'AT':-90,'VA':-90,'WA':-80,'YA':-105,'TA':-95,'LT':-100,'LV':-90,'LW':-85,'LY':-105,'FA':-65,'PA':-65,'Tr':-55,'Tu':-55,'Ty':-45,'Tv':-45,'Tw':-45,'Vr':-25,'Vu':-25,'Wr':-12,'Wu':-12,'Yr':-55,'Yu':-55,'Yv':-30,'Yw':-30}
for c in 'acegos':
 for left,v in [('T',-85),('V',-62),('W',-45),('Y',-90)]:k[left+c]=v
for c in 'aeo':
 for left,v in [('v',-22),('w',-16),('y',-18)]: k[left+c]=v
for c in 'vwy':
 for left,v in [('o',-14),('e',-12),('a',-8)]: k[left+c]=v
for left,v in [('V',-100),('W',-85),('Y',-85),('T',-80),('r',-40),('v',-50),('w',-50),('y',-50)]:
 for right in '.,':k[left+right]=v
cmap={chr(int(cp[2:],16)):name for name,data in p['glyphs'].items() for cp in data['codepoints']}
pairs={(z['left'],z['right']):z['value'] for z in p['kerning']['pairs']}
for pair,value in k.items():pairs[cmap[pair[0]],cmap[pair[1]]]=value
p['kerning']['pairs']=[{'left':left,'right':right,'value':value} for (left,right),value in pairs.items()]
with (dst/'font.yaml').open('w') as f:y.dump(p,f)
(root/'trial-1.json').write_text(json.dumps({'advance_overrides':{},'kerning_overrides':k},indent=2)+'\n')

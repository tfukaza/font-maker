from pathlib import Path
import shutil,json,importlib.util
from ruamel.yaml import YAML
root=Path(__file__).parent; src=root.parent; dst=root/'final-project';dst.mkdir()
shutil.copy2(src/'font.yaml',dst/'font.yaml');shutil.copytree(src/'glyphs',dst/'glyphs')
y=YAML(); p=y.load((dst/'font.yaml').read_text()); proposals=json.loads((src/'spacing-refinement.json').read_text())
for c,v in proposals['advance_overrides'].items():p['glyphs'][c]['advance_width']=v
for c,v in proposals['left_side_bearing_overrides'].items():p['glyphs'][c]['left_side_bearing']=v
cmap={chr(int(cp[2:],16)):name for name,data in p['glyphs'].items() for cp in data['codepoints']}
pairs={(z['left'],z['right']):z['value'] for z in p['kerning']['pairs']}
for pair,value in proposals['kerning_overrides'].items():pairs[cmap[pair[0]],cmap[pair[1]]]=value
p['kerning']['pairs']=[{'left':left,'right':right,'value':value} for (left,right),value in pairs.items()]
with (dst/'font.yaml').open('w') as f:y.dump(p,f)
spec=importlib.util.spec_from_file_location('proof','skills/font-spacing-kerning/scripts/render_kerning_proofs.py'); mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
keys=list(proposals['kerning_overrides']);texts=[' '.join(keys[n:n+6]) for n in range(0,len(keys),6)]
mod.render_proofs(dst,out=root/'final-pairs',font_size=50,pixel_scale=3,sheet_width=640,rows_per_sheet=4,texts=texts,include_defaults=False)
words=['HHOO HOHO nnno nono','nanan onoan aaaa','rare radar parallel','wave away woven','AVATAR WAYWARD WATER','Typography Works: Quality.','jigsaw vivid minimum','a:a a;a a,a a.a','fifty affine flaw flint','rover worry rarely','Town Vowel Waves Yesterday.','Waxwork: Woven, away.']
mod.render_proofs(dst,out=root/'final-words',font_size=44,pixel_scale=3,sheet_width=640,rows_per_sheet=4,texts=words,include_defaults=False)
mod.render_proofs(dst,out=root/'final-reading',font_size=22,pixel_scale=1,sheet_width=640,rows_per_sheet=4,texts=['Angular grace: parallel waves.','Typography Works: Quality, Variety.','Woven away, rare radar, vivid jigsaw.','AVATAR WAYWARD WATER','a:a a;a a,a a.a A:A A;A A,A A.A','Town Vowel Waves Yesterday.'],include_defaults=False)
print('Final proof complete')

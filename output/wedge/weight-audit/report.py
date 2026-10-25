from pathlib import Path
import json,hashlib,shutil
from fontTools.ttLib import TTFont
from font_maker.preview import shape_font
D=Path(__file__).resolve().parent;O=D.parent
integration=json.loads((D/'integration.json').read_text());audit={};records=[]
for group in ['caps','lower','figures','marks']:
 r=json.loads((D/group/'review.json').read_text());audit[group]=r
 entries=r['glyphs']
 if isinstance(entries,dict): entries=[dict(character=k,**v) for k,v in entries.items()]
 for entry in entries:
  visual=entry.get('visual',entry.get('visual_review'));geometry=entry.get('geometry',entry.get('svg_review'))
  assert visual.startswith('inspected') and geometry.startswith('inspected'),(group,entry['character'],visual,geometry)
  e=dict(entry);e['review_group']=group
  c=e['character']; path=O/f'refined/glyph-U{ord(c):04X}.svg'
  if not path.exists():path=O/f'drawings/glyph-U{ord(c):04X}.svg'
  e['final_source']=str(path.relative_to(O));e['final_source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  e['integration_result']='refined and compiled comparison inspected' if c in integration['selected_sources'] else 'retained; exported outline unchanged'
  records.append(e)
font=O/'build/fonts/HakilandDisplay-Regular.ttf';cmap=TTFont(font).getBestCmap()
assert len(records)==103 and {ord(r['character']) for r in records}==set(cmap)
for size in [72,24]:
 for ext in ['svg','png']:shutil.copy2(D/f'final-comparison-{size}.{ext}',O/f'weight-comparison-{size}.{ext}')
checktexts=['0123456789 147 777','SHAPES bad dad adapted','Yes. No, wait; $77.70?!','We Welcome Wednesday','fl fk fb fh office']
formats={}
for ext in ['ttf','otf','woff2']:
 f=O/f'build/fonts/HakilandDisplay-Regular.{ext}';ft=TTFont(f);assert ft.getBestCmap()==cmap
 shape_path=f
 if ext=='woff2':
  shape_path=D/'decompressed-woff2.ttf';ft.flavor=None;ft.save(shape_path)
 shaped={t:shape_font(shape_path,t,{'kern':True,'liga':False}) for t in checktexts}
 for t,result in shaped.items():
  assert all(g['glyph_id'] for g in result['glyphs'])
  base=shape_font(font,t,{'kern':True,'liga':False})
  assert result['total_advance']==base['total_advance'],(ext,t)
 formats[ext]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'coverage':len(ft.getBestCmap()),'context_shaping_checked':checktexts}
report=dict(version=integration['version'],revision=integration['revision'],status='103 glyphs reviewed visually and through SVG geometry; 11 refined and final compiled comparisons inspected; user aesthetic acceptance pending',baseline_revision=audit['caps']['revision'],baseline_sha256=audit['caps']['font_sha256'],font_sha256=integration['sha256'],reviewed_count=103,changed_characters=list(integration['selected_sources']),retained_count=92,changes={'7':{'perpendicular_diagonal_units':[132.26,108],'top_bar_units':[109,92],'preserved':'parallel edges;45-degree wedge;546advance'},'S/$':{'central_normal_section_units':[143.49,128.95],'preserved':'extrema,terminals,dollar27-unitbar,advances'},'d':{'lower_bowl_section_units':[55.83,30.83],'preserved':'outercontour,leftsilhouette,106-unitstem,advance'},'punctuation':{'characters':'. , : ; ! ? …','diamond_diagonal_units':[78,92],'preserved':'45-degreecutfamily,baseline,advances'}},invariants=integration['unchanged'],formats=formats,final_proofs=['weight-comparison-72.png','weight-comparison-72.svg','weight-comparison-24.png','weight-comparison-24.svg'],method='Construction-family controls, individual compiled silhouettes, repeated forms, words and figures at display/native24px, followed by per-glyph SVG inspection. Local measures diagnose visual differences; no global stem equalization.',glyphs=records)
(O/'weight-review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
md='''# Hakiland Display — perceived stroke weight, version 0.113

All 103 encoded characters were reviewed by construction family, through the actual SVG paths and compiled specimens at display and native 24 px. Three subagents covered capitals, lowercase, and punctuation; the main pass covered all ten figures, compared proposed changes, and integrated the exports.

| Changed family | Correction | Preserved |
| --- | --- | --- |
| 7 | Long diagonal about 132→108 units perpendicular to its edges; top bar 109→92 | Parallel slope, 45° wedge, outer bounds, advance |
| S and $ | Central band about 143→129 units | Terminals, extrema, dollar bar, spacing |
| d | Lower bowl thickness about 56→31 units at the reviewed section | Outer silhouette and previous bulge repair |
| . , : ; ! ? … | Diamond/head size 78→92 units | Shared 45° cuts, baseline and advances |

The other 92 entries were retained. In particular, the recent w/diagonal compensation and larger i/j dots remain appropriate. Weight varies deliberately between upright, curved, diagonal, thick, and hairline families; the pass does not force equal geometry.

Before/after evidence: [display comparison](weight-comparison-72.png), [native 24 px comparison](weight-comparison-24.png), [complete per-glyph record](weight-review.json). Full diagnostic/trial proofs are under weight-audit/ in the workspace.

TTF, OTF and WOFF2 compile and shape the tested contexts. Coverage, all advances, kerning and substitution tables are unchanged. Only the 11 selected outlines changed. The previous 0.112 geometry review did not catch the optical-weight issues above and is superseded for those glyphs. The revised drawings remain subject to the user's aesthetic judgment.

The font metrics and serif skills now direct reviewers to audit every delivered construction family, including figures and symbols, and consider lightening as well as thickening strokes.
'''
old=(O/'review-notes.md').read_text();(O/'review-notes.md').write_text(md+'\n---\n\n## Previous pass (version 0.112)\n\n'+old)
(O/'weight-review.md').write_text(md)
print(json.dumps({'reviewed':len(records),'changed':report['changed_characters'],'formats':formats},indent=2,ensure_ascii=False))

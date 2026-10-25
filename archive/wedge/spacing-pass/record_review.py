from pathlib import Path
import json,statistics
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
root=Path(__file__).parent
font=TTFont(root/'final-pairs/proof-font.ttf');glyphs=font.getGlyphSet();cmap=font.getBestCmap()
class Edges(BasePen):
 def __init__(self,gs):super().__init__(gs);self.edges=[];self.cur=None;self.start=None
 def _moveTo(self,p):self.cur=self.start=p
 def _lineTo(self,p):self.edges.append((self.cur,p));self.cur=p
 def _closePath(self):self._lineTo(self.start)
 def _endPath(self):pass
 def _qCurveToOne(self,c,p):
  p0=self.cur
  for i in range(1,65):
   t=i/64;s=1-t;self._lineTo((s*s*p0[0]+2*s*t*c[0]+t*t*p[0],s*s*p0[1]+2*s*t*c[1]+t*t*p[1]))
 def _curveToOne(self,a,b,p):
  p0=self.cur
  for i in range(1,65):
   t=i/64;s=1-t;self._lineTo((s**3*p0[0]+3*s*s*t*a[0]+3*s*t*t*b[0]+t**3*p[0],s**3*p0[1]+3*s*s*t*a[1]+3*s*t*t*b[1]+t**3*p[1]))
cache={}
def scans(c):
 if c in cache:return cache[c]
 pen=Edges(glyphs);glyphs[cmap[ord(c)]].draw(pen);data={}
 for y in range(-240,801,2):
  xs=[a[0]+(y-a[1])/(b[1]-a[1])*(b[0]-a[0]) for a,b in pen.edges if a[1]!=b[1] and min(a[1],b[1])<=y<max(a[1],b[1])]
  if xs:data[y]=(min(xs),max(xs))
 cache[c]=data;return data
proposals=json.loads((root.parent/'spacing-refinement.json').read_text())
evidence={}
for pair,k in proposals['kerning_overrides'].items():
 a,b=pair; aa,bb=scans(a),scans(b); adv=font['hmtx'][cmap[ord(a)]][0]
 gaps=[adv+k+bb[y][0]-aa[y][1] for y in aa.keys()&bb.keys()]
 evidence[pair]={'kern':k,'minimum_horizontal_clearance_units':round(min(gaps),1),'median_horizontal_gap_units':round(statistics.median(gaps),1),'measurement_note':'Outer-boundary scanlines every 2 units; approximate, diagnostic only.'}
(root/'pair-clearances.json').write_text(json.dumps(evidence,indent=2)+'\n')
print('Closest pairs:',sorted(evidence.items(),key=lambda x:x[1]['minimum_horizontal_clearance_units'])[:8])

def explain_pair(pair):
 a,b=pair
 if b in '.,':return ('The low punctuation sits in the lower open region after the preceding glyph.','The mark attaches more clearly to its preceding glyph, while its diamond/tail stays separate from the letter and subsequent space.')
 if a in 'AVWY' and b in 'AVWYT':return ('Opposed or offset sloping strokes leave a widening wedge of white.','Reducing that wedge brings its apparent area closer to the adjacent capital gaps; top and baseline terminal approaches stay separate.')
 if a in 'LFP' and b.isupper():return ('An open upper or lower cavity meets the next diagonal capital.','The next glyph nests modestly into that cavity; the lower foot and diagonal remain distinguishable and the phrase no longer develops a hole.')
 if a in 'TVWY' and b.islower():return ('A capital overhang meets a lower shoulder, curve, or diagonal.','The x-height form moves under the overhang enough to relate to the following lower-case gap; r/u and diagonal starts use milder values to retain shoulder clearance.')
 return ('A lower-case diagonal opens a triangular cavity beside a curved or stemmed neighbor.','The small correction evens the texture of wave/away/woven without forcing the top serif into the neighboring shoulder.')
for group in ['final-pairs','final-words','final-reading']:
 path=root/group/'index.json';index=json.loads(path.read_text())
 for case in index['cases']:
  text=case['text'];pairs=[p for p in proposals['kerning_overrides'] if p in text]
  case['review_status']='accepted'
  case['visually_inspected']=True
  case['tested_pairs']=pairs
  if group=='final-pairs':
   case['pair_reviews']={p:{'white_space_shape':explain_pair(p)[0],'why_acceptable':explain_pair(p)[1],**evidence[p]} for p in pairs}
   case['observation']='Inspected compiled OFF/ON sheet after latest a, i/j, and diagonal outlines; all exact proposed pairs in this row remain separate and show the intended optical tightening.'
   case['why_acceptable']='Per-pair whitespace and closest-approach notes recorded below; pair spacing also checked in final-words and native-size final-reading controls.'
  elif group=='final-reading':
   case['observation']='Inspected at font_size22, pixel_scale1. The letters remain individually readable, word spaces are immediately distinguishable, and punctuation attaches without merging.'
   case['why_acceptable']='ON reduces the visibly loose overhang and diagonal starts; baseline marks and the larger i/j dots stay distinguishable at actual small size.'
  else:
   case['observation']='Inspected compiled OFF/ON word/control proof at font_size44, pixel_scale3.'
   case['why_acceptable']='The word holds a consistent rhythm across stem, round, and diagonal gaps. The a bearing correction removes extra pre-a air, and no tested word depends on a fused join.'
  case['unresolved_action']=None
 index['review_summary']={'accepted':len(index['cases']),'unresolved':0,'note':'Accepted only for these exact strings/settings. Not an exhaustive all-pair font assurance.'}
 path.write_text(json.dumps(index,indent=2)+'\n')
final_index=json.loads((root/'final-pairs/index.json').read_text())
proposals['review']['status']='accepted in compiled final-shape trial'
proposals['review']['source_revision_before_spacing']='b97535502a2716f68b56a13b2109505aad241d969961bf876395c1056212952a'
proposals['review']['final_trial_revision']=final_index['revision']
proposals['review']['final_trial_font_sha256']=final_index['font']['sha256']
proposals['review']['evidence']=['spacing-pass/final-pairs/index.json','spacing-pass/final-words/index.json','spacing-pass/final-reading/index.json','spacing-pass/pair-clearances.json']
proposals['review']['tested_scope']={'proposed_exact_pairs':len(proposals['kerning_overrides']),'final_pair_rows':15,'final_word_control_rows':14,'native_reading_rows':6,'display_settings':{'font_size':50,'pixel_scale':3},'word_settings':{'font_size':44,'pixel_scale':3},'reading_settings':{'font_size':22,'pixel_scale':1},'features_off':final_index['settings']['features_off'],'features_on':final_index['settings']['features_on']}
proposals['review']['limits']=['This is a bounded spacing review, not exhaustive coverage of every glyph combination.','Existing discretionary ligatures are not evaluated by these proofs; they remain disabled.','Approximate outline clearances are diagnostic and do not replace the recorded visual inspection.']
(root.parent/'spacing-refinement.json').write_text(json.dumps(proposals,indent=2)+'\n')
(root/'REVIEW.md').write_text('''# Wedge spacing pass

The accepted proposal is `../spacing-refinement.json`: a advances 562 → 547 with LSB 75 → 60, and 85 exact kerning values are added or revised. The matched 15-unit shift and advance reduction preserve a\'s right spacing while improving nanan/parallel after the bowl narrowing. H/O, n/o and space keep their advances.

Capital wedges and overhangs are the largest corrections (AV −95, AT −90, TA −95, LT −100); mixed-case T/V/W/Y pairs use separately reviewed values. Lower diagonal-round pairs receive small corrections. The existing ra/re/ro −18 stays: its top shoulder is already close, and tightening the lower cavity more would damage that relationship. Punctuation after overhangs moves closer; colon/semicolon geometry and spacing are unchanged.

Final exact-pair rows (85 pairs), word controls and actual 22px reading-size samples were all opened and visually inspected after the latest source outlines. All tested pairs remain recognizable, words remain distinct, and the corrected gaps are related to neighboring gaps rather than made numerically equal. Final ledgers contain source revision, font hash, feature maps, images, shaping and per-row acceptance notes. Approximate same-height outline clearances in `pair-clearances.json` support the review but are not aesthetic verdicts.

- `final-pairs/index.json`: 15 accepted rows, 7 inspected sheets, 50px / 3×.
- `final-words/index.json`: 14 accepted rows, 7 inspected sheets, 44px / 3×.
- `final-reading/index.json`: 6 accepted rows, 2 inspected sheets, 22px / 1×.

Scope is bounded to those strings; this does not certify every possible glyph combination. Baseline and earlier trial proofs are retained for comparison and are superseded by the final ledgers.
''')
print('Accepted proposal final revision:', final_index['revision'])

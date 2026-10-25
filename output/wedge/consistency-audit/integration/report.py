from pathlib import Path
import json,hashlib,math
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from font_maker.preview import shape_font
D=Path(__file__).resolve().parent;A=D.parent;O=A.parent
integration=json.loads((D/'integration.json').read_text());font=O/'build/fonts/HakilandDisplay-Regular.ttf';f=TTFont(font);gs=f.getGlyphSet();records=[]
for group in ['caps','lower','marks']:
 r=json.loads((A/group/'review.json').read_text())
 for raw in r['glyphs']:
  e=dict(raw);assert e['visual'].startswith('inspected') and e['geometry'].startswith('inspected'),(group,e)
  c=e['character'];e['review_group']=group;e['baseline_decision']=e.get('decision',e.get('recommendation'))
  e['final_decision']='refined; final compiled comparison inspected' if c in integration['selected_sources'] else 'retained; exported outline unchanged'
  path=O/f'refined/glyph-U{ord(c):04X}.svg'
  if not path.exists():path=O/f'drawings/glyph-U{ord(c):04X}.svg'
  e['final_source']=str(path.relative_to(O));e['final_source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  if c=='7':
   e['final_observation']='User rejected uniform-width 0.113 construction. Selected T2 after comparing three uniform and three tapered trials. Fine upper entry and38-unit bar refer to4 contrast; monotonic curved inner edge grows smoothly toward the base. Deliberate taper supersedes parallel inner/outer diagonal edges; outer edge, baseline,45-degree left wedge andadvance stay aligned. Root and independent capreviewer inspected allT2proofs/source; final display/native comparisons inspected.'
   e['final_proofs']=['seven-taper-comparison.png','consistency-comparison-80.png','consistency-comparison-24.png']
  records.append(e)
assert len(records)==103 and {ord(e['character']) for e in records}==set(f.getBestCmap())
class Flatten(BasePen):
 def __init__(self):super().__init__(gs);self.contours=[];self.pts=[]
 def _moveTo(self,p):self.pts=[p]
 def _lineTo(self,p):self.pts.append(p)
 def _qCurveToOne(self,p1,p2):
  p0=self.pts[-1]
  for j in range(1,101):
   t=j/100;s=1-t;self.pts.append(tuple(s*s*p0[k]+2*s*t*p1[k]+t*t*p2[k] for k in (0,1)))
 def _curveToOne(self,p1,p2,p3):
  p0=self.pts[-1]
  for j in range(1,101):
   t=j/100;s=1-t;self.pts.append(tuple(s*s*s*p0[k]+3*s*s*t*p1[k]+3*s*t*t*p2[k]+t*t*t*p3[k] for k in (0,1)))
 def _closePath(self):self.pts.append(self.pts[0]);self.contours.append(self.pts);self.pts=[]
 def _endPath(self):self._closePath()
flat=Flatten();gs['seven'].draw(flat);profile=[];norm=math.hypot(677,235);ux,uy=677/norm,-235/norm
for ysvg in [200,350,500,650,750]:
 origin=(511-(ysvg-123)*235/677,800-ysvg);crossings=[]
 for points in flat.contours:
  for a,b in zip(points,points[1:]):
   ax=(a[0]-origin[0])*ux+(a[1]-origin[1])*uy;ay=-(a[0]-origin[0])*uy+(a[1]-origin[1])*ux
   bx=(b[0]-origin[0])*ux+(b[1]-origin[1])*uy;by=-(b[0]-origin[0])*uy+(b[1]-origin[1])*ux
   if (ay<=0<by) or (by<=0<ay):crossings.append(ax+(bx-ax)*(-ay)/(by-ay))
 crossings.sort();intervals=[(a,b) for a,b in zip(crossings[::2],crossings[1::2])];a,b=min(intervals,key=lambda ab:abs(ab[1]));profile.append({'svg_y':ysvg,'font_y':800-ysvg,'perpendicular_width':round(b-a,2)})
assert all(a['perpendicular_width']<b['perpendicular_width'] for a,b in zip(profile,profile[1:]))
formats={};contexts=['0123456789 147 747 777','HEFLNYI useful uniform','Angular grace 17:47','We Welcome Wednesday','fl fk fb fh office']
for ext in ['ttf','otf','woff2']:
 path=O/f'build/fonts/HakilandDisplay-Regular.{ext}';ft=TTFont(path);assert ft.getBestCmap()==f.getBestCmap();shapepath=path
 if ext=='woff2':shapepath=D/'decompressed.ttf';ft.flavor=None;ft.save(shapepath)
 for t in contexts:
  shaped=shape_font(shapepath,t,{'kern':True,'liga':False});assert all(g['glyph_id'] for g in shaped['glyphs']);assert shaped['total_advance']==shape_font(font,t,{'kern':True,'liga':False})['total_advance']
 formats[ext]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'coverage':len(ft.getBestCmap()),'shaping_checked':contexts}
report=dict(version=integration['version'],revision=integration['revision'],font_sha256=integration['font_sha256'],baseline_version='0.113',baseline_revision='272db274ec68a315bb99eabc7fd98cd3a484b6dd93cfdc76f01485f032b2e691',reviewed_count=103,changed_characters=list(integration['selected_sources']),retained_count=93,status='Full source and visual consistency review; ten glyphs refined and compiled comparisons inspected; user aesthetic acceptance pending',invariants=integration['invariants'],metric_differences=integration['metric_differences'],seven={'selected':'T2','source_width_profile':'44→112 units relative to the fixed outer-edge normal; quadratic progression','compiled_normal_samples':profile,'top_bar':38,'reason':'Lighter entry/top with stronger lower stroke, suggested by user after two rejected uniform-width reductions.','parallel_exception':'Inner edge deliberately curves away from outer edge to redistribute weight; this follows user taper direction.','comparison':'seven-taper-comparison.png'},cross_family_findings={'flat_caps':700,'round_caps_top':712,'A_apex':{'value':724,'decision':'retain optical pointed overshoot'},'lowercase':{'flat_top':470,'pointed_head_top':480,'round_top':482,'decision':'distinct optical zones retained'},'ascenders':770,'descenders':{'p_q':-220,'g':-223,'j':-230,'y':-229,'decision':'different constructions retain optically coherent depths'},'dots':{'i_j_diagonal':106,'punctuation_diagonal':92,'decision':'different roles intentionally retained'},'four_top':{'before':712,'after':700,'reason':'Broad flat figure top now matches flatcapline; innerdiagonal adjusted to retainparallelism'},'curves':'Original O/o controls, related bowlstress, and recent a/d/S/$ corrections retained. Reviewed in mixedcase and native24px contexts.','terminals':'Upright attachment cuts share45degree family; distinct armwedges, R/Q tails and inclinedlegterminals retained.'},formats=formats,glyphs=records)
(O/'consistency-review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
md='''# Hakiland Display — design consistency, version 0.114

Reviewed all 103 encoded characters against the concept art, related construction families, source SVG geometry, and fresh compiled display/native 24 px proofs. Three subagents covered capitals, lowercase, and figures/punctuation; the integrator checked mixed families and the final exports.

| Glyphs | Refined relationship |
| --- | --- |
| E F L N Y | Attached straight-stem serif cuts now follow the shared 45° family. |
| f | Foot flares match related upright lowercase stems. |
| u | Head wedges match n/i/j; exit wedge follows d. |
| 1 and 4 | Figure foot cuts match upright serif angles. The broad flat top of 4 meets cap height; its diagonal remains parallel. |
| 7 | Fine upper stroke grows smoothly toward a fuller base, with a much thinner top bar. This implements the user's suggestion to use 4's contrast and a thicker lower stroke. |

The 7 is a new construction rather than another uniformly thinner band. Three constant-width and three tapered alternatives were compared. T2 was selected: its inner cubic is monotonic, without an inflection or bulge, and starts tangent to the outer-edge direction before gradually diverging. This deliberate taper takes precedence over the earlier general preference for parallel edges. Prior weight-review acceptance of the uniform 7 is superseded.

The other 93 characters retain their exported outlines. Distinct bowls, arm terminals, Q/R tails, and optical overshoots were reviewed and preserved instead of being forced into identical geometry.

[7 before/after](seven-taper-comparison.png) · [Full comparison](consistency-comparison-80.png) · [Native 24 px](consistency-comparison-24.png) · [Per-glyph evidence and measurements](consistency-review.json)

TTF, OTF, and WOFF2 pass coverage and tested-context shaping checks. Advances, kerning, and substitution tables remain unchanged. The u outline extends one unit farther left (LSB26→25), and its exit reaches five units farther right; context spacing was reinspected. Other outline changes are confined to the ten listed glyphs. User aesthetic judgment remains open.

The design metrics and serif skills now encourage creative redistribution of weight—light entries, stronger terminals, relieved joins and tapers—when constant-width adjustments fail, with compiled comparisons and explicit geometry checks.
'''
(O/'consistency-review.md').write_text(md);(O/'review-notes.md').write_text(md+'\n---\n\n'+(O/'review-notes.md').read_text())
print(json.dumps({'reviewed':len(records),'changed':list(integration['selected_sources']),'seven_profile':profile,'formats':formats},indent=2))

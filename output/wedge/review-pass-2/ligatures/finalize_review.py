from pathlib import Path
import hashlib,json,math
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from font_maker.preview import shape_font
ROOT=Path(__file__).resolve().parent
source=json.loads((ROOT/'source.json').read_text());trial=json.loads((ROOT/'trial.json').read_text())
base=Path(source['source']['path'])/'build/fonts/HakilandDisplay-Regular.ttf'
assert hashlib.sha256(base.read_bytes()).hexdigest()==source['sha256']
font=TTFont(base);gs=font.getGlyphSet()
class SamplePen(BasePen):
 def __init__(self,g):super().__init__(g);self.segments=[]
 def _moveTo(self,p):self.p=p;self.first=p
 def _lineTo(self,p):self.segments.append((self.p,p));self.p=p
 def _qCurveToOne(self,c,p):
  a=self.p
  for i in range(1,65):
   t=i/64;self._lineTo(tuple((1-t)**2*a[k]+2*(1-t)*t*c[k]+t*t*p[k] for k in range(2)))
 def _curveToOne(self,c,d,p):
  a=self.p
  for i in range(1,65):
   t=i/64;self._lineTo(tuple((1-t)**3*a[k]+3*(1-t)**2*t*c[k]+3*(1-t)*t*t*d[k]+t**3*p[k] for k in range(2)))
 def _closePath(self):self._lineTo(self.first)
 def _endPath(self):pass
def segs(c,dx=0):
 p=SamplePen(gs);gs[c].draw(p)
 return [tuple((x+dx,y) for x,y in seg) for seg in p.segments]
def pdist(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];d=dx*dx+dy*dy
 t=0 if d==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def dist(sa,sb):
 return min(min(pdist(a,c,d),pdist(b,c,d),pdist(c,a,b),pdist(d,a,b)) for a,b in sa for c,d in sb)
measure={}
for seq in ['fi','fl','ff','ft','fj','fk','fb','fh']:
 measure[seq]={str(kern):round(dist(segs('f'),segs(seq[1],363+kern)),3) for kern in ([0,24] if seq in ['fl','fk','fb','fh'] else [0])}
# Feature toggles do not substitute, and spacing-only trial preserves cmap and glyphs.
toggle_records=[]
for fp in [base,Path(trial['font'])]:
 f=TTFont(fp);assert len(f.getBestCmap())==103
 assert set(f.getBestCmap().values())==set(font.getBestCmap().values())
 for text in ['fi fl ff ffi ffl ft fj fk','profile flower office official difficult affluent offline','Qu Queue Quartz rare river error letter pasta actor minimum manner','flfl ffh (fl) offkey offbeat offhand']:
  off=shape_font(fp,text,{'kern':True,'liga':False,'rlig':False,'dlig':False})
  on=shape_font(fp,text,{'kern':True,'liga':True,'rlig':True,'dlig':True})
  assert off['glyphs']==on['glyphs']
  toggle_records.append(dict(font=str(fp),text=text,off=off,on=on))
records=json.loads((ROOT/'records.json').read_text())
for r in records:r['status']='visually inspected; review conclusions in REVIEW.md'
(ROOT/'records.json').write_text(json.dumps(records,indent=2))
report=dict(source=source,trial=trial,status='inspected; no ligature recommended for production',routine_ligatures_required=False,ligature_rules_drawn=0,reason_no_replacement='No demonstrated functional or expressive benefit beyond the original separate forms and the +24 upper-serif clearance correction. No arbitrary bridge or dot removal was drawn.',recommended_kerning={k:24 for k in ['fb','fh','fk','fl']},approx_min_outline_distance_units=measure,measure_method='Compiled quadratic contours subdivided into 64 chords per curve; minimum segment distances. Diagnostic clearance, not a visual acceptance threshold.',proof_records=len(records),features_toggles=toggle_records,source_unchanged=True)
(ROOT/'report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['status','recommended_kerning','approx_min_outline_distance_units','proof_records']},indent=2))

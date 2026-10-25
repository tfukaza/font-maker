from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from pathlib import Path
import math,json
OUT=Path(__file__).parent
font=TTFont(OUT/'baseline.ttf'); gs=font.getGlyphSet(); cmap=font.getBestCmap()
class Flat(BasePen):
 def __init__(self): super().__init__(gs);self.contours=[];self.points=[]
 def _moveTo(self,p): self.points=[p]
 def _lineTo(self,p): self.points.append(p)
 def _curveToOne(self,p1,p2,p3):
  p0=self.points[-1]
  for j in range(1,101):
   t=j/100;s=1-t;self.points.append(tuple(s*s*s*p0[k]+3*s*s*t*p1[k]+3*s*t*t*p2[k]+t*t*t*p3[k] for k in (0,1)))
 def _qCurveToOne(self,p1,p2):
  p0=self.points[-1]
  for j in range(1,101):
   t=j/100;s=1-t;self.points.append(tuple(s*s*p0[k]+2*s*t*p1[k]+t*t*p2[k] for k in (0,1)))
 def _closePath(self): self.points.append(self.points[0]);self.contours.append(self.points);self.points=[]
 def _endPath(self): self._closePath()
def slice_glyph(ch,svg_point,direction=(1,0)):
 p=Flat();gs[cmap[ord(ch)]].draw(p)
 origin=(svg_point[0],800-svg_point[1]);dx,dy=direction;dy=-dy;mag=math.hypot(dx,dy);dx/=mag;dy/=mag
 vals=[]
 for cont in p.contours:
  for a,b in zip(cont,cont[1:]):
   # rotated into coordinate along ray (u), perpendicular(v)
   ax=(a[0]-origin[0])*dx+(a[1]-origin[1])*dy; ay=-(a[0]-origin[0])*dy+(a[1]-origin[1])*dx
   bx=(b[0]-origin[0])*dx+(b[1]-origin[1])*dy; by=-(b[0]-origin[0])*dy+(b[1]-origin[1])*dx
   if (ay<=0<by) or (by<=0<ay): vals.append(ax+(bx-ax)*(-ay)/(by-ay))
 vals.sort();return [{'start':round(a,2),'end':round(b,2),'width':round(b-a,2)} for a,b in zip(vals[::2],vals[1::2])]
measurements={}
for c in 'abcdefghijklmnopqrstuvwxyz':
 measurements[c]={'horizontal_svg_y565':slice_glyph(c,(0,565)), 'horizontal_svg_y650':slice_glyph(c,(0,650))}
for c in 'vwxyzk':
 # Main descending stroke perpendicular slope, z rising also
 slope={'v':(295,-118),'w':(446,-165),'x':(394,-262.667),'y':(295,-118),'z':(427,294),'k':(294,-152)}[c]
 midpoint={'v':(170,565),'w':(200,565),'x':(260,565),'y':(170,565),'z':(245,565),'k':(340,620)}[c]
 measurements[c]['normal_primary']={'point_svg':midpoint,'direction_svg':slope,'intervals':slice_glyph(c,midpoint,slope)}
for c in 'bodpq':
 x={'b':299,'o':279,'d':287,'p':299,'q':281}[c]
 measurements[c]['vertical_round_extrema']={'x':x,'intervals':slice_glyph(c,(x,0),(0,1))}
for c in 'ij':
 measurements[c]['dot']={'diagonal_bbox':106,'diamond_side':round(106/math.sqrt(2),2),'svg_y_min':139,'svg_y_max':245,'body_clearance':75,'stem':106}
(OUT/'measurements.json').write_text(json.dumps(measurements,indent=2))
for c,ms in measurements.items(): print(c,json.dumps(ms))

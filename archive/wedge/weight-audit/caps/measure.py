from pathlib import Path
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
import json,math
class FlatPen(BasePen):
 def __init__(self,gs):super().__init__(gs);self.contours=[];self.current=[]
 def _moveTo(self,p):self.current=[p]
 def _lineTo(self,p):self.current.append(p)
 def _curveToOne(self,p1,p2,p3):
  p0=self.current[-1]
  for i in range(1,201):
   t=i/200;u=1-t;self.current.append(tuple(u**3*p0[j]+3*u*u*t*p1[j]+3*u*t*t*p2[j]+t**3*p3[j] for j in [0,1]))
 def _qCurveToOne(self,p1,p2):
  p0=self.current[-1]
  for i in range(1,201):
   t=i/200;u=1-t;self.current.append(tuple(u*u*p0[j]+2*u*t*p1[j]+t*t*p2[j] for j in [0,1]))
 def _closePath(self):self.current.append(self.current[0]);self.contours.append(self.current);self.current=[]
 def _endPath(self):self._closePath()
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def sections(font,c,point,direction):
 tt=TTFont(font);gs=tt.getGlyphSet();pen=FlatPen(gs);gs[tt.getBestCmap()[ord(c)]].draw(pen)
 mag=math.hypot(*direction);d=tuple(v/mag for v in direction);hits=[]
 for contour in pen.contours:
  for a,b in zip(contour,contour[1:]):
   v=(b[0]-a[0],b[1]-a[1]);den=cross(d,v)
   if abs(den)<1e-9:continue
   q=(a[0]-point[0],a[1]-point[1]);t=cross(q,v)/den;u=cross(q,d)/den
   if 0<=u<1:hits.append(t)
 hits.sort();intervals=[(round(a,3),round(b,3),round(b-a,3)) for a,b in zip(hits[::2],hits[1::2])]
 return intervals
ROOT=Path('output/wedge/weight-audit/caps');font=Path('output/wedge/build/fonts/HakilandDisplay-Regular.ttf')
records={}
# Font-space points; vertical figures use horizontal section; diagonals use true normals.
for c,point,d in [('H',(0,250),(1,0)),('O',(0,350),(1,0)),('B',(0,190),(1,0)),('D',(0,350),(1,0)),('P',(0,510),(1,0)),('A',(480,300),(657,302)),('K',(495,350),(2,1)),('M',(320,350),(619,297)),('N',(390,350),(623,522)),('V',(242,350),(660,264)),('W',(260,350),(3,1)),('X',(350,350),(600,400)),('Y',(300,500),(345,223)),('Z',(320,350),(653,-440)),('S',(320,350),(30,66))]:
 records[c]={'point_font':point,'direction':d,'intervals':sections(font,c,point,d)}
for delta in [8,12]:records[f'S-minus{delta}']={'point_font':[320,350],'direction':[30,66],'intervals':sections(ROOT/f'S-minus{delta}.ttf','S',(320,350),(30,66))}
(ROOT/'measurements.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))

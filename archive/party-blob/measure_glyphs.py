"""Record comparable curve sections from the original project-specific drawings."""
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from fontTools.pens.basePen import BasePen
from fontTools.svgLib.path import parse_path

OUT=Path(__file__).resolve().parent
class Sections(BasePen):
    def __init__(self): super().__init__(None); self.edges=[]; self.start=None
    def _moveTo(self,p): self.start=p
    def _lineTo(self,p): self.edges.append((self._getCurrentPoint(),p))
    def _curveToOne(self,p1,p2,p3):
        p0=self._getCurrentPoint(); last=p0
        for i in range(1,101):
            t=i/100; u=1-t
            point=tuple(u**3*p0[j]+3*u*u*t*p1[j]+3*u*t*t*p2[j]+t**3*p3[j] for j in [0,1])
            self.edges.append((last,point)); last=point
    def _closePath(self): self.edges.append((self._getCurrentPoint(),self.start))
    def _endPath(self): pass
    def horizontal(self,y):
        xs=sorted(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]) for a,b in self.edges if (a[1]<=y<b[1]) or (b[1]<=y<a[1]))
        return [round(xs[i+1]-xs[i],1) for i in range(0,len(xs)-1,2)]
rows={}
items=json.loads((OUT/'glyphs.json').read_text())
for item in items:
    name=item['name']
    if name not in ['H','I','l','n','h','m','o','p','g','f','t']:continue
    pen=Sections()
    for node in ET.parse(item['svg_path']).getroot().findall('.//{http://www.w3.org/2000/svg}g[@id="glyph"]/{http://www.w3.org/2000/svg}path'):
        parse_path(node.attrib['d'],pen)
    rows[name]={'svg_y_600_font_y_200':pen.horizontal(600),'svg_y_440_font_y_360':pen.horizontal(440)}
(OUT/'measurements.json').write_text(json.dumps({'method':'Cubic curves sampled at 100 steps per segment; horizontal ink intervals in source font units, approximate. Sections distinguish thick and thin families, not a universal stroke width.','sections':rows},indent=2))
print(json.dumps(rows,indent=2))

"""Verify every creative substitution, overlaps, export parity, and base-font preservation."""
import io,json,hashlib,sys
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from font_maker.store import ProjectStore
OUT=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else OUT/'ligature-review/font'
DEST=Path(sys.argv[2]) if len(sys.argv)>2 else OUT/'ligature-review/acceptance.json'
BASE=OUT/'ligature-review/baseline'
COVERAGE=''.join(chr(i) for i in range(32,127))+'–—‘’“”•…'
RULES={'En':'E_n','ec':'e_c','in':'i_n','na':'n_a','oo':'o_o','rt':'r_t'}
WORDS=['Rec','record','collect','Engine','spinning','inside','Snap','banana','natural','moon','balloon','groovy','Party','started','artwork','final']
STRINGS=WORDS+list(RULES)+[f'({p}) {p}{p} a{p}a' for p in RULES]+['AV XYZ 0123456789 fi fl nn mm',COVERAGE,'En Engine','final banana Engine','Rec Snap Food Pool Tool Tech']
def expected(text,cmap,on):
 out=[];index=0
 while index<len(text):
  seq=text[index:index+2]
  if on and seq in RULES:out.append((RULES[seq],index));index+=2
  else:out.append((cmap[ord(text[index])],index));index+=1
 return out
def load(path):
 font=TTFont(path);font.flavor=None;stream=io.BytesIO();font.save(stream)
 h=hb.Font(hb.Face(stream.getvalue()));h.scale=(1000,1000)
 return font,h
def shape(h,text,on,kern=True):
 b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(h,b,{'kern':kern,'liga':False,'dlig':on})
 return [(h.glyph_to_string(i.codepoint),i.cluster,p.x_advance,p.x_offset,p.y_offset) for i,p in zip(b.glyph_infos,b.glyph_positions)]
results={};traces={}
for ext in ['ttf','otf','woff2']:
 path=ROOT/f'build/fonts/PartyBlob-Regular.{ext}'
 f,h=load(path);b,bh=load(BASE/f'build/fonts/PartyBlob-Regular.{ext}')
 cmap=f.getBestCmap();assert cmap==b.getBestCmap();assert len(cmap)==103
 for tag,attrs in [('head',['unitsPerEm']),('hhea',['ascent','descent','lineGap']),('OS/2',['sxHeight','sCapHeight'])]:
  assert all(getattr(f[tag],a)==getattr(b[tag],a) for a in attrs)
 # Every old glyph, including E_n, retains exactly its compiled outline and advance.
 fg,bg=f.getGlyphSet(),b.getGlyphSet()
 for name in b.getGlyphOrder():
  fp,bp=RecordingPen(),RecordingPen();fg[name].draw(fp);bg[name].draw(bp)
  assert fp.value==bp.value,(ext,name,'base outline changed')
  assert f['hmtx'][name]==b['hmtx'][name],(ext,name,'base metrics changed')
 for text in STRINGS:
  for on in [False,True]:
   run=shape(h,text,on)
   assert [(n,c) for n,c,*_ in run]==expected(text,cmap,on),(ext,text,on,run)
   assert all(n!='.notdef' for n,*_ in run)
   if not on:assert run==shape(bh,text,False),(ext,text,'feature-off changed')
   traces.setdefault(text,{})[str(on)]=run
  # Boundary kerning may move glyphs but may not alter identities or clusters.
  assert [(n,c) for n,c,*_ in shape(h,text,True,False)]==[(n,c) for n,c,*_ in shape(h,text,True,True)]
 assert [g[0] for g in shape(h,'final',True)]==['f','i_n','a','l']
 assert [g[0] for g in shape(h,'banana',True)]==['b','a','n_a','n_a']
 assert [g[0] for g in shape(h,'Engine',True)]==['E_n','g','i_n','e']
 unrelated='AV XYZ 0123456789 fi fl nn mm'
 assert shape(h,unrelated,False)==shape(h,unrelated,True)
 results[ext]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'encoded_count':len(cmap),'glyph_count':len(f.getGlyphOrder()),'base_outlines_and_metrics_unchanged':True,'feature_off_matches_baseline':True,'exact_substitutions_and_clusters':True,'cases_checked':len(STRINGS)}
 f.close();b.close()
DEST.parent.mkdir(exist_ok=True,parents=True)
DEST.write_text(json.dumps({'revision':ProjectStore(ROOT).revision(),'rules':RULES,'formats':results,'traces':traces},indent=2))
print(json.dumps({'revision':ProjectStore(ROOT).revision(),'formats':results},indent=2))

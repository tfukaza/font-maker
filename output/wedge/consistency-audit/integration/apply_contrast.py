from pathlib import Path
import hashlib, json, shutil
from xml.etree import ElementTree as ET
from fontTools.ttLib import TTFont
from font_maker.service import FontMakerService
from font_maker.preview import shape_font, compose_preview_svg, svg_to_png

D=Path(__file__).resolve().parent
O=D.parents[1]
B=O/'revisions/before-seven-contrast'
s=FontMakerService(); info=s.open_project(str(O)); store,p=s._store_project(info['project_id'])
assert p.font.version=='0.114'
B.mkdir(exist_ok=True)
for folder in ['build','glyphs','refined','references']:
    shutil.copytree(O/folder,B/folder,dirs_exist_ok=True)
for path in O.iterdir():
    if path.is_file() and path.suffix!='.zip': shutil.copy2(path,B/path.name)
src=D/'seven-contrast-108-24.svg'; dst=O/'refined/glyph-U0037.svg'
shutil.copy2(src,dst)
p.font.version='0.115'; rev=store.save(p,info['revision'])
res=s.upsert_glyphs(info['project_id'],rev,[dict(name='seven',codepoints=['U+0037'],advance_width=546,svg_path=str(dst))])
built=s.build(info['project_id'],['ttf','otf','woff2'])
for name in ['build-report.json','last-build.log']:(O/name).write_text(json.dumps(built,indent=2,default=str))
font=O/'build/fonts/HakilandDisplay-Regular.ttf'; prior=B/'build/fonts/HakilandDisplay-Regular.ttf'
f,b=TTFont(font),TTFont(prior)
assert f.getBestCmap()==b.getBestCmap()
assert f['hmtx'].metrics==b['hmtx'].metrics
changed=[n for n in f.getGlyphOrder() if f['glyf'][n].compile(f['glyf'])!=b['glyf'][n].compile(b['glyf'])]
assert changed==['seven'],changed
for tag in ['GPOS','GSUB']: assert f.getTableData(tag)==b.getTableData(tag)
p=s._store_project(info['project_id'])[1]
contexts=['0123456789 147 747 777','HEFLNYI useful uniform','Angular grace 17:47','We Welcome Wednesday','fl fk fb fh office']
formats={}
for ext in ['ttf','otf','woff2']:
    path=O/f'build/fonts/HakilandDisplay-Regular.{ext}'; ft=TTFont(path)
    assert ft.getBestCmap()==f.getBestCmap(); shape_path=path
    if ext=='woff2':
        shape_path=D/'contrast-decompressed.ttf'; ft.flavor=None; ft.save(shape_path)
    for text in contexts:
        actual=shape_font(shape_path,text,{'kern':True,'liga':False})
        assert all(g['glyph_id'] for g in actual['glyphs'])
        assert actual['total_advance']==shape_font(prior,text,{'kern':True,'liga':False})['total_advance']
    formats[ext]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),coverage=len(ft.getBestCmap()),shaping_checked=contexts)

def line(ft,text,x,y,size):
    root=ET.fromstring(compose_preview_svg(ft,p,shape_font(ft,text,{'kern':True,'liga':False}),font_size=size,guides=False))
    m=max(16,int(size*.25)); base=m+size*.8
    return f'<g transform="translate({x-m} {y-base})">'+''.join(ET.tostring(e,encoding='unicode') for e in root if e.tag.endswith('path'))+'</g>'
parts=[]
for y,label,ft in [(28,'Previous — tapered stroke',prior),(246,'Revised — full diagonal, hairline top bar',font)]:
    parts.append(f'<text x="28" y="{y}" font-family="Arial" font-size="14" fill="#726b62">{label}</text>')
    parts.append(line(ft,'147 747 777',28,y+155,180))
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="465"><rect width="100%" height="100%" fill="#f8f6ef"/>'+''.join(parts)+'</svg>'
(O/'seven-contrast-comparison.svg').write_text(svg)
(O/'seven-contrast-comparison.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=1))
baseline=O/'revisions/before-consistency-audit/build/fonts/HakilandDisplay-Regular.ttf'
for size,scale in [(80,3),(24,1)]:
    parts=[];y=25;w=1100 if size==80 else 700
    for text in ['0123456789 147 747','HEFLNYI useful uniform','Angular grace 17:47']:
        for ft,label in [(baseline,'Before — 0.113'),(font,'After — 0.115')]:
            parts.append(f'<text x="24" y="{y}" font-family="Arial" font-size="12" fill="#726b62">{label}</text>')
            y+=size+12;parts.append(line(ft,text,24,y,size));y+=33
        y+=10
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{y}"><rect width="100%" height="100%" fill="#f8f6ef"/>'+''.join(parts)+'</svg>'
    (O/f'consistency-comparison-{size}.svg').write_text(svg)
    (O/f'consistency-comparison-{size}.png').write_bytes(svg_to_png(svg.encode(),pixel_scale=scale))

report=json.loads((O/'consistency-review.json').read_text())
report.update(version='0.115',revision=res.revision,font_sha256=formats['ttf']['sha256'],formats=formats)
report['seven']=dict(selected='108 / 24',diagonal_perpendicular_width=108,top_bar=24,reason='Latest user direction: keep the main stroke thick and the horizontal line very thin.',parallel_construction='Straight inner and outer diagonal edges share slope 235/677; the left wedge diagonal remains 45 degrees.',comparison='seven-contrast-comparison.png',supersedes='0.114 tapered T2 construction',proof_status='Candidate images inspected; final exported images pending inspection')
for e in report['glyphs']:
    if e['character']=='7':
        e['final_source_sha256']=hashlib.sha256(dst.read_bytes()).hexdigest()
        e['final_observation']='Restored 108-unit parallel main diagonal and reduced the top bar to 24 units per latest user direction. Compared 108/24, 108/20, and 114/24 compiled candidates at display and native 24 px. 108/24 keeps a strong diagonal with a bar matching H/A crossbars, avoiding the heavier 114-unit alternative.'
        e['final_proofs']=['seven-contrast-comparison.png','consistency-comparison-80.png','consistency-comparison-24.png']
(O/'consistency-review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
md=(O/'consistency-review.md').read_text().replace('version 0.114','version 0.115')
md=md.replace('| 7 | Fine upper stroke grows smoothly toward a fuller base, with a much thinner top bar. This implements the user\'s suggestion to use 4\'s contrast and a thicker lower stroke. |','| 7 | Full 108-unit parallel diagonal paired with a 24-unit hairline top bar, following the latest user direction. |')
start=md.index('The 7 is a new construction')
end=md.index('\n\nThe other 93',start)
md=md[:start]+'The latest 7 restores a full, straight diagonal while making its top bar a hairline. Three compiled alternatives were compared: 108/24, 108/20, and 114/24 (diagonal/bar units). The selected 108/24 construction maintains parallel diagonal edges, a 45° left wedge, and the existing advance. The bar matches the 24-unit H/A crossbar family; the slightly lighter-than-4 main stroke avoids the stronger 114-unit candidate. This supersedes the tapered 0.114 trial after the user changed direction.'+md[end:]
md=md.replace('seven-taper-comparison.png','seven-contrast-comparison.png')
(O/'consistency-review.md').write_text(md)
notes=(O/'review-notes.md').read_text(); divider=notes.find('\n---\n\n')
(O/'review-notes.md').write_text(md+notes[divider:])
design=json.loads((O/'design.json').read_text());design['revision']=res.revision
design['user_refinements'].append('0.115: user superseded the tapered 7 with a full parallel 108-unit diagonal and a 24-unit hairline horizontal bar.')
(O/'design.json').write_text(json.dumps(design,indent=2))
# Keep superseded proof images out of the current package; archived above.
for name in ['seven-taper-comparison.svg','seven-taper-comparison.png','browser-preview.png']:
    path=O/name
    if path.exists():path.unlink()
(D/'contrast-integration.json').write_text(json.dumps(dict(version='0.115',revision=res.revision,formats=formats,changed_from_0114=changed,diagnostics=built['diagnostics']),indent=2))
print(json.dumps(dict(version='0.115',revision=res.revision,changed=changed,formats=formats,diagnostics=built['diagnostics']),indent=2))

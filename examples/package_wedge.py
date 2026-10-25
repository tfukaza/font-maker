"""Package the current compiled Hakiland Display font and its reviewable specimen."""
import base64
import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from font_maker.preview import compose_preview_svg, shape_font, svg_to_png
from font_maker.service import FontMakerService

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'archive/wedge'
service=FontMakerService()
info=service.open_project(str(OUT))
project=service._store_project(info['project_id'])[1]
report=json.loads((OUT/'build-report.json').read_text())
font_path=OUT/'build/fonts/HakilandDisplay-Regular.ttf'
font=TTFont(font_path)
cmap=font.getBestCmap()
expected={int(x,16) for x in json.loads((ROOT/'skills/font-production-workflow/references/latin-coverage.json').read_text())['profiles']['prototype']['codepoints']}
audit={'revision':info['revision'],'formats':{},'bounds':{},'shaping':{},'metrics':{},'parallel_construction':{}}
for suffix in ['ttf','otf','woff2']:
    path=OUT/f'build/fonts/HakilandDisplay-Regular.{suffix}'
    current=TTFont(path)
    mapping=current.getBestCmap()
    missing=sorted(expected-set(mapping))
    assert not missing,missing
    audit['formats'][suffix]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'encoded_characters':len(mapping),'missing_codepoints':missing}
glyphs=font.getGlyphSet()
for cp,name in cmap.items():
    p=BoundsPen(glyphs);glyphs[name].draw(p)
    audit['bounds'][chr(cp)]=p.bounds
    if p.bounds:
        assert p.bounds[1]>=-240 and p.bounds[3]<=800,(name,p.bounds)
for name,text in {'alphabet':'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789','pairs':'AV AW AY To Ta Ty Va Vo Ya Yo','bowls':'aadd bbppqq','figures':'0123456789 & ?!','punctuation':'12:30; a,b. “Quiet!” (g) $25.00'}.items():
    shaped=shape_font(font_path,text,{'kern':True,'liga':False})
    assert all(g['glyph_id'] for g in shaped['glyphs'])
    audit['shaping'][name]=shaped
dot_points=[(x,y) for x,y in font['glyf'][cmap[ord('i')]].coordinates if y>500]
audit['metrics']={
    'status':'inspected',
    'UPM':1000,'cap_height':700,'x_height':470,'ascender_zone':770,
    'body_top_i_j_n':[480,480,482],
    'body_top_reason':'10-unit pointed head overshoot; round n shoulder 12-unit overshoot.',
    'dot_bounds_i':[min(x for x,y in dot_points),min(y for x,y in dot_points),max(x for x,y in dot_points),max(y for x,y in dot_points)],
    'descenders':{c:audit['bounds'][c][1] for c in 'gpqjy'},
    'round_extrema':{c:audit['bounds'][c] for c in 'Oo'},
    'line_metrics':{'ascent':800,'descent':-240,'gap':70},
    'stem_families':{'capital':116,'lowercase':106,'hairlines':'20–24'},
    'figure_style':'proportional lining; top 700–712, baseline overshoots up to -12',
    'space_advance':255,
    'accents':'Not in the selected 103-character prototype scope.',
}
audit['parallel_construction']={
    'stems':'Vertical shared x coordinates through body sections; cap 116, lowercase 106 units.',
    'crossbars':'Horizontal; H/A 24-unit parallel edges, E/F 24-unit parallel edges.',
    'X_x':'Opposing sides are generated from identical vectors: 2/3 descent and 4/5 ascent. Integer export can round by <1 unit.',
    'V_v':'Both edges of each diagonal use |dx/dy| = 0.4.',
    'Q':'An under-bowl ribbon replaces the rejected slash tail; long ribbon edges have a shared 1:5 slope and the counter terminal echoes diamond dots.',
    'g':'Single 110 × 110 right triangle, 45-degree diagonal.',
    'r':'Three consecutive terminal edges are 45 degrees, matching the diamond dots.',
    'serifs':'Shared stem foot/crown helpers have 45-degree cuts; optical deviations retained in contextual joins.',
    'bowls':'Original cubic curves use aligned extrema/tangents; a and b/d/p/q have unified contours to remove overlap bulges.',
}
audit['review']={'status':'revised prototype; user aesthetic acceptance pending','inspected_scope':['alphabet and figures at display size','geometric Q and triangular g ear','a/d and related unified bowls','parallel construction families','selected kerning OFF/ON proofs','punctuation at display size','24 px native rendering'], 'limitations':['Display prototype, designed primarily for headings at 32 px and above.','103 encoded characters; accented letters and combining marks are not included.','No ligature substitutions.','All possible kerning combinations have not been individually reviewed.','Font licensing has not been assigned by the user.']}
for name in ['diagonal-refinement','spacing-refinement','optical-review','w-kerning-review','second-pass-review','weight-review','consistency-review']:
    report_path=OUT/f'{name}.json'
    if report_path.exists():
        audit[name]=json.loads(report_path.read_text())
(OUT/'quality-report.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False))

def line(text,x,y,size):
    data=compose_preview_svg(font_path,project,shape_font(font_path,text,{'kern':True,'liga':False}),font_size=size,guides=False)
    root=ET.fromstring(data)
    margin=max(16,int(size*.25))
    baseline=margin+800*size/1000
    body=''.join(ET.tostring(e,encoding='unicode') for e in root if e.tag.endswith('path'))
    return f'<g transform="translate({x-margin} {y-baseline})">{body}</g>'

poster=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1240" viewBox="0 0 1440 1240"><rect width="1440" height="1240" fill="#f8f6ef"/>',
        '<g fill="#736b61" font-family="Arial,sans-serif" font-size="17" letter-spacing="3"><text x="76" y="65">HAKILAND DISPLAY / REGULAR</text><text x="1035" y="65">DISPLAY STUDY 01</text></g>',
        '<path d="M76 90H1364" stroke="#c7c2b7"/>',
        line('Angular grace',70,294,182),line('AaRrGg Q',70,595,260),
        '<path d="M76 664H1364" stroke="#c7c2b7"/>',
        line('ABCDEFGHIJKLMNOPQRSTUVWXYZ',72,786,66),
        line('abcdefghijklmnopqrstuvwxyz',72,906,80),
        line('0123456789 & ?!',72,1040,91),
        '<path d="M76 1100H1364" stroke="#c7c2b7"/>',
        '<g fill="#736b61" font-family="Arial,sans-serif" font-size="18"><text x="76" y="1150">Parallel lines. Sharp wedges. Controlled curves.</text><text x="76" y="1185">103 characters • Original vector outlines • TTF / OTF / WOFF2</text></g></svg>']
poster=''.join(poster)
(OUT/'specimen.svg').write_text(poster)
(OUT/'specimen.png').write_bytes(svg_to_png(poster.encode(),pixel_scale=1))

encoded=base64.b64encode((OUT/'build/fonts/HakilandDisplay-Regular.woff2').read_bytes()).decode()
sha=audit['formats']['woff2']['sha256']
characters=''.join(chr(c) for c in sorted(cmap) if c!=32)
grid=''.join(f'<button class="glyph" type="button" title="U+{ord(c):04X}" data-char="{html.escape(c,quote=True)}"><span>{html.escape(c)}</span><small>{ord(c):04X}</small></button>' for c in characters)
page='''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hakiland Display — Font specimen</title>
<style>
@font-face{font-family:"Hakiland Display";src:url(data:font/woff2;base64,__FONT__) format('woff2');font-weight:400;font-style:normal;font-display:block}
:root{color:#1a1916;background:#f8f6ef;font-family:Arial,sans-serif;font-size:14px}*{box-sizing:border-box}body{margin:0}main{max-width:1440px;margin:auto;padding:36px 64px}header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #c9c4b9;padding-bottom:22px;gap:24px}.eyebrow{font-size:12px;letter-spacing:2px;text-transform:uppercase}a{color:inherit;text-underline-offset:4px}nav{display:flex;gap:24px}h1{font:400 clamp(58px,14vw,188px)/.96 "Hakiland Display";margin:55px 0 15px}.intro{display:flex;justify-content:space-between;gap:28px;align-items:end;margin-bottom:48px}.intro p{font-size:17px;line-height:1.6;max-width:430px;margin:0;color:#635e55}.stamp{font-size:12px;color:#766d61}.section{border-top:1px solid #c9c4b9;padding:25px 0 35px}.label{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:24px}h2{font-size:12px;font-weight:400;letter-spacing:2px;text-transform:uppercase;margin:0}.controls{display:flex;gap:25px;align-items:center;flex-wrap:wrap}input{accent-color:#9a482e}input[type=range]{width:165px;vertical-align:middle}.sample{font:400 96px/1.22 "Hakiland Display";margin:0;padding:22px 0 35px;outline:none;white-space:pre-wrap;overflow-wrap:anywhere;min-height:290px;letter-spacing:0;font-kerning:normal}.sample:focus{box-shadow:inset 3px 0 #9a482e;padding-left:16px}.presets{display:flex;flex-wrap:wrap;gap:9px}button,.download{font:inherit;cursor:pointer;border:1px solid #ccc6bb;background:transparent;color:inherit;padding:10px 14px;border-radius:0}button:hover,.download:hover{background:#e9e4d9}button:focus-visible,a:focus-visible,input:focus-visible{outline:2px solid #9a482e;outline-offset:3px}.status{color:#56705c;font-size:12px}.warn{color:#9a3824;white-space:pre-wrap}.notes{display:grid;grid-template-columns:1fr 1fr 1fr;gap:40px}.notes .letter{font:100px/1.1 "Hakiland Display";margin-bottom:15px}.notes p{line-height:1.7;color:#635e55;max-width:330px}.notes strong{font-weight:400;color:#1a1916}.grid{display:grid;grid-template-columns:repeat(12,1fr);border-top:1px solid #d5cfc2;border-left:1px solid #d5cfc2}.glyph{min-width:0;border:0;border-bottom:1px solid #d5cfc2;border-right:1px solid #d5cfc2;padding:12px 2px}.glyph span{display:block;font:49px/1.35 "Hakiland Display"}.glyph small{font-size:9px;color:#8b8275}.downloads{display:flex;gap:12px;flex-wrap:wrap}.download{text-decoration:none;display:inline-block}.meta{font-family:monospace;font-size:11px;overflow-wrap:anywhere;color:#81786b;line-height:1.8}footer{border-top:1px solid #c9c4b9;padding-top:25px;line-height:1.8;color:#766d61}details{margin:24px 0}summary{cursor:pointer}.reference{width:100%;max-width:1000px;margin:20px 0}.notloaded .sample,.notloaded .glyph span{visibility:hidden}@media(max-width:700px){main{padding:24px}header{align-items:start}nav{gap:12px}.intro{display:block}.stamp{margin-top:20px}.label{display:block}.controls{margin-top:20px}.notes{grid-template-columns:1fr;gap:8px}.notes .letter{font-size:80px}.grid{grid-template-columns:repeat(6,1fr)}.sample{min-height:210px}h1{margin-top:40px}}
</style>
<body class="notloaded"><main>
<header><div class="eyebrow">Hakiland Display / Regular</div><nav><a href="#try">Try it</a><a href="#characters">Characters</a><a href="#download">Download</a></nav></header>
<h1>Hakiland<br>Display</h1><div class="intro"><p>A sharp display serif shaped by parallel lines, triangular details, and high-contrast curves.</p><div class="stamp">01 / REVISED PROTOTYPE · 103 CHARACTERS</div></div>
<section class="section" id="try"><div class="label"><h2>Type something</h2><div class="controls"><label>Size <input id="size" type="range" min="16" max="180" value="96"> <output id="size-value">96 px</output></label><label><input type="checkbox" id="kern" checked> Kerning</label></div></div>
<div id="sample" class="sample" role="textbox" aria-label="Type your sample text" aria-multiline="true" contenteditable="true" spellcheck="false">Angular grace
Quiet geometry.</div>
<p id="loading" class="status" role="status">Loading Hakiland Display…</p><p id="warning" class="warn" role="status"></p>
<div class="presets"><button data-text="Angular grace&#10;Quiet geometry.">Concept phrase</button><button data-text="aadd bbppqq&#10;gag gig QO QUEUE">Bowl &amp; tail details</button><button data-text="AV AW AY To Ta Ty&#10;Va Vo Ya Yo">Spacing pairs</button><button data-text="We Welcome Wednesday&#10;Woven Words Warm Waves">W spacing</button><button data-text="Type Variety Freedom&#10;flower offline offhand office">Review words</button><button data-text="0123456789&#10;&amp; ?! @ # % $">Figures &amp; symbols</button><button data-text="0123456789 147 777&#10;SHAPES bad dad $77.70&#10;Yes. No, wait; 12:30!">Stroke weight</button><button data-text="147 747 777&#10;HEFLNYI useful uniform&#10;Angular grace 17:47">Design consistency</button></div>
<p class="stamp">Neutral letter spacing. No ligature substitutions are configured. Best suited to display sizes.</p></section>
<section class="section notes"><div><div class="letter">Q</div><strong>A more distinctive tail</strong><p>The tail turns beneath the oval bowl into an angular ribbon, with parallel long edges and a small diamond terminal.</p></div><div><div class="letter">g</div><strong>One clean triangle</strong><p>A single 45-degree ear replaces the small horizontal attachment.</p></div><div><div class="letter">ad</div><strong>Controlled curves</strong><p>Broader bowls, higher counters, and a slanted d foot restore the source character. Individual SVG refinements preserve these details.</p></div></section>
<section class="section" id="characters"><div class="label"><h2>Character set</h2><span class="stamp">Click a character to inspect it</span></div><div class="grid">__GRID__</div><p class="stamp">103 encoded characters including space. Printable ASCII plus en/em dashes, curly quotes, bullet, and ellipsis. Accented letters and combining marks are not included.</p></section>
<section class="section" id="download"><div class="label"><h2>Font files</h2><span class="stamp">Version 0.100</span></div><div class="downloads"><a class="download" href="build/fonts/HakilandDisplay-Regular.ttf" download>Desktop · TTF ↓</a><a class="download" href="build/fonts/HakilandDisplay-Regular.otf" download>Desktop · OTF ↓</a><a class="download" href="build/fonts/HakilandDisplay-Regular.woff2" download>Web · WOFF2 ↓</a><a class="download" href="HakilandDisplay-Package.zip" download>Full package ↓</a></div><p>Install either desktop format. Editable SVG outlines and the Font Maker project are included in the package.</p><details><summary>Source artwork &amp; build details</summary><a href="references/reference.png">Original concept image</a><p class="meta">Revision __REV__<br>WOFF2 SHA-256 __HASH__</p><a href="quality-report.json">Technical checks</a> · <a href="specimen.png">Static specimen</a></details></section>
<footer>Original vector drawings based on the supplied concept. Font licensing has not been assigned.<br>Compiled with FontForge through Font Maker. This is a single-style display prototype.</footer>
</main><script>
const supported=new Set(__COVERAGE__);const sample=document.querySelector('#sample');
function update(){const missing=[...new Set([...sample.innerText].filter(c=>!supported.has(c.codePointAt(0))&&!['\\n','\\r','\\t'].includes(c)))];document.querySelector('#warning').textContent=missing.length?'Not in this font (browser fallback): '+missing.map(c=>c+' U+'+c.codePointAt(0).toString(16).toUpperCase().padStart(4,'0')).join(', '):'';}
document.querySelector('#size').addEventListener('input',e=>{sample.style.fontSize=e.target.value+'px';document.querySelector('#size-value').textContent=e.target.value+' px'});
document.querySelector('#kern').addEventListener('change',e=>{sample.style.fontKerning=e.target.checked?'normal':'none';sample.style.fontFeatureSettings='"kern" '+(e.target.checked?'1':'0')});
sample.addEventListener('input',update);
document.querySelectorAll('[data-text]').forEach(b=>b.addEventListener('click',()=>{sample.innerText=b.dataset.text;update()}));
document.querySelectorAll('[data-char]').forEach(b=>b.addEventListener('click',()=>{sample.innerText=b.dataset.char;update();document.querySelector('#try').scrollIntoView({behavior:'smooth'})}));
document.fonts.load('96px "Hakiland Display"','Angular grace Qg').then(faces=>{if(!faces.length)throw Error('No font face');document.body.classList.remove('notloaded');document.querySelector('#loading').textContent='Hakiland Display loaded · 103 characters';document.body.dataset.fontLoaded='true';update()}).catch(()=>{document.querySelector('#loading').textContent='Font could not load. Please reopen the specimen in a browser.';document.querySelector('#loading').className='warn'});
</script></body></html>'''
page=page.replace('__FONT__',encoded).replace('__GRID__',grid).replace('__REV__',info['revision']).replace('__HASH__',sha).replace('__COVERAGE__',json.dumps(sorted(cmap)))
page=page.replace('Version 0.100',f'Version {project.font.version}')
page=page.replace('Broader bowls, higher counters, and a slanted d foot restore the source character. Individual SVG refinements preserve these details.','A narrower lower bowl keeps a compact. Larger diamond dots and compensated diagonal strokes balance the surrounding letters.')
(OUT/'specimen.html').write_text(page)
reference=next((OUT/'references').glob('*'))
if reference.name!='reference.png':
    shutil.copy2(reference,OUT/'references/reference.png')
readme='''# Hakiland Display Regular — display prototype 0.100

Open `specimen.html` in a browser to type with the font. Install either
`build/fonts/HakilandDisplay-Regular.ttf` or `.otf`; `.woff2` is the webfont.

This revised prototype contains 103 encoded characters: A–Z, a–z, 0–9, printable ASCII,
curly quotes, en/em dashes, bullet, and ellipsis. No accented letters,
combining-mark positioning, additional weights, or ligatures are included.
Designed primarily for headings at 32 px and above.

The supplied artwork guided original vector construction; no existing font
outlines were imported or traced. The design uses high contrast, wedge serifs,
diamond dots, parallel stem/crossbar families and shared diagonal angles.
User refinements: single triangular g ear; a faceted Q tail with parallel edges;
reference-led a/d bowls and a slanted d foot. Curves retain optical compensation. The latest Q/a/d are revised candidates, not user-approved drawings.

`font.yaml` and `glyphs/` are the editable Font Maker sources. `refined/` contains individually edited source SVGs; the generator gives these priority and never overwrites them. `drawings/` has
readable codepoint filenames. The reproducible drawing script is
`source/build_wedge.py` (run within the Font Maker repository/environment).
`quality-report.json` records format coverage, measured bounds, metrics,
shaping and hashes. `specimen.svg` is a vector proof; `specimen.png` is its render.

Font license: not assigned. Font Maker's own software license does not assign
a license to this font. All possible kerning combinations have not been
individually reviewed.
'''
(OUT/'README.md').write_text(readme.replace('0.100',project.font.version)+'\nLatest refinements: compact a lower bowl, larger i/j dots, compensated diagonal weights, optically reviewed spacing, and the perceived-weight and design-consistency passes recorded in `weight-review.json` and `consistency-review.json`, including the full diagonal and hairline top bar of 7. `spacing-refinement.json` is loaded on each rebuild.\n')
(OUT/'source').mkdir(exist_ok=True)
shutil.copy2(ROOT/'examples/build_wedge.py',OUT/'source/build_wedge.py')
shutil.copy2(Path(__file__),OUT/'source/package_wedge.py')
with zipfile.ZipFile(OUT/'HakilandDisplay-Package.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.rglob('*'):
        if p.is_file() and p.suffix!='.zip' and p.name not in {'Wedge-Regular.ttf','Wedge-Regular.otf','Wedge-Regular.woff2'} and not any(part in ['.fontmaker','spacing-review','spacing-pass','revisions','proofs','glyph-review','review-pass-2','weight-audit','consistency-audit'] for part in p.relative_to(OUT).parts):
            z.write(p,Path('HakilandDisplay')/p.relative_to(OUT))
print(json.dumps({'specimen':str(OUT/'specimen.html'),'package':str(OUT/'HakilandDisplay-Package.zip'),'audit':audit['formats']},indent=2))

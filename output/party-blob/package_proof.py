"""Package inspected compiled outlines, a portable font tester, and acceptance evidence."""
import base64
import hashlib
import html
import json
import io
from pathlib import Path
from xml.etree import ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import uharfbuzz as hb
from font_maker.preview import shape_font, svg_to_png
from font_maker.store import ProjectStore

OUT = Path(__file__).resolve().parent
ROOT = OUT / 'font'
load = lambda name: json.loads((OUT / name).read_text())
build = load('build-report.json')
revision = build['revision']
project = ProjectStore(ROOT).load()
active = [''.join(rule.sequence) for rule in project.ligatures if rule.feature == 'dlig']
ET.register_namespace('', 'http://www.w3.org/2000/svg')
svg_ns = '{http://www.w3.org/2000/svg}'
poster = ET.Element(svg_ns+'svg', {'width':'1448','height':'800','viewBox':'0 0 1448 800'})
ET.SubElement(poster, svg_ns+'rect', {'width':'1448','height':'800','fill':'#f7f5ef'})
for index, name in enumerate(['snap-final.json','super-final.json']):
    proof = load(name)
    source = next(a for a in proof['artifacts'] if a['mime_type']=='image/svg+xml')
    scene = ET.parse(ROOT / source['path']).getroot()
    scale = 1.62
    width = float(scene.attrib['width'])
    g = ET.SubElement(poster, svg_ns+'g', {'transform':f'translate({(1448-width*scale)/2:.2f} {index*365-25}) scale({scale})'})
    for path in scene.findall(svg_ns+'path'):
        path.set('fill','#101010'); g.append(path)
(OUT/'specimen.svg').write_bytes(ET.tostring(poster))
(OUT/'specimen.png').write_bytes(svg_to_png(ET.tostring(poster),pixel_scale=2))

# A portable inventory sheet using paths from the actual delivered TTF.
sheet = ET.Element(svg_ns+'svg', {'width':'1448','height':'1590','viewBox':'0 0 1448 1590'})
ET.SubElement(sheet, svg_ns+'rect', {'width':'1448','height':'1590','fill':'#f7f5ef'})
lines = [
    ('Party Blob',240,210),
    ('ABCDEFGHIJKLM',110,410), ('NOPQRSTUVWXYZ',110,550),
    ('abcdefghijklm',125,690), ('nopqrstuvwxyz',125,845),
    ('0123456789',125,1010),
    ('! " # $ % & \' ( ) * + , - . /',75,1140),
    (': ; < = > ? @ [ \\ ] ^ _ ` { | } ~',75,1250),
    ('– — ‘ ’ “ ” • …',85,1370),
    ('Snap Engine / Super Rec',100,1530),
]
ttf = ROOT/'build/fonts/PartyBlob-Regular.ttf'
with TTFont(ttf) as font:
    glyphs = font.getGlyphSet()
    for text, size, baseline in lines:
        run = shape_font(ttf, text, {'kern':True,'dlig':True})
        scale = min(size/1000, 1320/run['total_advance'])
        cursor = (1448-run['total_advance']*scale)/2
        for g in run['glyphs']:
            pen = SVGPathPen(glyphs); glyphs[g['glyph_name']].draw(pen)
            ET.SubElement(sheet, svg_ns+'path', {'d':pen.getCommands(),'fill':'#101010',
                'transform':f'translate({cursor+g["x_offset"]*scale} {baseline-g["y_offset"]*scale}) scale({scale} {-scale})'})
            cursor += g['x_advance']*scale
(OUT/'character-specimen.svg').write_bytes(ET.tostring(sheet))
(OUT/'character-specimen.png').write_bytes(svg_to_png(ET.tostring(sheet),pixel_scale=1))

# Check actual font bytes and shaping across every delivered format.
checks = {}
coverage = ''.join(chr(cp) for cp in range(32,127)) + '–—‘’“”•…'
assert len(set(coverage)) == 103
texts = [coverage, 'Snap Engine','Super Rec','Party Blob', 'En Engine', 'Five affable office staff efficiently filed flawless affidavits.']
for artifact in build['artifacts']:
    path = ROOT / artifact['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact['sha256']
    with TTFont(path) as font:
        assert font['head'].unitsPerEm == 1000
        assert font['hhea'].descent == -270
        assert font['hhea'].ascent == 800
        assert font['OS/2'].sxHeight == 420
        assert font['OS/2'].sCapHeight == 720
        cmap = font.getBestCmap()
        assert all(ord(c) in cmap for text in texts for c in text)
        assert font['name'].getDebugName(1) == 'Party Blob'
        glyph_count = len(font.getGlyphOrder())
        mapped_count = len(cmap)
        # Shape the entire inventory from every export, including decompressed WOFF2.
        font.flavor = None
        stream = io.BytesIO(); font.save(stream)
    hbfont = hb.Font(hb.Face(stream.getvalue())); hbfont.scale = (1000,1000)
    for feature_on in (False, True):
        buffer = hb.Buffer(); buffer.add_str(coverage); buffer.guess_segment_properties()
        hb.shape(hbfont, buffer, {'kern':feature_on, 'liga':feature_on, 'dlig':feature_on})
        assert all(info.codepoint != 0 for info in buffer.glyph_infos)
    # HarfBuzz needs sfnt input, so decompress WOFF2 in memory before comparison.
    if path.suffix == '.woff2':
        with TTFont(path) as font:
            font.flavor=None; stream=io.BytesIO(); font.save(stream)
        face=hb.Face(stream.getvalue()); hbfont=hb.Font(face); hbfont.scale=(1000,1000)
        buffer=hb.Buffer(); buffer.add_str('En Engine'); buffer.guess_segment_properties()
        hb.shape(hbfont,buffer,{'kern':True,'dlig':True})
        names=[hbfont.glyph_to_string(i.codepoint) for i in buffer.glyph_infos]
    else:
        run=shape_font(path,'En Engine',{'kern':True,'liga':True,'dlig':True})
        names=[g['glyph_name'] for g in run['glyphs']]
    assert names.count('E_n') == 2
    checks[path.suffix[1:]]={'sha256_verified':True,'upm':1000,'coverage_verified':True,'encoded_characters':mapped_count,'glyph_count':glyph_count,'all_103_shape_without_notdef':True,'discretionary_substitution':names}
koff,kon=load('kern-shape-False.json'),load('kern-shape-True.json')
assert [(g['glyph_name'],g['cluster']) for g in koff['glyphs']]==[(g['glyph_name'],g['cluster']) for g in kon['glyphs']]
assert kon['total_advance']-koff['total_advance']==-350
assert load('sentence-shape-False.json')['glyphs']==load('sentence-shape-True.json')['glyphs']
(OUT/'acceptance.json').write_text(json.dumps({'revision':revision,'formats':checks,'kerning_delta':-350,'standard_ligature_comparison':'identical; no standard substitutions configured'},indent=2))

fontdata=base64.b64encode((ROOT/'build/fonts/PartyBlob-Regular.woff2').read_bytes()).decode()
reference=next((ROOT/'references').glob('*.png'))
refdata=base64.b64encode(reference.read_bytes()).decode()
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Party Blob — Font study</title>
<style>
@font-face{font-family:Syrup;src:url(data:font/woff2;base64,FONT_DATA) format('woff2');font-display:block}*{box-sizing:border-box}body{margin:0;background:#f7f5ef;color:#171714;font:15px/1.5 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:30px 48px}header{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid #bfbdb5;padding:0 0 18px}h1{font-size:18px;margin:0;font-weight:600}header span,.label{font:11px/1.5 ui-monospace,monospace;text-transform:uppercase;letter-spacing:1.5px;color:#646459}.hero{font-family:Syrup;font-size:clamp(64px,15.3vw,210px);line-height:1.25;text-align:center;font-feature-settings:'dlig' 1,'kern' 1;padding:26px 0 32px;white-space:nowrap}.hero div+div{margin-top:0}.panel{border-top:1px solid #bfbdb5;padding:22px 0}h2{font-size:17px;margin:0 0 14px}nav{display:flex;gap:24px;align-items:center;flex-wrap:wrap}label{display:flex;align-items:center;gap:8px}textarea{width:100%;resize:vertical;min-height:175px;background:transparent;border:1px solid #bfbdb5;border-radius:3px;padding:20px;font:96px/1.25 Syrup;outline-offset:4px;margin:18px 0 4px;color:inherit}input{accent-color:#454a30}input[type=range]{width:160px}.note{color:#66665b;font-size:13px}.alphabet{font:clamp(35px,5.5vw,78px)/1.6 Syrup;overflow-wrap:anywhere}.reference{width:100%;display:block;margin:15px 0}.download{color:inherit;text-underline-offset:4px}footer{font-size:12px;padding:20px 0 8px;color:#66665b}@media(max-width:700px){main{padding:20px}.hero{font-size:15vw}.label{font-size:9px}header{gap:20px}textarea{font-size:60px}}
.comparison{display:grid;grid-template-columns:60px minmax(0,1fr) minmax(0,1fr);gap:14px;border-top:1px solid #dedcd3;padding:18px 0;align-items:center}.kern-comparison{align-items:start}.comparison .sample{font:clamp(32px,4.8vw,76px)/1.35 Syrup;overflow-wrap:anywhere}.comparison .off{font-feature-settings:'kern' 1,'dlig' 0}.comparison .on{font-feature-settings:'kern' 1,'dlig' 1}.comparison .kern-off{font-feature-settings:'kern' 0,'dlig' 1}.comparison .kern-on{font-feature-settings:'kern' 1,'dlig' 1}button{background:transparent;color:inherit;border:1px solid #bfbdb5;border-radius:3px;padding:7px 10px;cursor:pointer}.comparison .sample span{display:block}@media(max-width:700px){.comparison{grid-template-columns:30px minmax(0,1fr) minmax(0,1fr);gap:8px}.comparison .sample{font-size:clamp(26px,6.6vw,46px)}}
</style><main><header><h1>Party Blob</h1><span>Original display study · 0.100</span></header>
<section class="hero" aria-label="Party Blob"><div>Party Blob</div></section>
<section class="panel"><h2>Try the font</h2><nav><label>Size <input id="size" type="range" min="24" max="180" value="96"><output id="sizeLabel">96 px</output></label><label><input id="kern" type="checkbox" checked>Kerning</label><label><input id="lig" type="checkbox" checked>Creative ligatures</label><button id="kernSample" type="button">Try kerning pairs</button><button id="ligSample" type="button">Try ligatures</button></nav><textarea id="tester" aria-label="Font test text" spellcheck="false">Party Blob, Snap Engine, Super Rec.</textarea><p class="note">Active ligature pairs: ACTIVE_PAIRS. Enable discretionary ligatures (dlig) in other applications.</p><p class="note" id="coverage" aria-live="polite">All characters in this text are supported.</p></section>
<section class="panel"><div class="label">103 characters · ACTIVE_COUNT optional ligatures</div><div class="alphabet">ABCDEFGHIJKLM<br>NOPQRSTUVWXYZ<br>abcdefghijklm<br>nopqrstuvwxyz<br>0123456789<br>! &quot; # $ % &amp; ' ( ) * + , - . /<br>: ; &lt; = &gt; ? @ [ &#92; ] ^ _ &#96; { | } ~<br>– — ‘ ’ “ ” • …</div><p class="note">All 95 printable ASCII characters plus eight common typographic symbols. Best at display sizes; narrow strokes are fragile at 32 px. Accented letters and further language coverage are future work.</p><p><a class="download" href="font/build/fonts/PartyBlob-Regular.ttf">TrueType</a> · <a class="download" href="font/build/fonts/PartyBlob-Regular.otf">OpenType</a> · <a class="download" href="font/build/fonts/PartyBlob-Regular.woff2">Webfont</a> · <a class="download" href="Party-Blob-proof.zip">Complete source package</a></p></section>
<section class="panel"><h2>Reference words</h2><div class="alphabet" style="font-feature-settings:'dlig' 1">Snap Engine<br>Super Rec</div></section>
<section class="panel"><h2>Kerning changes spacing</h2><p class="note">Only configured pairs change. These examples keep creative ligatures on and compare kerning off/on; the amount below is the change in total word width.</p>KERNING_COMPARISONS</section>
<section class="panel"><h2>Creative ligatures in words</h2><p class="note">Compare ordinary letters with the optional drawings. Kerning stays enabled on both sides.</p>LIGATURE_COMPARISONS<p><a class="download" href="ligature-proof.png">Full ligature proof sheet</a></p></section>
<section class="panel"><h2>From concept to font</h2><p class="note">The flowing ec and in, nested na and oo, and coordinated rt were redrawn as original vector outlines and reviewed in compiled text. AI sketches helped explore gestures; every active shape belongs to the font. Identity-changing treatments such as nn resembling m still require consultation unless full creative freedom was explicitly granted.</p><a class="download" href="concepts/ligature-exploration.png">na / in / ec concepts</a> · <a class="download" href="concepts/oo-rt-exploration.png">oo / rt concepts</a></section>
<section class="panel"><h2>Reference</h2><img class="reference" alt="Supplied Snap Engine and Super Rec lettering reference" src="data:image/png;base64,REF_DATA"><p class="note">Original outlines inspired by the supplied lettering. Optional ligatures develop its connected rhythm; turning them off restores the separate letterforms.</p></section>
<footer>Compiled with the repository's MCP tools and FontForge 20251009. Source revision REVISION.</footer></main>
<script>const text=document.querySelector('#tester'),size=document.querySelector('#size'),kern=document.querySelector('#kern'),lig=document.querySelector('#lig');const supported=new Set(COVERAGE);function update(){text.style.fontSize=size.value+'px';document.querySelector('#sizeLabel').textContent=size.value+' px';text.style.fontFeatureSettings='"kern" '+Number(kern.checked)+', "dlig" '+Number(lig.checked);const missing=[...new Set([...text.value].filter(c=>!supported.has(c)&&c!=='\\n'))];document.querySelector('#coverage').textContent=missing.length?'Not drawn in this study: '+missing.join(' '):'All characters in this text are supported.';}document.querySelector('#kernSample').addEventListener('click',()=>{text.value='AV Re Sn up';update();});document.querySelector('#ligSample').addEventListener('click',()=>{text.value='Party Snap record balloon inside';update();});for(const el of [text,size,kern,lig])el.addEventListener('input',update);update();</script></html>'''
examples={'En':['En','Engine'],'ec':['Rec','record','collect'],'in':['inside','spinning','final'],'na':['Snap','banana','natural'],'oo':['moon','balloon','groovy'],'rt':['Party','started','artwork']}
comparisons='<div class="comparison"><span></span><span class="label">Off</span><span class="label">On</span></div>'
for pair in active:
    words=''.join('<span>'+html.escape(word)+'</span>' for word in examples[pair])
    comparisons += '<div class="comparison"><span class="label">'+pair+'</span><div class="sample off">'+words+'</div><div class="sample on">'+words+'</div></div>'
kerning_comparisons='<div class="comparison"><span></span><span class="label">Kerning off</span><span class="label">Kerning on</span></div>'
for word in ['Rec','Pool']:
    off=shape_font(ttf,word,{'kern':False,'dlig':True})
    on=shape_font(ttf,word,{'kern':True,'dlig':True})
    delta=on['total_advance']-off['total_advance']
    assert delta != 0
    kerning_comparisons += f'<div class="comparison kern-comparison"><span class="label">{word}</span><div class="sample kern-off">{word}</div><div><div class="sample kern-on">{word}</div><p class="note">{delta} font units</p></div></div>'
page=page.replace('KERNING_COMPARISONS',kerning_comparisons)
page=page.replace('ACTIVE_PAIRS', ', '.join(active)).replace('ACTIVE_COUNT', str(len(active))).replace('LIGATURE_COMPARISONS', comparisons)
page=page.replace('FONT_DATA',fontdata).replace('REF_DATA',refdata).replace('REVISION',revision[:12]).replace('COVERAGE',json.dumps(coverage))
(OUT/'specimen.html').write_text(page)
print(json.dumps({'revision':revision,'checks':checks,'specimen':str(OUT/'specimen.html')},indent=2))

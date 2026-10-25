from pathlib import Path
import json, hashlib, shutil, uuid, html, math, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from font_maker.preview import shape_font, svg_to_png
from font_maker.store import ProjectStore

ROOT=Path(__file__).parent
MASTER=ROOT.parents[1]
FEATURES={'kern':True,'liga':False,'rlig':True,'dlig':False}
NEIGHBORS='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:!?()‘’“”'
CANDIDATES='ATVYFL'

def init():
    ROOT.mkdir(parents=True,exist_ok=True)
    ttf=MASTER/'build/fonts/HakilandDisplay-Regular.ttf'
    if not (ROOT/'baseline.ttf').exists(): shutil.copy2(ttf,ROOT/'baseline.ttf')
    trial=ROOT/'trial-project'
    if not trial.exists():
        trial.mkdir()
        shutil.copy2(MASTER/'font.yaml',trial/'font.yaml')
        shutil.copytree(MASTER/'glyphs',trial/'glyphs')
        shutil.copytree(MASTER/'references',trial/'references')
        s=ProjectStore(trial); p=s.load(); rev=s.revision(p)
        p.project_id=str(uuid.uuid4()); s.save(p,rev)
    return trial

def render(font,pairs,out,title,cols=8,font_size=50,scale=3,compare=None):
    font=Path(font); out=Path(out); out.parent.mkdir(exist_ok=True,parents=True)
    fonts=[font] if compare is None else [Path(compare),font]
    info={}
    for f in fonts:
        with TTFont(f) as t:
            gs=t.getGlyphSet(); paths={}
            for n in t.getGlyphOrder():
                p=SVGPathPen(gs); gs[n].draw(p); paths[n]=p.getCommands()
            info[f]=paths
    w=128*cols; cellh=139; h=42+math.ceil(len(pairs)/cols)*cellh
    pieces=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">', '<rect width="100%" height="100%" fill="#faf9f5"/>',f'<text x="12" y="20" font-family="sans-serif" font-size="13">{html.escape(title)} · {font_size}px × {scale} · '+('BASE / TRIAL' if compare else 'KERN OFF / ON')+'</text>']
    records=[]
    for i,pair in enumerate(pairs):
        x=(i%cols)*128; y=38+(i//cols)*cellh
        pieces.append(f'<path d="M{x} {y}h128v139h-128Z" fill="none" stroke="#ddd9cf" stroke-width=".5"/>')
        shaped=[]
        for j in range(2):
            f=fonts[j] if compare else font
            features={**FEATURES,'kern':True if compare else bool(j)}
            s=shape_font(f,pair,features); shaped.append(s)
            width=s['total_advance']*font_size/1000
            cursor=x+max(3,(128-width)/2); baseline=y+58+56*j
            for g in s['glyphs']:
                d=info[f][g['glyph_name']]; sx=cursor+g['x_offset']*font_size/1000
                pieces.append(f'<path d="{html.escape(d,quote=True)}" fill="{"#aaa69b" if not j else "#171815"}" transform="translate({sx} {baseline}) scale({font_size/1000} {-font_size/1000})"/>')
                cursor+=g['x_advance']*font_size/1000
        delta=shaped[1]['total_advance']-shaped[0]['total_advance']
        pieces.append(f'<text x="{x+6}" y="{y+14}" font-family="sans-serif" font-size="10">{html.escape(pair)} · Δ{delta}</text>')
        records.append({'pair':pair,'cell':i,'image':str(out.with_suffix('.png').relative_to(ROOT)),'baseline_shaping':shaped[0],'current_shaping':shaped[1],'review_status':'generated','font_size':font_size,'pixel_scale':scale})
    pieces.append('</svg>'); svg=''.join(pieces).encode(); out.with_suffix('.svg').write_bytes(svg); out.with_suffix('.png').write_bytes(svg_to_png(svg,pixel_scale=scale))
    return records

def baseline():
    init(); records=[]
    for c in CANDIDATES:
        for direction in ('before','after'):
            for name,neighbors in [('caps',NEIGHBORS[:26]),('lower',NEIGHBORS[26:52]),('punct',NEIGHBORS[52:])]:
                pairs=[c+n if direction=='before' else n+c for n in neighbors]
                records+=render(ROOT/'baseline.ttf',pairs,ROOT/'baseline'/f'{c}-{direction}-{name}',f'{c} {direction} {name}')
    inv={}
    for r in records:
        pair=r['pair']
        if pair not in inv: inv[pair]={'pair':pair,'evidence':[],'review_status':'generated'}
        inv[pair]['evidence'].append(r)
    manifest={'source_revision':ProjectStore(MASTER).revision(),'font_sha256':hashlib.sha256((ROOT/'baseline.ttf').read_bytes()).hexdigest(),'font_version':'0.111','candidates':CANDIDATES,'neighbors':NEIGHBORS,'features':FEATURES,'unique_pairs':len(inv),'pairs':list(inv.values())}
    (ROOT/'coverage.json').write_text(json.dumps(manifest,indent=2))
    print('generated',len(inv),len(records))

if __name__=='__main__': baseline()

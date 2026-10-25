import json,html,math,hashlib
from review import ROOT,FEATURES
from font_maker.preview import shape_font,svg_to_png
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

FONT=ROOT/'trial.ttf'
with TTFont(FONT) as t:
    gs=t.getGlyphSet(); PATHS={}
    for n in t.getGlyphOrder():
        pen=SVGPathPen(gs); gs[n].draw(pen); PATHS[n]=pen.getCommands()

def paths(text,x,y,size,font=FONT):
    if font!=FONT:
        with TTFont(font) as t:
            gs=t.getGlyphSet(); pth={}
            for n in t.getGlyphOrder():
                pen=SVGPathPen(gs);gs[n].draw(pen);pth[n]=pen.getCommands()
    else: pth=PATHS
    s=shape_font(font,text,FEATURES); out=[]
    for g in s['glyphs']:
        out.append(f'<path d="{html.escape(pth[g["glyph_name"]],quote=True)}" fill="#161714" transform="translate({x} {y}) scale({size/1000} {-size/1000})"/>')
        x+=g['x_advance']*size/1000
    return ''.join(out),s

def matrix():
    c=json.loads((ROOT/'coverage.json').read_text());pairs=[r['pair'] for r in c['pairs']]; records=[]
    for start in range(0,len(pairs),64):
        batch=pairs[start:start+64]; w=1024;h=42+math.ceil(len(batch)/8)*70
        out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="100%" height="100%" fill="#faf9f5"/>',f'<text x="10" y="20" font-family="sans-serif" font-size="13">Trial context {start+1}–{min(start+64,len(pairs))} · 32px × 3 · kern ON / liga OFF · controls H/n</text>']
        target=ROOT/'contexts'/f'context-{start//64+1:02d}'
        for i,pair in enumerate(batch):
            x=(i%8)*128;y=35+(i//8)*70
            control='H' if pair.isupper() else 'n';text=control+pair+control
            draw,shaping=paths(text,x+5,y+52,32)
            out+=[f'<path d="M{x} {y}h128v70h-128Z" fill="none" stroke="#ddd9cf"/>',f'<text x="{x+5}" y="{y+13}" font-family="sans-serif" font-size="10">{html.escape(pair)}</text>',draw]
            records.append({'pair':pair,'text':text,'image':str(target.with_suffix('.png').relative_to(ROOT)),'shaping':shaping,'font_size':32,'pixel_scale':3,'review_status':'generated'})
        out.append('</svg>');svg=''.join(out).encode();target.parent.mkdir(exist_ok=True);target.with_suffix('.svg').write_bytes(svg);target.with_suffix('.png').write_bytes(svg_to_png(svg,pixel_scale=3))
    (ROOT/'contexts/index.json').write_text(json.dumps({'font_sha256':hashlib.sha256(FONT.read_bytes()).hexdigest(),'cases':records},indent=2))

WORDS=[
 'AGORA ROAM CADENCE DAWN', 'AVATAR WAVE WAY LATELY',
 'TOWER TOGETHER VOGUE VOLUME', 'YOGA YOUTH YONDER',
 'FOLIO FORGE FOAM FJORD', 'LOCAL LOGO LOCATE',
 'Tide Tinker Tjorn Tm Tn Tp Td Tq', 'Text Tzara True Tulip Type Twist',
 'Value Veda Vigor Vogue Vd Vq Vp Vn', 'Vivid Vulture Vex Vying Vw Vz',
 'Yield Yiddish Yodel Ymir Yd Yq Yp', 'Year Yule Youth Yt Yx Yy Yz',
 'Face Fable Felt Food Forge Fd Fq', 'Fine Fjord Fruit Fuel Fy Fw Fx Fz',
 'Local Light Lively Lyric Lv Lw', '“A” ‘A’ A’s L’été L’art',
 'ACT: LIST; TV: WHY; HALF, HALF.', 'L? A? V! Y! T. F. W.',
 'aT bT cT eT gT hT iT jT kT', 'mT nT oT pT qT rT sT tT uT vT wT xT yT zT',
 'aV bV cV eV gV hV iV jV kV', 'mV nV oV pV qV rV sV tV uV vV wV xV yV zV',
 'aY bY cY eY gY hY iY jY kY', 'mY nY oY pY qY rY sY tY uY vY wY xY yY zY',
 'We Welcome Wednesday Woven Wedge', 'Wa We Wi Wj Wm Wn Wr Wu Wd Wq',
 'HHOOH noon minimum angular grace', '“We value your work,” said Ada.'
]
# ASCII-only equivalent for words containing unsupported accents.
WORDS=[x.replace('L’été','L’ete') for x in WORDS]

def words(size,scale,dir):
    records=[]; rowh=2*size*1.25+26;w=1040 if size>30 else 780
    for start in range(0,len(WORDS),7):
        batch=WORDS[start:start+7];h=32+len(batch)*rowh;target=ROOT/dir/f'words-{start//7+1:02d}'
        out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="100%" height="100%" fill="#faf9f5"/>',f'<text x="10" y="20" font-family="sans-serif" font-size="12">Word and regression context · {size}px × {scale} · baseline / trial, same ink · kern ON</text>']
        for i,text in enumerate(batch):
            y=35+i*rowh
            for n,f in enumerate([ROOT/'baseline.ttf',FONT]):
                draw,s=paths(text,12,y+size*(n+1)*1.25,size,f)
                draw=f'<text x="{w-66}" y="{y+size*(n+1)*1.25}" font-family="sans-serif" font-size="9" fill="#777">'+('BASE' if n==0 else 'TRIAL')+'</text>'+draw
                out.append(draw)
                if n:records.append({'text':text,'image':str(target.with_suffix('.png').relative_to(ROOT)),'shaping':s,'font_size':size,'pixel_scale':scale,'review_status':'generated'})
        out.append('</svg>');svg=''.join(out).encode();target.parent.mkdir(exist_ok=True);target.with_suffix('.svg').write_bytes(svg);target.with_suffix('.png').write_bytes(svg_to_png(svg,pixel_scale=scale))
    (ROOT/dir/'index.json').write_text(json.dumps({'font_sha256':hashlib.sha256(FONT.read_bytes()).hexdigest(),'cases':records},indent=2))

matrix();words(40,3,'words');words(24,1,'native')

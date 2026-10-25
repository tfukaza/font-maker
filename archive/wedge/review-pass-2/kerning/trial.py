from pathlib import Path
import json, hashlib, shutil
from review import ROOT, MASTER, render, init, FEATURES
from font_maker.store import ProjectStore
from font_maker.service import FontMakerService
from font_maker.models import KerningPair
from font_maker.preview import shape_font
from fontTools.ttLib import TTFont

# Individually selected from the inspected 36 baseline matrix sheets.
# Similar values record the resulting decision; they do not define kerning classes.
VALUES={
 'AG':-20,'OA':-20,'DA':-15,'CA':-10,'fA':-30,'vA':-25,'wA':-25,'yA':-25,
 'A‘':-60,'A’':-80,'A“':-60,'A”':-80,'‘A':-70,'“A':-70,'’A':-60,'”A':-60,
 'TC':-25,'TG':-25,'TO':-25,'TQ':-25,
 'Td':-85,'Tq':-85,'Tm':-55,'Tn':-55,'Tp':-55,'Ti':-30,'Tj':-30,'Tt':-25,'Tx':-45,'Tz':-45,
 'T:':-55,'T;':-55,
 'BT':-20,'DT':-25,'OT':-25,'QT':-20,'ST':-20,
 'aT':-50,'bT':-50,'cT':-60,'eT':-60,'gT':-20,'hT':-40,'iT':-25,'jT':-25,'kT':-35,
 'mT':-40,'nT':-40,'oT':-60,'pT':-50,'qT':-35,'rT':-35,'sT':-50,'tT':-20,'uT':-40,
 'vT':-30,'wT':-30,'xT':-30,'yT':-30,'zT':-30,
 '.T':-80,',T':-80,':T':-50,';T':-50,
 'VC':-25,'VG':-25,'VO':-25,'VQ':-25,'VS':-20,
 'Va':-90,'Vc':-90,'Vd':-90,'Ve':-90,'Vg':-90,'Vo':-90,'Vq':-90,'Vs':-75,
 'Vr':-55,'Vu':-55,'Vm':-55,'Vn':-55,'Vp':-55,'Vi':-35,'Vj':-35,
 'Vv':-35,'Vw':-35,'Vx':-35,'Vy':-35,'Vz':-35,'Vt':-25,'V:':-60,'V;':-60,
 'BV':-15,'DV':-25,'OV':-25,'QV':-25,'RV':-15,'SV':-15,
 'aV':-45,'bV':-45,'cV':-50,'eV':-50,'gV':-20,'hV':-35,'iV':-20,'jV':-20,'kV':-25,
 'mV':-35,'nV':-35,'oV':-50,'pV':-45,'qV':-30,'rV':-30,'sV':-40,'tV':-20,'uV':-35,
 'vV':-25,'wV':-25,'xV':-25,'yV':-25,'zV':-25,
 '.V':-80,',V':-80,':V':-50,';V':-50,
 'YC':-35,'YG':-35,'YO':-35,'YQ':-35,'YS':-25,
 'Yd':-90,'Yq':-90,'Yi':-40,'Yj':-40,'Ym':-55,'Yn':-55,'Yp':-55,'Yt':-25,'Yx':-30,'Yy':-30,'Yz':-30,'Y:':-55,'Y;':-55,
 'BY':-15,'DY':-35,'OY':-35,'QY':-30,'RY':-15,'SY':-20,
 'aY':-45,'bY':-60,'cY':-65,'eY':-65,'gY':-20,'hY':-40,'iY':-20,'jY':-20,'kY':-30,
 'mY':-40,'nY':-40,'oY':-65,'pY':-60,'qY':-40,'rY':-35,'sY':-50,'tY':-20,'uY':-40,
 'vY':-30,'wY':-30,'xY':-30,'yY':-30,'zY':-30,
 '.Y':-75,',Y':-75,':Y':-50,';Y':-50,
 'FC':-20,'FG':-20,'FO':-20,'FQ':-20,'FJ':-35,
 'Fa':-50,'Fc':-50,'Fd':-50,'Fe':-50,'Fg':-50,'Fo':-50,'Fq':-50,'Fs':-40,
 'Fm':-25,'Fn':-25,'Fp':-25,'Fr':-25,'Fu':-25,'Fi':-15,'Fj':-15,
 'Fv':-20,'Fw':-20,'Fx':-20,'Fy':-20,'Fz':-20,'F.':-100,'F,':-100,'F:':-45,'F;':-45,
 'LC':-20,'LG':-20,'LO':-20,'LQ':-20,
 'Lc':-15,'Ld':-15,'Le':-15,'Lg':-15,'Lo':-15,'Lq':-15,'Lv':-50,'Lw':-50,'Ly':-50,
 'L‘':-90,'L’':-120,'L“':-90,'L”':-120,'L?':-30,
}

def reason(pair):
    a,b=pair
    if a in 'ATVYFL' and b in '‘’“”': return f'{a} recedes from the high {b} quote, leaving excess upper white space; bring the quote toward the letter while preserving separate silhouettes.'
    if a in '‘’“”' and b=='A': return f'{a} floats away from A because its left diagonal recedes toward the apex; reduce the triangular opening with a direction-specific adjustment.'
    if a in '.,:;' or b in '.,:;': return 'The low/mid punctuation sits in the open cavity under a cap overhang or diagonal; attach it more clearly while retaining punctuation separation.'
    if a=='L': return 'L has a large upper right cavity, but its raised foot controls the nearest approach; use a restrained exception suited to this exact following contour.'
    if a=='F': return 'F leaves a lower right cavity; bring the following form inward only as far as its short middle arm and top beak permit.'
    if a in 'TVY': return f'{a} overhang/diagonal opens excessive white space before {b}; its left profile can enter that cavity without crowding the nearest top/shoulder.'
    if b in 'TVY': return f'{a} right contour leaves excess space below {b} left overhang/diagonal; the reverse order needs its own smaller value, preserving ascender/dot/ear clearance.'
    return 'The facing curved/diagonal profiles leave a wider optical opening than neighboring control gaps; this small exception balances the pocket without pinching a serif.'

def trial():
    pdir=init(); svc=FontMakerService(); opened=svc.open_project(str(pdir)); store=ProjectStore(pdir); p=store.load()
    with TTFont(ROOT/'baseline.ttf') as t: cmap=t.getBestCmap()
    old={r['pair']:r['evidence'][0]['current_shaping']['total_advance']-r['evidence'][0]['baseline_shaping']['total_advance'] for r in json.loads((ROOT/'coverage.json').read_text())['pairs']}
    pairs=[KerningPair(left=cmap[ord(k[0])],right=cmap[ord(k[1])],value=v) for k,v in VALUES.items()]
    svc.set_kerning(p.project_id,store.revision(),upsert_pairs=pairs)
    result=svc.build(p.project_id,['ttf']); font=pdir/result['artifacts'][0]['path']; shutil.copy2(font,ROOT/'trial.ttf')
    proposals=[{'pair':k,'left_glyph':cmap[ord(k[0])],'right_glyph':cmap[ord(k[1])],'before':old[k],'after':v,'reason':reason(k),'status':'trial-generated'} for k,v in VALUES.items()]
    report={'base_revision':json.loads((ROOT/'coverage.json').read_text())['source_revision'],'base_font_sha256':hashlib.sha256((ROOT/'baseline.ttf').read_bytes()).hexdigest(),'trial_revision':result['revision'],'trial_font_sha256':hashlib.sha256((ROOT/'trial.ttf').read_bytes()).hexdigest(),'kerning_overrides':VALUES,'proposals':proposals}
    records=[]
    for i in range(0,len(proposals),32):
        records+=render(ROOT/'trial.ttf',[x['pair'] for x in proposals[i:i+32]],ROOT/'trial'/f'changes-{i//32+1:02d}',f'Changes {i+1}–{min(i+32,len(proposals))}',compare=ROOT/'baseline.ttf')
    report['pair_evidence']=records
    (ROOT/'proposed-kerning.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'count':len(VALUES),'revision':result['revision'],'sha256':report['trial_font_sha256']}))

if __name__=='__main__': trial()

from pathlib import Path
import json,hashlib,shutil,string
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
O=Path('output/wedge');R=O/'consistency-audit/caps';manifest=json.loads((R/'manifest.json').read_text());old=O/'build/fonts/HakilandDisplay-Regular.ttf';new=R/'serif-candidate.ttf'
assert hashlib.sha256(old.read_bytes()).hexdigest()==manifest['font_sha256']
shutil.copy2(old,R/'baseline-0.113.ttf')
a,b=TTFont(old),TTFont(new);cmap=a.getBestCmap();changed=[]
for c,n in cmap.items():
 p1,p2=RecordingPen(),RecordingPen();a.getGlyphSet()[n].draw(p1);b.getGlyphSet()[n].draw(p2)
 if p1.value!=p2.value:changed.append(chr(c))
assert changed==list('EFLNY'),changed
assert a['hmtx'].metrics==b['hmtx'].metrics
assert a.getBestCmap()==b.getBestCmap()
for t in ['GPOS','GSUB']:assert a.getTableData(t)==b.getTableData(t)
notes={
'A':('Pointed triangular construction retains broad right diagonal and thin left leg; crossbar meets counter cleanly.','Apex y76 provides24-unit cap overshoot; crossbar24; diagonal taper retained as intentional optical construction, not forced parallel to unlike serif edges.'),
'B':('Upper/lower bowls share high vertical contrast and flat top/baseline with stemmed capitals.','116-unit stem;54x54 stem serifs;23-unit bowl closure; larger lower bowl retained rather than mirrored ellipses.'),
'C':('Open round fits O/G stress and tapered terminal vocabulary; aperture stays clean at24px.','Top/bottom y88/812; inner-leftx183 matches G/O family; wedge terminal intentionally diagonal, not a stem-head serif.'),
'D':('Broad bowl and flat left stem balance H/O without a visible shoulder bump.','116-unit stem;54x54 serifs;24-unit top/bottom bowl joins with tangent horizontal departure.'),
'E':('Shallower left head/foot cuts looked flatter beside H; exact45-degree candidate restores shared attached-serif rhythm.','Head y147→154 and foot y751→746, x reach54 retained. Arm-end terminals and counters unchanged.'),
'F':('Left head and bilateral foot used same shallow cuts as E; candidate aligns them with H/I.','Head y147→154; both foot junctions y751→746;54-unit reach retained. Crossbar/arm terminals unchanged.'),
'G':('Open round and strong inward spur preserve concept without a dark join or detached bar.','Round extrema y88/812; main stem118 versus116 control justified by separate spur assembly; asymmetric spur flanks remain intentional.'),
'H':('Control remains clean: matching stem serifs, parallel verticals and centered hairline bar.','Stems116; repeated54x54 serifs; crossbar24; flat top100/bottom800.'),
'I':('Narrow stem and bilateral wedges match H and remain distinct from lowercase.','116-unit stem and54x54 head/foot serifs; shared flat cap and baseline.'),
'J':('Descending hook/cut remains a coherent curved counterpart to angular j; not pulled up to flat baseline.','116-unit stem;54x54 top serif; endpoint y872 is deliberate72-unit descender; curve transitions into angular terminal.'),
'K':('Upper hairline and lower strong leg meet without a pinched counter; crisp cuts match wedge family.','116 stem; lower diagonal edges parallel dx220/dy440 and dx177/dy354;45-degree foot cuts; upper arm slope retained.'),
'L':('Head and lower-left cut were shallower than H; candidate makes matching45-degree attachment with no change to right arm wedge.','Two head joins y147→154 and lower-left y751→746;116 stem and24-unit horizontal unchanged.'),
'M':('Wide high-contrast construction fits N/H; center point leaves adequate negative space at smallsize.','Right116 stem with54x54 serifs; left24 hairline; inner point y796 deliberately near baseline; taper preserved.'),
'N':('Thin-stem wedge attachments looked flatter than M/H;45-degree candidate aligns their cuts while retaining diagonal and proportions.','Upper-left y150→154; right head junctions148→154/155 for respective54/55-unit reaches; foot752→746. Diagonal unchanged.'),
'O':('Round control has continuous stress and clean counter; reads level with flat caps through overshoot.','Extrema88/812; inner110/790;136-unit maximum sides,22-unit top/bottom; symmetric economical cubic structure.'),
'P':('Upper bowl and empty lower-right space remain proportionate with B/R; counter joins are crisp.','116 stem;54x54 serifs; top/bowl closing sections23; bowl copied legitimately into R from same original design.'),
'Q':('User-refined angular tail is retained: diamond onset, angled band and terminal wedge give deliberate expression without clashing with O.','O bowl unchanged; lower tail band edges(319,837)→(534,880) and(274,884)→(609,951) share slope0.2. Tail bottom951 fits descender budget.'),
'R':('P-family bowl continues into lively diagonal leg with wedge endpoint; preserves concept grace rather than rigid slash.','Stem116 and54x54 serifs; curved leg shoulder and flared endpoint intentionally differ from K straight leg.'),
'S':('Recent waist-lightening remains balanced with O/H and gives the two bowls consistent tension.','0.113 refined path preserved byte-for-byte; top/bottom88/812 and vertical terminal cuts retained.'),
'T':('Wide upper arm wedges and central stem maintain symmetry and spacing; no accidental serif step after overlap removal.','116 stem;54x54 baseline serif; arm hairline25; mirrored arm extremities23/667 around345.'),
'U':('Heavy left/light right transition remains smooth and coherent with contrast in N; bottom round clears baseline optically.','Left116/right25 stems;45-degree head cuts; bottom812; asymmetric interior curve retained as optical distribution.'),
'V':('Sharp bottom and open counter fit A/W; diagonal pair remains parallel without darkening the point.','Long edges slope2.5;26-unit flat bottom at814;14-unit overshoot differs appropriately from pointed A apex.'),
'W':('Recent diagonal compensation holds; two valleys and tapered upper wedges form an intentional wide rhythm.','Parallel repeated heavy diagonals near3:1dy/dx; bottoms814; narrow right branch differs from heavy strokes intentionally.'),
'X':('Crossing preserves thin/thick contrast and repeated wedge feet without a central knot.','Heavy edges dx400/dy600 exactly parallel; opposing hairline edges also parallel;50x50 serif cuts.'),
'Y':('Lower stem foot was shallower than H/I; candidate makes both foot slopes45 degrees with the same reach.','Both baseline join heights751→746;116-unit stem and54-unit reaches retained. Upper branches and their optical cuts unchanged.'),
'Z':('Long diagonal, arm wedges, and flat top/bottom are coherent with E/L; no need to equalize sloped arm ends with stem-head cuts.','Main diagonal slopes653/440 and653/439 differ negligibly from integer geometry;23/24-unit arm hairlines retained.')
}
records=[]
for c in string.ascii_uppercase:
 d=dict(manifest['glyphs'][c]);d.update(character=c,visual='inspected: '+notes[c][0],geometry='inspected: '+notes[c][1],decision='refine attached stem serif cuts' if c in changed else 'retain',proofs=[d['proof'],'proofs/context-56.png','proofs/context-24.png'])
 if c in changed:
  fp=R/f'glyph-U{ord(c):04X}.svg';d.update(candidate_source=str(fp),candidate_sha256=hashlib.sha256(fp.read_bytes()).hexdigest());d['proofs'] += ['proofs/serif-comparison-160.png','proofs/serif-comparison-56.png','proofs/serif-comparison-24.png','proofs/serif-detail.png']
 records.append(d)
report=dict(scope='A-Z general design consistency',status='completed visual and source audit; candidates frozen for parent integration review',baseline_version='0.113',revision=manifest['revision'],font_sha256=manifest['font_sha256'],reference='references/reference.png',inspected_sizes=[{'font_size':180,'pixel_scale':1},{'font_size':56,'pixel_scale':1},{'font_size':24,'pixel_scale':1}],candidate_sizes=[{'font_size':160,'pixel_scale':1},{'font_size':56,'pixel_scale':3},{'font_size':24,'pixel_scale':1},{'font_size':1000,'pixel_scale':1,'crop':'compiled stem-serif attachments'}],changed_characters=changed,candidate_font=str(new),candidate_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),invariants={'all_advances_bearings':True,'cmap':True,'GPOS':True,'GSUB':True,'all_unchanged_outlines':True,'unmodified_weight_corrections_and_Q':True},rationale='Restrain changes to visibly shallower attached stem-serif cuts. Preserve geometry differences serving distinct structural or optical roles, rather than equalizing every terminal angle.',glyphs=records)
(R/'review.json').write_text(json.dumps(report,indent=2))
(R/'review.md').write_text('''# Capitals: design consistency, baseline0.113

Reviewed all26 capital sourceSVGs and new compiled glyph proofs at180px,56px, and native24px, plus reference and words. The alphabet retains coherent proportions, high vertical contrast, curve stress, and shared flat/overshoot zones.

Recommend five local changes: **E F L N Y** attached straight-stem serif cuts become45 degrees, matching H/I/B/D/P/R/M. Previous depth47–50 over54-unit reach looked flatter in magnified comparisons. Changes preserve contours outside the attachment, all bounds, advance/bearings, kerning and substitutions. Candidate compiled proofs show no crowding or reading-size regressions.

Arm-end wedges, diagonal capitals, curved terminals, and optical taper remain distinct families. In particular Q's expressive tail, S's recent lightening, and W's recent diagonal compensation remain unchanged. No additional cap shape corrections were supported by this pass.

Frozen candidates: glyph-U0045.svg, glyph-U0046.svg, glyph-U004C.svg, glyph-U004E.svg, glyph-U0059.svg. Review/measurements per character are in review.json; before/after specimens and magnified compiled joins are in proofs/serif-*.png with SVG companions. Baseline font is archived as baseline-0.113.ttf, trial as serif-candidate.ttf. Parent still needs to inspect and integrate.
''')
print(json.dumps({'changed':changed,'sha256':report['candidate_sha256'],'baseline':report['font_sha256']},indent=2))

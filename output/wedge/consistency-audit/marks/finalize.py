from pathlib import Path
import json,hashlib,math,shutil
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
r=json.loads((OUT/'review.json').read_text());baseline=TTFont(OUT/'baseline.ttf');candidate=TTFont(OUT/'trial/build/fonts/HakilandDisplay-Regular.ttf')
observations={
' ': 'Empty outline and255-unit advance remain intentional. Native sentences establish a clear word break; there is no shape or baseline inconsistency to correct.',
'!': 'Tapered shaft retains the reference gesture. Current92-unit diamond has exact45-degree edges, baseline point800 and near-centered axis126 against shaft126.5. The half-unit offset is below compilation significance; the visible separation is clear.',
'"': 'Two identical tapered components share top100/bottom311 and171-unit separation. Flat-ended straight quotes intentionally differ from curved typographic quotes. Both appear level and belong to the wedge vocabulary.',
'#': 'Paired slanted stems use the same110/710 vector and equal33-unit horizontal span. Both51-unit crossbars are exactly horizontal. Joining cleanup introduces no pinholes; repeated alignment reads deliberate in numeric context.',
'$': 'Current refined S outline matches the recently reduced waist and maintains its letter-family curves. The27-unit central bar is vertical and projects equally enough for recognizable currency. Counters remain separate; no independent redraw warranted.',
'%': 'Two identical oval forms share radii130/177 and inner64/156; the second is translated406/371. Their extrema and vertical stress are consistent with0. The slash is parallel-sided and intentionally finer than the oval sides.',
'&': 'The reference two-counter construction survives with a small upper loop and broad lower loop. The main diagonal boundaries are nearly parallel; top/bottom counter stress and right-hand triangular exit stay coherent. Crossed joins remain clear at24px.',
"'": 'The single taper exactly matches one double-quote component. Shared100/311 levels and93/41 widths create an intentional straight-quote family.',
'(': 'Inner and outer cubic curves use matching vertical tangents at their centers. The tips are sharp, with a slight angled terminal cut rather than a wedge serif. Full enclosure height is intentionally greater than capitals and balances(10).',
')': 'Opening-parenthesis geometry mirrors exactly across the353-unit advance. Tip heights, central width and curvature therefore correspond; the compiled silhouette also reads balanced.',
'*': 'Five rotational wedge arms follow equal construction around one center; the central pentagon is open intentionally. The sharp outer ends and small negative center remain legible at24px. No rounded replacement needed.',
'+': 'Horizontal and vertical rectangles have36-unit thickness and centers within0.5unit. Shared square endings are appropriate for operators; wedge attachments would be intrusive.',
',': 'Revised92-unit head uses exact45-degree sides and matches the full-stop family. Its connected cubic tail preserves the original endpoint915 and does not show an abrupt bulge at the head/tail transition.',
'-': 'The short244-unit rectangular bar is45units thick, sharing lower edge557 with the longer dashes. Its3-unit higher center is an optical compensation for the shorter, heavier mark and is imperceptible in a-b context.',
'.': 'Current92-unit diamond is centered on x100, uses exact45-degree edges, and terminates on baseline800. It matches colon and ellipsis geometry and remains visible in decimals.',
'/': 'The two long edges have identical344/805 vectors, with horizontal terminal cuts. The baseline descender and ascender projection are deliberate for a separator, not lining-figure height. It pairs consistently with the mirrored backslash.',
'0': 'Symmetric oval has aligned outer/inner extrema and vertical stress, with22-unit top/bottom hairlines. The narrow proportion distinguishes0 fromO and matches the original figure row. No pinch or lopsided counter in1001.',
'1': 'The baseline foot has visibly shallower cuts than H/I despite a comparable upright: left35.62degrees and right36.03degrees. Chosen candidate changes both foot cuts to45degrees, preserving the original angled head,114-unit stem, bounds and advance. It now shares the wedge-foot grammar without becoming an I.',
'2': 'The upper hook follows the reference, transitioning from broad right curve into a fine descending sweep and solid baseline wedge. Top overshoot88 and flat baseline800 match round-to-flat figure construction. Counter opening remains clear; terminal angles are local tapers rather than repeated foot serifs.',
'3': 'The angled top-half construction is a defining reference trait. Horizontal top100 and curved bottom812 place it in the flat/round figure family. The short top wedge and lower pointed terminal are intentionally different from a full foot serif; no visible benefit from imposing one universal angle.',
'4': 'The broad flat top at SVG88 sits12units above H and flat3/5/7, with no pointed or curved extremum to justify it. The foot cuts are shallow38.53degrees. Chosen candidate sets top100 and footcuts45degrees, retains114-unit stem/30-unit crossbar, and adjusts the inner diagonal endpoint139→143.1847 so its edges are parallel. The open counter remains clear.',
'5': 'Flat top100 and rounded bottom812 align with3. The top bar flows into a thin slanted spine, then a broad round bowl; the lower pointed terminal repeats3 vocabulary. Its counter is deliberately rounder than the angled upper3 and retains clear aperture.',
'6': 'Outer upper sweep and inner bowl transition smoothly without a visible shoulder bump. The thin cut tip at SVG95 is an optical near-cap endpoint; the bowl overshoots to812 like0/8. The narrow upper exit matches the reference and the rotated9 counterpart.',
'7': 'Current0.113 has parallel diagonal edges,108-unit normal weight and92-unit top bar, but the user rejected its remaining perceived heaviness during this audit. This baseline is unresolved. Root owns the new lighter candidate and final judgment; no7 path is proposed or accepted here.',
'8': 'Two asymmetric counters preserve the reference crossing stress, with smaller upper eye and broader lower bowl. The top/bottom extrema88/812 match0; the inner cardinal tangents are smooth. Waist is visually clear and does not require forcing symmetric bowls.',
'9': 'The6-derived rotated construction preserves loop tension, matching24-unit-ish bottom-cut vocabulary and broad upper bowl. Top88 aligns with other rounds; the lower thin tip805 is a deliberate near-baseline overshoot. Native8989 remains distinct.',
':': 'Both current diamonds have92-unit bounds, exact45-degree edges and the samex109 axis. The lower tip uses baseline800, and the upper center439 aligns with the semicolon. Their unequal-to-letter-dot scale is role-specific, not drift.',
';': 'Upper diamond exactly matches colon placement/shape. Lower92-unit head and tail match comma with a9-unit horizontal translation. Both components now share the approved punctuation construction.',
'<': 'Upper/lower arms are symmetric around SVG499, ending in matched vertical cuts. The slight difference between outer and inner arm slopes produces a controlled bevel, not a visible asymmetric bulge. The operator is coherent with> and does not need wedge serifs.',
'=': 'Two35-unit rectangles sharex54..528 and190-unit offsets. All horizontal edges are parallel, with a clear interval and consistent square terminals.',
'>': 'Mirrored less-than has the same arm weights, axis499 and central20-unit bevel. The pair is visually balanced in the operator context.',
'?': 'The question hook preserves the concept diamond-like entry and gradual thinning into its stem. The current92-unit baseline dot is centered under the hook tail and matches!. Tangent transitions remain clean after compilation.',
'@': 'Outer spiral and internal slanted a intentionally form a separate compact construction. Vertical stress and the outer terminal echo the letters, while the internal counter remains open. Both spiral-to-stem and exit transitions look continuous.',
'[': 'Exact vertical92-unit spine and25-unit horizontal lips have square terminals. Levels50/950 intentionally enclose figures beyond cap/baseline. Negative inside corners remain square and clear.',
'\\': 'Exact mirror of slash across439-unit advance, preserving normal width, terminal cuts and vertical bounds. Any apparent sidebearing asymmetry reverses consistently.',
']': 'Exact mirrored bracket construction keeps levels50/950,92-unit stem and25-unit lips. It frames figures evenly with[.',
'^': 'The symmetric chevron intentionally tapers rather than behaving as a constant-width slash. Both outer endpoints share337, apex plateau94 and inner vertex174. This standalone accent-like symbol need not match foot-wedge45degrees.',
'_': 'The31-unit rectangle has exact horizontal edges and symmetric22-unit sidebearings. Its lowered889..920 zone intentionally distinguishes an underscore from the centered hyphen.',
'`': 'The standalone tapered accent uses a broad top and short slanted cut; the shape has the same sharp terminal vocabulary as the reference without pretending to be a positioned combining accent.',
'{': 'Outer and inner vertical segments have clean tangent transitions into the curved shoulders. Top and bottom terminal widths23 match, while the24-unit waist stays pointed but unknotted. Full-height enclosure is balanced around figures.',
'|': 'Centered32-unit vertical rectangle has square ends and spans the enclosure zone39..955. Its geometry is intentionally simpler than bracket shapes and maintains the operator family.',
'}': 'Exact mirror of the opening brace preserves widths, curve handles, waist position and top/bottom levels. No independent adjustment needed.',
'~': 'Two broad cubic crests share deliberate60-unit thickness at their horizontal extrema and taper toward diagonal terminal cuts. The undulation feels consistent with curved operators; it is not a pair of arbitrary circles.',
'–': 'The486-unit bar shares exact518/557 edges with the em dash. Square endpoints and39-unit weight are stable in text. Its size relationship to hyphen and em dash is legible.',
'—': 'The912-unit bar repeats the en-dash vertical position and39-unit weight exactly. Its much greater width is intentional; the outline and bearings do not clip.',
'‘': 'Opening curly quote is a rotated comma-like construction with81-unit head and curved tail. The attached tail explains its smaller head than the92-unit isolated full stop. It reads in the correct direction and has a shared family with double-opening quotes.',
'’': 'Closing quote maintains the same head/tail proportions as its opening counterpart, with a3-unit optical vertical offset in bounding extrema. No visible misalignment in context; retain the shape rather than equalizing bounding boxes mechanically.',
'“': 'Two repeated opening components use an exact171-unit translation. Endpoints, handles and head geometry correspond, preserving both visual rhythm and the slight compactness of quote marks.',
'”': 'Two repeated closing components exactly reuse the single closing quote at171-unit offset. Curvature and terminal cuts match the opening family without becoming straight quotation marks.',
'•': 'The centered150-unit diamond repeats45-degree punctuation geometry at a deliberately larger separator scale. Its higher vertical position528 distinguishes it from a full stop.',
'…': 'Three exact copies of the approved92-unit period sit on baseline800 at200-unit centers. Equal spacing and identical vertices remain evident at24px; no contour or alignment drift.'
}
assert len(observations)==51
sourceout=OUT/'source-svg';sourceout.mkdir(exist_ok=True)
selected=[]
for g in r['glyphs']:
 c=g['character'];source=ROOT/g['source'];copy=sourceout/f'glyph-U{ord(c):04X}.svg';shutil.copy2(source,copy)
 name=g['glyph'];p=BoundsPen(baseline.getGlyphSet());baseline.getGlyphSet()[name].draw(p)
 g.update({'visual':'inspected','geometry':'inspected','observation':observations[c],'reference_visible':c in '0123456789&?!','source_sha256':hashlib.sha256(copy.read_bytes()).hexdigest(),'source_snapshot':str(copy.relative_to(OUT)),'compiled_font_bounds':p.bounds,'recommendation':'refine_proposed' if c in '14' else 'user_rejected_pending_root_revision' if c=='7' else 'retain'})
 if c in '14':
  path=OUT/'candidate-svg'/f'glyph-U{ord(c):04X}.svg';record={'character':c,'glyph':name,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};selected.append(record);g['candidate']=record

def outlines(font):
 gs=font.getGlyphSet();result={}
 for n in font.getGlyphOrder():
  p=RecordingPen();gs[n].draw(p);result[n]=p.value
 return result
baseoutline=outlines(baseline);candoutline=outlines(candidate);changed=sorted(n for n in baseoutline if baseoutline[n]!=candoutline[n]);assert changed==['four','one']
assert baseline.getBestCmap()==candidate.getBestCmap();assert baseline.getTableData('GPOS')==candidate.getTableData('GPOS');assert baseline.getTableData('GSUB')==candidate.getTableData('GSUB');assert baseline['hmtx'].metrics==candidate['hmtx'].metrics
for c in '14':
 g=next(g for g in r['glyphs'] if g['character']==c);name=g['glyph'];p=BoundsPen(candidate.getGlyphSet());candidate.getGlyphSet()[name].draw(p);g['candidate_compiled_font_bounds']=p.bounds
r.update({'scope':'All51 encoded nonletter entries, including10digits,40marks andspace. General design consistency, not only stroke weight.','concept_reference':'references/codex-clipboard-9b9d5222-0485-40e2-b46a-a99d6d1fe063.png','concept_reference_inspected':True,'context_proofs':[{'file':'context-56.png','font_size':56,'pixel_scale':2},{'file':'context-24.png','font_size':24,'pixel_scale':1}],'candidate_proofs':[{'file':f'compare-{z}.png','font_size':z,'pixel_scale':1 if z==24 else 2} for z in [96,56,24]],'candidate_font_sha256':hashlib.sha256((OUT/'trial/build/fonts/HakilandDisplay-Regular.ttf').read_bytes()).hexdigest(),'candidate_changed_glyphs':changed,'candidate_invariants':{'cmap_unchanged':True,'hmtx_unchanged':True,'GPOS_unchanged':True,'GSUB_unchanged':True,'all_other_outlines_unchanged':True},'selected_candidates':selected,'candidate_validation':'Compiled successfully, no error/warning diagnostics; FONT_LICENSE_UNSET informational only.','measurements':{'one_foot_angles_before_degrees':[round(math.degrees(math.atan2(48,67)),3),round(math.degrees(math.atan2(48,66)),3)],'one_foot_angles_candidate_degrees':[45,45],'one_stem_width_unchanged':114,'four_foot_angles_before_degrees':[round(math.degrees(math.atan2(43,54)),3)]*2,'four_foot_angles_candidate_degrees':[45,45],'four_flat_top_svg_y_before':88,'four_flat_top_svg_y_candidate':100,'four_stem_width_unchanged':114,'four_crossbar_unchanged':30,'four_inner_diagonal_vertex_svg_y_before':139,'four_inner_diagonal_vertex_svg_y_candidate':143.1847,'four_candidate_diagonal_perpendicular':round(abs(314*(-6)-(-468)*33)/math.hypot(314,468),4)},'result':'Recommend two selected figure refinements:1/4 exact45-degree footcuts;4 flat-cap alignment and parallel thin diagonal. Other48entries retained.7 is explicitly unresolved after fresh user feedback and belongs to root revision. No master edits. Candidate files are frozen at this handoff.'})
(OUT/'review.json').write_text(json.dumps(r,indent=2,ensure_ascii=False));(OUT/'selected-candidates.json').write_text(json.dumps({'frozen':True,'source_revision':r['revision'],'candidate_font_sha256':r['candidate_font_sha256'],'candidates':selected},indent=2))
print(json.dumps({'coverage':len(r['glyphs']),'changed':changed,'candidates':selected,'candidate_font_sha256':r['candidate_font_sha256']},indent=2))

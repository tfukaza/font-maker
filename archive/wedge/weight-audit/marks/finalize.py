from pathlib import Path
import json,hashlib,math
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
r=json.loads((OUT/'review.json').read_text());baseline=TTFont(OUT/'baseline.ttf');candidate=TTFont(OUT/'trial/build/fonts/HakilandDisplay-Regular.ttf')
# These observations were written after reading paths.txt, five isolated sheets and both clean contexts.
observations={
' ':('spacing','No ink by design. The255-unit space separates words clearly in24px context.',{'advance':255}),
'!':('dot','The tapered shaft is coherent, but its78-unit dot is weak beside the large shaft and current i/j dots. The92-unit candidate preserves the centered diamond and gives the stop enough presence.',{'shaft_top_width':97,'shaft_max_width':123,'shaft_tip_width':21,'dot_diameter_before':78,'dot_diameter_candidate':92,'shaft_dot_clearance_candidate':79}),
'"':('quotation','Both93-to41-unit tapered components have equal weight. Their larger filled area remains appropriate for suspended quotation; no thickening is needed.',{'component_top_width':93,'component_bottom_width':41}),
'#':('operator','Two51-unit crossbars deliberately dominate the32.6-unit slanted stems. Their identical joins do not accumulate excessive blackness in #1 context.',{'crossbar':51,'slanted_stem_perpendicular':round(33*710/math.hypot(110,710),2)}),
'$':('S curve and hairline','The27-unit central bar is suitably fine. Parallel capital review identified excessive S waist mass; this sign shares that exact S base, so it must receive the same confirmed S correction rather than retain a heavier waist.',{'central_bar':27,'S_waist_before_perpendicular_from_caps_review':143.49,'S_waist_candidate_perpendicular_from_caps_review':128.95}),
'%':('round and slash','Each small oval has66-unit sides and21-unit extrema; the25.35-unit slash remains fine but continuous at24px. The contrast is deliberate and does not require matching upright letter stems.',{'oval_side':66,'oval_extrema':21,'slash_perpendicular':round(31*736/math.hypot(518,736),2)}),
'&':('compound diagonal and rounds','The long main diagonal is about96units normal to its edges. The crossing has sufficient white clearance and does not produce an isolated dark knot; bowl weight remains consistent with the concept.',{'main_diagonal_perpendicular_approx':round(abs(234*69-258*(-67))/math.hypot(234,258),2)}),
"'":('quotation','The single93-to41-unit tapered stroke matches each straight-double-quote component and is visible without dominating letters at24px.',{'top_width':93,'bottom_width':41}),
'(':('curved enclosure','The115-unit center weight tapers evenly to light terminals. Despite the taller outline, its perceived mass is balanced around10; do not make the entire enclosure monoline.',{'center_width':115}),
')':('curved enclosure','Mirrored115-unit center weight matches the opening parenthesis at both proof sizes. Neither side appears darker.',{'center_width':115}),
'*':('radial wedge','Five equal rotational arms taper82→34units; the open center and negative wedges prevent the compact mark becoming a blot. All arms remain visible at24px.',{'arm_outer_width':82,'arm_inner_width':34}),
'+':('operator','The36-unit cross reads evenly in horizontal and vertical directions. A thick letter-stem weight would make this functional sign visually intrusive.',{'horizontal':36,'vertical':36}),
',':('dot and tail','The existing81-by80-unit head looks finer than needed in text. Candidate uses a92-unit head with equal45-degree sides and a restrained redrawn tail connection; endpoint and descender remain unchanged.',{'head_before_width':81,'head_before_height':80,'head_candidate_width':92,'head_candidate_height':92,'tail_bottom_svg_y':915}),
'-':('horizontal separator','Its short244-unit span needs a45-unit bar to remain legible. It is heavier than the longer39-unit dashes intentionally, with consistent perceived emphasis.',{'bar':45,'length':244}),
'.':('dot','The78-unit diamond has little visual presence at24px, especially in decimals. Enlarging to92 keeps the baseline point and center fixed, improving stop visibility without reaching the106-unit i/j dot weight.',{'diameter_before':78,'diameter_candidate':92,'ink_area_before':3042,'ink_area_candidate':4232,'comparison_i_dot_diameter':106}),
'/':('thin diagonal','The28.5-unit normal weight is deliberately a thin separator. It remains continuous in a/b, and parallels the backslash; matching bold letter diagonals would overemphasize it.',{'perpendicular':round(31*805/math.hypot(344,805),2)}),
':':('dot','Equal78-unit diamonds are quiet beside numerals. Candidate92-unit diamonds preserve the lower baseline and upper439-unit SVG center, making12:30 clearer without closing the gap.',{'diameter_before':78,'diameter_candidate':92,'upper_center_svg_y':439,'gap_candidate':223}),
';':('dot and tail','Both components were underweight with the period family. Candidate combines the92-unit upper dot and revised comma head; the tail remains distinct and does not add a dark bump.',{'upper_dot_before':78,'upper_dot_candidate':92,'comma_head_before_width':81,'comma_head_candidate_width':92}),
'<':('operator diagonal','The approximately34-unit arms match the35/36-unit straight operators perceptually. The central bevel prevents excess acute-corner mass.',{'arm_perpendicular_approx':round(38/math.sqrt(1.25),2),'central_vertical_bevel':20}),
'=':('operator','Both35-unit bars have identical thickness and remain distinct at24px; matching plus by apparent weight is more relevant than the thick letters.',{'bar':35}),
'>':('operator diagonal','The matching less-than construction keeps both arms near34units and appears equally dark. No independent adjustment is needed.',{'arm_perpendicular_approx':round(38/math.sqrt(1.25),2),'central_vertical_bevel':20}),
'?':('curve and dot','The hook maintains thick/thin contrast. Its78-unit dot is too quiet under the broad curved head;92units improves balance and still leaves82units clearance below the hook.',{'dot_before':78,'dot_candidate':92,'hook_dot_clearance_candidate':82}),
'@':('spiral and internal letter','The94-unit outer-left stroke,27-unit top and37-unit outer-right stroke create intentional contrast. The inner a has enough white counter, and @home does not show an unusually dark enclosure.',{'outer_left_at_svg_y452':94,'outer_top':27,'outer_right_at_svg_y395':37}),
'[':('rectilinear enclosure','The92-unit upright is deliberately lighter than the full letter stems;25-unit lips frame rather than compete with figures. Corners do not swell.',{'vertical':92,'horizontal_lips':25}),
'\\':('thin diagonal','Mirrored slash shares28.5-unit normal thickness and is equally visible in contextual a\\b.',{'perpendicular':round(31*805/math.hypot(344,805),2)}),
']':('rectilinear enclosure','The92/25-unit upright/lip family matches the opening bracket, with no unevenness around10.',{'vertical':92,'horizontal_lips':25}),
'^':('tapered chevron','The accent-like standalone chevron intentionally tapers to28-unit outer termini and a48-unit apex plateau. Both halves carry equal perceived mass; it should not be converted to a uniform ribbon.',{'outer_terminal_span':28,'apex_plateau':48}),
'_':('horizontal separator','The31-unit low bar is long enough to remain visible at24px and light enough to avoid competing with the baseline serifs.',{'bar':31,'length':510}),
'`':('tapered accent','The92-unit broad end tapers to an approximately26.8-unit cut. The steep shape keeps adequate visible mass without looking like a bold diagonal stem.',{'broad_horizontal_end':92,'terminal_length':round(math.hypot(24,12),2)}),
'{':('curved enclosure','The102-unit vertical segments and23/24-unit terminals/waist preserve contrast. The inward waist remains light with no accumulated knot at24px.',{'vertical_segments':102,'top_bottom_terminal':23,'waist_terminal':24}),
'|':('thin vertical separator','A32-unit vertical is appropriate to a separator and close to the slash/operator family, while remaining visible between figures.',{'vertical':32}),
'}':('curved enclosure','Mirrored102-unit vertical segments and23/24-unit terminals match the opening brace perceptually at both sizes.',{'vertical_segments':102,'top_bottom_terminal':23,'waist_terminal':24}),
'~':('curved operator','The paired curves carry60-unit thickness at horizontal extrema, tapering toward the ends. This compensates for the compact curved shape; it looks balanced with other operators.',{'thickness_at_horizontal_extrema':60}),
'–':('horizontal separator','The486-unit bar uses39-unit thickness, maintaining visible text separation without the visual mass of a stem.',{'bar':39,'length':486}),
'—':('horizontal separator','The912-unit bar keeps the same39-unit stroke as en dash. Its longer span does not require adding stroke weight.',{'bar':39,'length':912}),
'‘':('curved quotation','The81-unit head plus long curved tail carries enough total ink in “Wedge” context. It may remain slightly smaller than the proposed92-unit full stop because its connected tail adds mass.',{'head_span':81}),
'’':('curved quotation','Mirrored quotation weight remains visible over the lowercase ascenders; the tail adds mass missing from an isolated dot.',{'head_span':81}),
'“':('curved quotation','Two repeated opening components share81-unit head span and171-unit separation. No dark cluster or vanishing mark is visible in24px text.',{'component_head_span':81,'component_offset':171}),
'”':('curved quotation','Closing pair shares single-quote construction and171-unit separation; both marks remain equally dark in the native proof.',{'component_head_span':81,'component_offset':171}),
'•':('separator dot','The150-unit diamond deliberately exceeds punctuation size; its greater ink area communicates a separator. It remains distinct without overwhelming adjacent words.',{'diameter':150,'ink_area':11250}),
'…':('dot sequence','Three78-unit diamonds are fine enough to fade at24px. Three92-unit candidates preserve200-unit center spacing and baseline points, improving rhythm without merging into a bar.',{'diameter_before':78,'diameter_candidate':92,'center_spacing':200})
}
proposed=set('!,. :;?…'.replace(' ',''))
assert len(observations)==41
for g in r['glyphs']:
 c=g['character'];family,observation,measures=observations[c]
 g.update({'family':family,'visual':'inspected','geometry':'inspected','observation':observation,'measurements':measures,'recommendation':'refine_proposed' if c in proposed else 'follow_capital_S_proposal' if c=='$' else 'retain','source_sha256':hashlib.sha256((ROOT/g['source']).read_bytes()).hexdigest()})
 if c in proposed:
  path=OUT/'candidate-svg'/f'glyph-U{ord(c):04X}.svg';g['candidate_source']=str(path.relative_to(ROOT));g['candidate_source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();g['candidate_visual']='inspected and recommended; master integration pending'
 if c=='$':g['dependency']='weight-audit/caps capital S and dollar candidate; dollar bar stays27units'
def outlines(font):
 gs=font.getGlyphSet();result={}
 for n in font.getGlyphOrder():
  p=RecordingPen();gs[n].draw(p);result[n]=p.value
 return result
baseoutline=outlines(baseline);candoutline=outlines(candidate);changed=[n for n in baseoutline if baseoutline[n]!=candoutline[n]]
expected=sorted(baseline.getBestCmap()[ord(c)] for c in proposed)
assert sorted(changed)==expected,(changed,expected)
assert baseline.getBestCmap()==candidate.getBestCmap()
assert baseline.getTableData('GPOS')==candidate.getTableData('GPOS')
assert baseline.getTableData('GSUB')==candidate.getTableData('GSUB')
assert {n:v[0] for n,v in baseline['hmtx'].metrics.items()}=={n:v[0] for n,v in candidate['hmtx'].metrics.items()}
r.update({'scope':'All41 encoded nondigit nonletter entries including space. Digits and letters belong to the other parallel audits. Source paths and compiled proofs inspected after generation.','context_proofs':[{'file':'context-56.png','font_size':56,'pixel_scale':2},{'file':'context-24.png','font_size':24,'pixel_scale':1}],'candidate_proofs':[{'file':f'compare-{z}.png','font_size':z,'pixel_scale':1 if z==24 else 2} for z in [96,56,24]],'candidate_font_sha256':hashlib.sha256((OUT/'trial/build/fonts/HakilandDisplay-Regular.ttf').read_bytes()).hexdigest(),'candidate_changed_glyphs':changed,'candidate_invariants':{'cmap_unchanged':True,'advances_unchanged':True,'GPOS_unchanged':True,'GSUB_unchanged':True,'all_other_outlines_unchanged':True},'candidate_validation':'Compiled successfully with no error/warning diagnostics. Informational FONT_LICENSE_UNSET only.','result':'Seven punctuation refinements recommended after compiled before/after comparison. Dollar refinement follows matching S proposal from capital audit. Other33 entries retained. No master edits made by this agent. This evidence supersedes prior blanket no-change mark review for the seven punctuation forms and dollar.'})
(OUT/'review.json').write_text(json.dumps(r,indent=2,ensure_ascii=False))
print(json.dumps({'coverage':len(r['glyphs']),'candidate_glyphs':changed,'candidate_sha256':r['candidate_font_sha256']},indent=2))

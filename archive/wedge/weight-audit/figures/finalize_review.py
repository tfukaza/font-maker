from pathlib import Path
import json,hashlib,math
D=Path(__file__).parent; O=D.parents[1]
paths=json.loads((D/'paths.json').read_text())
observations={
'0':'Retain: 121-unit mid-side strokes compensate the curved sides; 22-unit top/bottom hairlines remain clear in 00 and 06. No local swelling.',
'1':'Retain: 114-unit upright matches the figure stem family and H comparison. The broad base and head wedge add deliberate terminal mass, not a heavy body.',
'2':'Retain: right upper bowl is approximately119 units at the extremum; descending taper is light by contrast design. Solid baseline wedge balances the curved head in 22 and 23.',
'3':'Retain: the105-unit top bar is balanced by a light diagonal and open lower bowl. Lower right thick stroke is about126 units and its22-unit baseline hairline keeps 33 from darkening.',
'4':'Retain: 114-unit vertical,30-unit crossbar, and light left diagonal form a deliberate contrast system. The crossbar junction is local, with a spacious triangular counter.',
'5':'Retain:106-unit top bar balances a roughly124-unit bowl side and22-unit baseline hairline. Curve transitions stay open in 55 and35; no long heavy uninterrupted stroke comparable to7.',
'6':'Retain: approximately120–124-unit sides with22-unit baseline hairline and tapered entry. The shoulder join looks slightly darker locally, but 06/68 proofs show coherent overall weight and open counter.',
'7':'Change to candidateC: lighten long diagonal from about132.2 to108 perpendicular units, top bar109→92. Inspected original/A/B/C in number rows, repeated777, prices, and24px. C best balances1/4/6; preserve slope235:677,45-degree wedge, original outerbounds and546 advance.',
'8':'Retain: unequal bowl sides and thin extrema preserve the crossing contrast; central knot is intentional and does not merge into a heavy band in88/89. Do not equalize all its curved thicknesses.',
'9':'Retain: mirrored6 construction retains approximately120–124-unit sides,22-unit top hairline, and light exit. 89/98 comparisons have coherent apparent mass.'}
report=dict(baseline_revision='c5c1dfebdde7e86a107e9b155087a50ececa2a571cbd6d86c8d50010f22c451c',font_sha256=hashlib.sha256((O/'revisions/before-weight-audit/build/fonts/HakilandDisplay-Regular.ttf').read_bytes()).hexdigest(),proof_records='proof-records.json',visual_status='inspected',geometry_status='inspected',glyphs=[])
for c in paths:
 report['glyphs'].append(dict(character=c,codepoint=f'U+{ord(c):04X}',source=paths[c]['path'],source_sha256=hashlib.sha256(paths[c]['svg'].encode()).hexdigest(),visual='inspected',geometry='inspected',recommendation='change' if c=='7' else 'retain',observation=observations[c],proposal='seven-C.svg' if c=='7' else None))
report['seven']=dict(selected='C',independent_reviewer='weight_lower',before_diagonal=140/math.sqrt(1+(235/677)**2),after_diagonal=108,before_bar=109,after_bar=92,parallel_edge_slope=235/677,advance=546,reason='A/B retain excessive mass along a long uninterrupted diagonal; C is optically balanced in compiled display/native specimens.')
(D/'review.json').write_text(json.dumps(report,indent=2))
print('10 figure reviews recorded; candidate C selected')

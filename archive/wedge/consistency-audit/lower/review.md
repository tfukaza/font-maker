# Hakiland Display0.113 — lowercase design-consistency review

All26 lowercase glyphs were read as SVG commands and inspected in fresh compiled TTF proofs:160px isolated cells,56px context, and native24px. The original concept was inspected alongside these proofs. Candidates f/u were separately compiled and compared at96px and native24px.

Recommended changes:

- **f:** align upright foot with l/h/i:54-unit rise and45° flares instead of a shallow42-unit rise. Keep106-unit stem, f arch, terminal and crossbar.
- **u:** align both head wedges with n/i/j and exit wedge with d. Keep bowl curves,106-unit stems and advance. Head extremum moves1 unit left; exit extends5 units right.

Candidate files are frozen: `glyph-U0066.svg` and `glyph-U0075.svg`. Master project and skills were not edited. `candidate.ttf` contains these two changes only. All advances and GPOS bytes are unchanged; u LSB follows its new xmin26→25. Temporary build validation has no errors; see trial.json.

| Glyph | Decision | Evidence and rationale |
|---|---|---|
| a | retain | Narrower teardrop lower bowl and angled exit preserve concept identity. Outer left extremum82 and inner186 maintain the approved104-unit side; aligned upper entry handles feed the diagonal counter without a second bulge. The asymmetric bowl is deliberately not o-like. |
| b | retain | Ascender head matches h/k/l: upper54/162 slope and45-degree entry. Bowl shares p coordinates; horizontal extrema tangents and24-unit top/bottom bowl rails are clean. One-sided baseline foot avoids a right spur beneath bowl. |
| c | retain | Outer body318–812 agrees with e/o. Upper triangular terminal remains from reference; the lower thin angled exit and open aperture are related to e without copying its horizontal bar. |
| d | retain | Keeps the0.113 lower-counter correction: bottom778, horizontal handles, lower join709. Ascender head and exit slope are both1/3. Counter is deliberately asymmetric and slightly higher than b/q because the left-side bowl joins an upright on right. |
| e | retain | Body318–812 matches c/o. Counter has a22-unit top and24-unit horizontal bar; flat ends remain aligned. Lower exit follows c family and the distinct bowl/bar construction remains recognizable. |
| f | refine | Current foot flares begin at758 versus746 for l/h/i; shallow42-unit rise makes the base a flattened wedge. Candidate uses746 and54-unit flare on each side, leaving106-unit stem, crossbar, arch and terminal intact. Compiled before/after gives a coherent foot beside l/i/h without opening a new gap. |
| g | retain | Approved simple triangular ear has horizontal base338 and45-degree diagonal338,338→448,228. Upper bowl318–644 uses vertical elliptical stress; lower loop and curved link remain distinct, appropriate to two-storey g. Lower extremum1023 coheres with220-unit flat descenders plus round overshoot. |
| h | retain | Main stem/head/feet match l. Shoulder exactly shares n construction, including outer318 top and inner361 top. Straight stem joins are continuous after overlap cleanup. |
| i | retain | Body top320 and head374→430 share n construction, not accidentally shortened.106×106 diamond139–245 centered135 exactly over106-unit stem82–188;75-unit clearance stays open at24px. |
| j | retain | Authoritative source already matches i: head35,374→197,320 and45-degree entry→91,430.106×106 diamond uses same139–245 vertical bounds; curved descender ends1030, a10-unit optical depth beyond flat p/q. |
| k | retain | Ascender stem and foot share l/h. Open branch and inclined lower leg have attachment-specific flares; their slight taper preserves counter and avoids a crowded crossing. No reason to force leg-attached flare into the upright-foot template. |
| l | retain | Straight106-unit control stem with770-unit ascender,1/3 head slope,45-degree entry and45-degree54-unit feet. Clean baseline and coherent width against i/h. |
| m | retain | Outer shoulders318 and inner361 align with n/h. Middle shoulder is compressed to accommodate a second arch; keeping distinct339/342-width lobes avoids a mechanical triple-stem expansion. All stems/feet meet common baseline. |
| n | retain | Control: body top320 head/318 curved shoulder,106-unit first stem and105-unit second,45-degree feet. The slightly thin join entering the upright gives contrast and clear counter at24px. |
| o | retain | Round control has318/812 outer and340/790 inner extrema,113-unit sides with continuous tangent transitions. Symmetry belongs here but should not be imposed on a/d or open c/e. |
| p | retain | Bowl exactly shares b above baseline; head repeats n. Flat descending foot1020 coheres with q and is shallower than curved/pointed j/y. Counter and attachment remain open. |
| q | retain | Bowl remains related to b/p with left-right structural reversal; no longer has an extraneous spur. Short upper head slope35/106 is near1/3 and joins bowl at370 without a detached serif. Baseline bowl812 and flat foot1020 are coherent. |
| r | retain | 106-unit stem and standard feet. Faceted terminal has45-degree edges and312 top,8 units above stemhead: optical compensation for a point, not baseline drift. Its asymmetric inner join keeps the distinctive reference gesture. |
| s | retain | Body318–812 and22-unit round rails match o/c/e. Both triangular terminals are vertical-faced but have their own wedge slopes to enter curved bowls; enforcing g-ear45-degree geometry would distort their curve flow. |
| t | retain | Diagonal head is exactly45 degrees, related to g ear; crossbar330–355 matches f. Tall top162 is distinct from ascenders by construction; hook turns to812 with an open wedge-like exit that fits c/e family. |
| u | refine | Current heads use46/161 slope and41/55 entry, flatter than n/i/j; exit uses58/157 versus d54/162. Candidate aligns head slopes54/162 and entries56/56, and exit54/162 at812; curves and106-unit stems are unchanged. Visual differences are subtle at24px but clear beside n/d in display proof. |
| v | retain | Top330 flat rails match x/z. Parallel diagonal edges retain prior perceived-weight compensation; thin ascending diagonal and13-unit pointed overshoot distinguish it from upright n. |
| w | retain | Two descending strokes use the same slope; right ascending hairline and internal join preserve open triangular counters. Top330 and bottom813 agree with v/y. Preserve approved diagonal weight; its wider footprint is intentional. |
| x | retain | Both crossing stroke pairs are parallel. Flat rails330/800 and38-unit flare depths match the diagonal family. Resolved overlapping contours have no central sliver; angled construction does not require54-unit upright flares. |
| y | retain | Body is the exact approved v construction and retains its weight. Descending tail has its own curved terminal, reaching1029, matching j optically rather than forcing both to flat p/q1020. |
| z | retain | Top330/bottom800 match flat diagonal forms.23-unit upper rail and23-unit lower are balanced. Approximate1-unit diagonal divergence is restrained taper, not a visible kink; broad top/bottom end wedges fit its horizontal architecture. |

Compiled comparisons: `uf-comparison.png`, `uf-native.png`. Source inventory: `paths.txt`. Full measurable bounds and candidate hashes: `review.json`.

This audit retains intended variation: asymmetric bowls, compact m, optical point overshoot, and different flat versus curved descenders. It does not treat exact geometry as proof of optical quality.

Additional inspected160px detail comparisons at pixel_scale3: `f-detail.png`, `u-detail.png`.

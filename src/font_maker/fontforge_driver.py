"""Pure-stdlib script executed by the FontForge command-line runtime.

Do not import this module in the long-lived MCP process. FontForge executes it
with its embedded Python interpreter.
"""

import json
import sys

import fontforge


def draw_commands(glyph, contours, x_shift=0):
    pen = glyph.glyphPen()
    for contour in contours:
        for command in contour:
            operation = command["op"]
            points = [tuple((point[0] + x_shift, point[1])) for point in command["points"]]
            if operation == "moveTo":
                pen.moveTo(points[0])
            elif operation == "lineTo":
                pen.lineTo(points[0])
            elif operation == "curveTo":
                pen.curveTo(*points)
            elif operation == "qCurveTo":
                pen.qCurveTo(*points)
            elif operation == "closePath":
                pen.closePath()
            elif operation == "endPath":
                pen.endPath()
            else:
                raise ValueError(f"Unsupported pen operation: {operation}")


def draw_notdef(glyph, upm):
    width = int(upm * 0.6)
    inset = int(upm * 0.08)
    top = int(upm * 0.7)
    pen = glyph.glyphPen()
    pen.moveTo((inset, 0))
    pen.lineTo((width - inset, 0))
    pen.lineTo((width - inset, top))
    pen.lineTo((inset, top))
    pen.closePath()
    inner = inset * 2
    pen.moveTo((inner, inset))
    pen.lineTo((inner, top - inset))
    pen.lineTo((width - inner, top - inset))
    pen.lineTo((width - inner, inset))
    pen.closePath()
    glyph.width = width


def add_lookups(font, request):
    pairs = request.get("kerning_pairs", [])
    classes = request.get("kerning_classes", [])
    if pairs or classes:
        lookup = "fontmaker_gpos_kern"
        font.addLookup(
            lookup,
            "gpos_pair",
            (),
            (("kern", (("latn", ("dflt",)),)),),
        )
        if pairs:
            subtable = lookup + "_pairs"
            font.addLookupSubtable(lookup, subtable)
            for pair in pairs:
                font[pair["left"]].addPosSub(subtable, pair["right"], pair["value"])
        for index, class_request in enumerate(classes):
            font.addKerningClass(
                lookup,
                f"{lookup}_classes_{index}",
                tuple(tuple(group) for group in class_request["first_classes"]),
                tuple(tuple(group) for group in class_request["second_classes"]),
                tuple(class_request["offsets"]),
            )

    by_feature = {}
    for rule in request.get("ligatures", []):
        by_feature.setdefault(rule["feature"], []).append(rule)
    for feature, rules in by_feature.items():
        lookup = f"fontmaker_gsub_{feature}"
        subtable = lookup + "_ligatures"
        font.addLookup(
            lookup,
            "gsub_ligature",
            (),
            ((feature, (("latn", ("dflt",)),)),),
        )
        font.addLookupSubtable(lookup, subtable)
        for rule in rules:
            font[rule["replacement"]].addPosSub(subtable, tuple(rule["sequence"]))


def suggest_spacing(font, request):
    spacing = request["spacing"]
    selected = tuple(spacing["glyph_names"])
    if selected:
        font.selection.select(*selected)
        font.autoWidth(spacing["target_separation"])
    glyph_metrics = {
        name: {
            "advance_width": round(font[name].width),
            "left_side_bearing": round(font[name].left_side_bearing),
            "right_side_bearing": round(font[name].right_side_bearing),
        }
        for name in selected
    }

    pair_candidates = spacing.get("pair_candidates", [])
    kerning_pairs = []
    if pair_candidates:
        lookup = "fontmaker_spacing_probe"
        subtable = lookup + "_pairs"
        font.addLookup(lookup, "gpos_pair", (), (("kern", (("latn", ("dflt",)),)),))
        font.addLookupSubtable(lookup, subtable)
        left_names = tuple(sorted({pair[0] for pair in pair_candidates}))
        right_names = tuple(sorted({pair[1] for pair in pair_candidates}))
        font.autoKern(
            subtable,
            spacing["target_separation"],
            left_names,
            right_names,
            minKern=spacing.get("minimum_kerning", 5),
        )
        requested = {tuple(pair) for pair in pair_candidates}
        for left in left_names:
            for record in font[left].getPosSub(subtable):
                if record[1] == "Pair" and (left, record[2]) in requested:
                    kerning_pairs.append(
                        {"left": left, "right": record[2], "value": int(record[5])}
                    )
    return {"glyph_metrics": glyph_metrics, "kerning_pairs": kerning_pairs}


def main():
    request_path, result_path = sys.argv[-2:]
    with open(request_path) as stream:
        request = json.load(stream)

    font = fontforge.font()
    metadata = request["font"]
    metrics = request["metrics"]
    font.encoding = "UnicodeFull"
    font.ascent = metrics["ascender"]
    font.descent = abs(metrics["descender"])
    # FontForge defines em as ascent + descent. Set the requested em last,
    # before drawing, and write independent line metrics below.
    font.em = metrics["units_per_em"]
    font.familyname = metadata["family_name"]
    font.fontname = metadata["postscript_name"]
    font.fullname = f"{metadata['family_name']} {metadata['style_name']}"
    font.version = metadata["version"]
    font.os2_typoascent_add = False
    font.os2_typodescent_add = False
    font.os2_winascent_add = False
    font.os2_windescent_add = False
    font.hhea_ascent_add = False
    font.hhea_descent_add = False
    font.os2_typoascent = metrics["ascender"]
    font.os2_typodescent = metrics["descender"]
    font.os2_typolinegap = metrics["line_gap"]
    font.os2_winascent = max(metrics["ascender"], metrics["cap_height"])
    font.os2_windescent = abs(metrics["descender"])
    font.os2_capheight = metrics["cap_height"]
    font.os2_xheight = metrics["x_height"]
    font.hhea_ascent = metrics["ascender"]
    font.hhea_descent = metrics["descender"]
    font.hhea_linegap = metrics["line_gap"]
    if metadata.get("designer"):
        font.appendSFNTName("English (US)", "Designer", metadata["designer"])
    if metadata.get("license_text"):
        font.appendSFNTName("English (US)", "License", metadata["license_text"])
    if metadata.get("license_url"):
        font.appendSFNTName("English (US)", "License URL", metadata["license_url"])

    notdef = font.createChar(-1, ".notdef")
    draw_notdef(notdef, metrics["units_per_em"])
    notdef.correctDirection()
    notdef.addExtrema()
    notdef.round()

    names = set()
    for glyph_request in request["glyphs"]:
        name = glyph_request["name"]
        names.add(name)
        codepoints = glyph_request.get("codepoints", [])
        primary = codepoints[0] if codepoints else -1
        glyph = font.createChar(primary, name)
        # FontForge can infer a presentation-form mapping from names such as
        # s_t even with createChar(-1, name). The manifest owns all mappings.
        glyph.unicode = primary
        glyph.altuni = None
        if len(codepoints) > 1:
            glyph.altuni = tuple((value, -1, 0) for value in codepoints[1:])
        draw_commands(glyph, glyph_request["contours"], glyph_request.get("x_shift", 0))
        glyph.width = glyph_request["advance_width"]
        options = request["build_options"]
        if options.get("remove_overlaps"):
            glyph.removeOverlap()
        if options.get("correct_contour_direction"):
            glyph.correctDirection()
        if options.get("add_extrema"):
            glyph.addExtrema()
        if options.get("round_coordinates"):
            glyph.round()
        # Rounding can collapse nearby overlap intersections onto the same
        # integer coordinate. Run a final cleanup so the generated outline,
        # rather than the pre-rounded geometry, is what validation inspects.
        if options.get("remove_overlaps"):
            glyph.removeOverlap()
        if options.get("correct_contour_direction"):
            glyph.correctDirection()

    if "space" not in names:
        space = font.createChar(0x20, "space")
        space.width = int(metrics["units_per_em"] * 0.25)

    if request.get("operation") == "suggest_spacing":
        proposal = suggest_spacing(font, request)
        version = fontforge.version()
        font.close()
        with open(result_path, "w") as stream:
            json.dump(
                {
                    "ok": True,
                    "fontforge_version": version,
                    "spacing": proposal,
                },
                stream,
                sort_keys=True,
            )
        return

    add_lookups(font, request)
    glyph_validation = {}
    for glyph in font.glyphs():
        flags = int(glyph.validate())
        if flags:
            glyph_validation[glyph.glyphname] = flags
    validation = int(font.validate())
    outputs = {}
    for format_name, output_path in request["outputs"].items():
        font.generate(output_path)
        outputs[format_name] = output_path
    version = fontforge.version()
    font.close()

    with open(result_path, "w") as stream:
        json.dump(
            {
                "ok": True,
                "fontforge_version": version,
                "validation": validation,
                "glyph_validation": glyph_validation,
                "outputs": outputs,
            },
            stream,
            sort_keys=True,
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        result = {"ok": False, "error": f"{type(error).__name__}: {error}"}
        try:
            result_path = sys.argv[-1]
            with open(result_path, "w") as stream:
                json.dump(result, stream)
        except Exception:
            pass
        print(result["error"], file=sys.stderr)
        sys.exit(1)

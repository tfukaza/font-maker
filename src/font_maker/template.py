"""Generate the canonical shared-coordinate glyph template."""

from __future__ import annotations

from xml.sax.saxutils import escape

from .models import FontMetadata, SvgContract, VerticalMetrics


def render_glyph_template(font: FontMetadata, metrics: VerticalMetrics, svg: SvgContract) -> str:
    x, y, width, height = svg.view_box

    def svg_y(font_y: float) -> float:
        return svg.baseline_y - (font_y / svg.scale) + svg.translate_y

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{x:g} {y:g} {width:g} {height:g}"
     width="{width:g}" height="{height:g}"
     data-fontmaker-family="{escape(font.family_name)}"
     data-fontmaker-upm="{metrics.units_per_em}"
     data-fontmaker-baseline-y="{svg.baseline_y:g}">
  <title>{escape(font.family_name)} shared glyph template</title>
  <desc>Draw filled outlines only inside #glyph. Do not crop or move the baseline.</desc>
  <g id="fontmaker-guides" data-fontmaker-ignore="true"
     fill="none" stroke-width="1" vector-effect="non-scaling-stroke">
    <line id="ascender-guide" x1="{x:g}" x2="{x + width:g}" y1="{svg_y(metrics.ascender):g}" y2="{svg_y(metrics.ascender):g}" stroke="#8b5cf6" opacity="0.45"/>
    <line id="cap-height-guide" x1="{x:g}" x2="{x + width:g}" y1="{svg_y(metrics.cap_height):g}" y2="{svg_y(metrics.cap_height):g}" stroke="#3b82f6" opacity="0.45"/>
    <line id="x-height-guide" x1="{x:g}" x2="{x + width:g}" y1="{svg_y(metrics.x_height):g}" y2="{svg_y(metrics.x_height):g}" stroke="#10b981" opacity="0.45"/>
    <line id="baseline" data-fontmaker-baseline="true" x1="{x:g}" x2="{x + width:g}" y1="{svg.baseline_y:g}" y2="{svg.baseline_y:g}" stroke="#ef4444" stroke-width="2"/>
    <line id="descender-guide" x1="{x:g}" x2="{x + width:g}" y1="{svg_y(metrics.descender):g}" y2="{svg_y(metrics.descender):g}" stroke="#f59e0b" opacity="0.45"/>
  </g>
  <g id="glyph" fill="#000000"></g>
</svg>
'''

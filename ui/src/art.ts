export type ArtKey =
  | "construction"
  | "personalities"
  | "serif_style"
  | "weight"
  | "width"
  | "corners"
  | "contrast"
  | "regularity"
  | "slant"
  | "decoration";

export type IconName =
  | "arrow-left"
  | "arrow-right"
  | "brief"
  | "check"
  | "chevron-down"
  | "close"
  | "code"
  | "describe"
  | "edit"
  | "explore"
  | "guide"
  | "spinner"
  | "warning";

function svg(content: string, className = ""): string {
  return `<svg class="${className}" viewBox="0 0 160 96" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">${content}</svg>`;
}

const stroke = 'fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"';
const hairline = 'fill="none" stroke="currentColor" stroke-width="2" vector-effect="non-scaling-stroke"';

function construction(value: string): string {
  if (value === "pixel") {
    return svg(`
      <g ${hairline} opacity=".25"><path d="M24 18v64M48 18v64M72 18v64M96 18v64M120 18v64M144 18v64M16 32h132M16 56h132M16 80h132"/></g>
      <path fill="currentColor" d="M32 78V38h12V26h48v12h12v40H88V62H48v16zm16-28h40V38H48z"/>
      <rect x="112" y="66" width="16" height="12" fill="currentColor"/>
    `);
  }
  if (value === "textured") {
    return svg(`
      <path fill="currentColor" d="M28 78 32 31l9-5 7 3 9-4 7 4 9-3 10 3 8-2 10 6 2 45H88l-3-17-7 3-9-3-8 4-8-3-7 4-2 12zm19-30 4-9 13-3 14 4 5 8-7 5-13-2-9 4z"/>
      <path d="m111 29 6 8-4 7 8 7-7 8 6 10-8 8" ${stroke}/>
    `);
  }
  return svg(`
    <path d="M31 77V48c0-17 12-27 29-27 20 0 31 12 31 31v25M32 52h59M110 77V34c0-8 6-13 15-13 8 0 13 5 13 13v43" ${stroke}/>
    <circle cx="62" cy="52" r="9" fill="currentColor"/>
  `);
}

function personality(value: string): string {
  switch (value) {
    case "sci-fi":
      return svg(`
        <path fill="currentColor" d="M24 74V38l14-14h42l12 12v12H78V39l-5-5H45l-7 7v28l5 5h30l5-5v-7H61V50h38v23L86 84H39z"/>
        <path d="M111 30h25M111 48h16M111 66h25" ${hairline}/>
      `);
    case "classical":
      return svg(`
        <path fill="currentColor" d="M37 20h72v8l-22 4v45l22 4v8H37v-8l22-4V32l-22-4z"/>
        <path d="M27 89h92M32 18h82" ${hairline}/>
      `);
    case "fantasy":
      return svg(`
        <path d="M31 81 61 18l19 31 17-26 29 58M48 62h62M69 34l-2 47M97 39l5 42" ${stroke}/>
        <path fill="currentColor" d="m125 18 3 8 8 3-8 3-3 8-3-8-8-3 8-3z"/>
      `);
    case "friendly":
      return svg(`
        <path d="M28 57c0-21 14-34 35-34 23 0 37 15 37 36v19M29 58c0 13 9 22 23 22 16 0 27-11 27-25 0-10-7-17-18-17-10 0-17 6-17 15 0 8 6 14 15 14 8 0 14-5 14-12M118 31v47" ${stroke}/>
        <circle cx="118" cy="22" r="5" fill="currentColor"/>
      `);
    case "editorial":
      return svg(`
        <path d="M30 82V18h27c20 0 32 9 32 25 0 15-11 25-31 25H31M65 66l28 16" fill="none" stroke="currentColor" stroke-width="5"/>
        <path d="M43 18v64M28 18h33M28 82h34M91 79h31" fill="none" stroke="currentColor" stroke-width="2"/>
        <path d="M112 22v48" fill="none" stroke="currentColor" stroke-width="13"/>
      `);
    default:
      return svg(`
        <g fill="currentColor"><circle cx="38" cy="62" r="17"/><rect x="63" y="25" width="18" height="55" transform="rotate(-8 72 52)"/><path d="m102 72 11-51 23 57z"/></g>
        <path d="M21 84c23-7 43-6 61 0 20 7 39 6 59-1" ${hairline}/>
      `);
  }
}

function serifStyle(value: string): string {
  const serif = value === "serif";
  const slab = value === "slab";
  return svg(`
    <rect x="69" y="22" width="22" height="56" fill="currentColor"/>
    ${value === "sans" ? "" : `<rect x="${slab ? 46 : 55}" y="${slab ? 15 : 18}" width="${slab ? 68 : 50}" height="${slab ? 12 : 5}" fill="currentColor"/><rect x="${slab ? 46 : 55}" y="${slab ? 74 : 75}" width="${slab ? 68 : 50}" height="${slab ? 12 : 5}" fill="currentColor"/>`}
    ${serif ? `<path d="M55 23c11 0 14-2 18-8M105 23c-11 0-14-2-18-8M55 75c11 0 14 2 18 8M105 75c-11 0-14 2-18 8" ${hairline}/>` : ""}
  `);
}

function weight(value: string): string {
  const width = value === "light" ? 5 : value === "bold" ? 20 : 11;
  return svg(`
    <path d="M38 78V25M39 48c9-17 37-18 45 0v30M108 78V25M109 48c9-17 27-17 35 0v30" fill="none" stroke="currentColor" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>
  `);
}

function glyphWidth(value: string): string {
  const scale = value === "narrow" ? 0.62 : value === "wide" ? 1.28 : 0.92;
  const translate = 80 - 60 * scale;
  return svg(`
    <g transform="translate(${translate} 0) scale(${scale} 1)">
      <path d="M20 77V24M21 50c11-21 52-22 66 0v27M101 77V24" ${stroke}/>
    </g>
    <path d="M20 86h120M20 82v8M140 82v8" ${hairline} opacity=".45"/>
  `);
}

function corners(value: string): string {
  const path = value === "round"
    ? "M35 78V47c0-15 10-25 25-25h67"
    : value === "soft"
      ? "M35 78V48Q35 22 61 22h66"
      : "M35 78V22h92";
  return svg(`<path d="${path}" ${stroke}/><path d="M35 86v-8M127 14v8" ${hairline} opacity=".4"/>`);
}

function contrast(value: string): string {
  if (value === "dramatic") {
    return svg(`<path d="M80 18c31 0 49 13 49 31S111 80 80 80 31 67 31 49 49 18 80 18Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M47 25c-10 7-16 15-16 24s6 18 17 25M113 25c10 7 16 15 16 24s-6 18-17 25" fill="none" stroke="currentColor" stroke-width="17"/>`);
  }
  if (value === "moderate") {
    return svg(`<ellipse cx="80" cy="49" rx="49" ry="31" fill="none" stroke="currentColor" stroke-width="8"/><path d="M44 27c-9 6-13 13-13 22s5 18 14 23M116 27c9 6 13 13 13 22s-5 18-14 23" fill="none" stroke="currentColor" stroke-width="13"/>`);
  }
  return svg(`<ellipse cx="80" cy="49" rx="49" ry="31" fill="none" stroke="currentColor" stroke-width="10"/>`);
}

function regularity(value: string): string {
  const precise = `<path d="M30 78V30M67 78V30M104 78V30M141 78V30" ${stroke}/>`;
  const human = `<path d="M29 78V31M67 80V27M105 76V32M140 79V29" ${stroke}/>`;
  const expressive = `<path d="M28 80 35 27M64 77l-4-45M101 81l9-55M136 77l-8-42" ${stroke}/>`;
  return svg(value === "precise" ? precise : value === "human" ? human : expressive);
}

function slant(value: string): string {
  const skew = value === "upright" ? 0 : value === "slight" ? -8 : -18;
  return svg(`
    <g transform="skewX(${skew}) translate(${skew < 0 ? -skew * 2 : 0} 0)">
      <path d="M48 78V24M49 51c12-20 47-20 58 0v27M119 78V24" ${stroke}/>
    </g>
    <path d="M20 84h120" ${hairline} opacity=".4"/>
  `);
}

function decoration(value: string): string {
  if (value === "ornate") {
    return svg(`<path d="M69 77V23M48 23h43M44 77h49M91 23c33-14 45 9 29 20-12 8-24-2-16-11M93 77c30 13 46-9 29-20-12-8-25 3-16 12" ${stroke}/>`);
  }
  if (value === "distinctive") {
    return svg(`<path d="M69 77V23M48 23h54l-11 10M44 77h58l-11-10" ${stroke}/><circle cx="116" cy="50" r="8" fill="none" stroke="currentColor" stroke-width="4"/>`);
  }
  return svg(`<path d="M69 77V23M49 23h40M49 77h40" ${stroke}/>`);
}

export function optionArt(key: ArtKey, value: string): string {
  switch (key) {
    case "construction": return construction(value);
    case "personalities": return personality(value);
    case "serif_style": return serifStyle(value);
    case "weight": return weight(value);
    case "width": return glyphWidth(value);
    case "corners": return corners(value);
    case "contrast": return contrast(value);
    case "regularity": return regularity(value);
    case "slant": return slant(value);
    case "decoration": return decoration(value);
  }
}

export function routeArt(mode: "describe" | "explore" | "guided"): string {
  if (mode === "describe") {
    return svg(`<path d="M27 24h106v51H76L54 88V75H27z" ${stroke}/><path d="M45 42h70M45 57h48" ${hairline}/>`);
  }
  if (mode === "explore") {
    return svg(`<rect x="24" y="30" width="67" height="48" ${stroke}/><rect x="69" y="18" width="67" height="48" fill="var(--paper)" stroke="currentColor" stroke-width="6"/><path d="m112 70 4 9 10 4-10 4-4 9-4-9-10-4 10-4z" fill="currentColor"/>`);
  }
  return svg(`<path d="M33 23h94M33 49h94M33 75h94" ${hairline}/><circle cx="57" cy="23" r="10" fill="var(--paper)" stroke="currentColor" stroke-width="6"/><circle cx="104" cy="49" r="10" fill="var(--paper)" stroke="currentColor" stroke-width="6"/><circle cx="75" cy="75" r="10" fill="var(--paper)" stroke="currentColor" stroke-width="6"/>`);
}

const iconPaths: Record<IconName, string> = {
  "arrow-left": '<path d="m14 6-6 6 6 6M8 12h10"/>',
  "arrow-right": '<path d="m10 6 6 6-6 6M6 12h10"/>',
  brief: '<path d="M7 3h10v18H7zM10 7h4M10 11h4M10 15h4"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  "chevron-down": '<path d="m7 9 5 5 5-5"/>',
  close: '<path d="M6 6l12 12M18 6 6 18"/>',
  code: '<path d="m9 18-6-6 6-6M15 6l6 6-6 6"/>',
  describe: '<path d="M4 5h16v11H9l-4 4v-4H4zM8 9h8M8 12h5"/>',
  edit: '<path d="m4 20 4-1 11-11-3-3L5 16zM14 7l3 3"/>',
  explore: '<path d="M4 7h11v10H4zM10 4h10v10M18 16l1 2 2 1-2 1-1 2-1-2-2-1 2-1z"/>',
  guide: '<path d="M4 6h16M4 12h16M4 18h16M8 3v6M16 9v6M10 15v6"/>',
  spinner: '<path d="M12 3a9 9 0 1 1-9 9"/>',
  warning: '<path d="M12 3 2 21h20zM12 9v5M12 17h.01"/>',
};

export function icon(name: IconName): string {
  return `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${iconPaths[name]}</svg>`;
}

import { App } from "@modelcontextprotocol/ext-apps";

import { icon, optionArt, routeArt, type ArtKey } from "./art";
import "./styles.css";

type Mode = "describe" | "explore" | "guided";
type Phase = "landing" | Mode | "review" | "concepts" | "sent";
type SaveState = "idle" | "saving" | "saved" | "error";

type Brief = {
  mode: Mode | null;
  sample_text: string;
  purpose: string;
  languages: string[];
  description: string;
  construction: "smooth" | "pixel" | "textured" | null;
  personalities: string[];
  serif_style: "sans" | "serif" | "slab" | null;
  weight: "light" | "regular" | "bold" | null;
  width: "narrow" | "regular" | "wide" | null;
  corners: "sharp" | "soft" | "round" | null;
  contrast: "even" | "moderate" | "dramatic" | null;
  regularity: "precise" | "human" | "expressive" | null;
  slant: "upright" | "slight" | "italic" | null;
  decoration: "minimal" | "distinctive" | "ornate" | null;
  constraints: string;
};

type Concept = {
  concept_id: string;
  title: string;
  description: string;
  image_uri: string | null;
};

type Session = {
  session_id: string;
  status: "draft" | "ready";
  brief: Brief;
  concepts: Concept[];
  prompt: string;
  missing_fields: string[];
  completion: number;
};

type ToolResult = {
  isError?: boolean;
  structuredContent?: unknown;
};

type QuestionKey = Exclude<
  keyof Brief,
  | "mode"
  | "sample_text"
  | "purpose"
  | "languages"
  | "description"
  | "constraints"
>;

type Question = {
  key: QuestionKey;
  artKey: ArtKey;
  prompt: string;
  multiple?: boolean;
  options: readonly { value: string; label: string }[];
};

type Trait = { key: ArtKey; value: string; label: string };

const rootElement = document.querySelector<HTMLElement>("#app");
if (!rootElement) throw new Error("Font Maker root element is missing");
const root: HTMLElement = rootElement;
const standalonePreview = window.self === window.top;
const previewState = new URLSearchParams(window.location.search).get("preview");

const app = new App(
  { name: "Font Maker Designer", version: "0.1.0" },
  {},
  { autoResize: true },
);

let session: Session | null = null;
let phase: Phase = "landing";
let guidedStep = 0;
let guidedVisited = 0;
let exploreStep = 0;
let exploreVisited = 0;
let drawerOpen = false;
let saveState: SaveState = "idle";
let saveMessage = "";
let saveTimer: number | null = null;
let savedTimer: number | null = null;
let pollTimer: number | null = null;
let busy = false;

const guidedQuestions: readonly Question[] = [
  {
    key: "construction",
    artKey: "construction",
    prompt: "How are the edges made?",
    options: [
      { value: "smooth", label: "Smooth" },
      { value: "pixel", label: "Pixel" },
      { value: "textured", label: "Rough" },
    ],
  },
  {
    key: "personalities",
    artKey: "personalities",
    prompt: "What world does it belong to?",
    multiple: true,
    options: [
      { value: "sci-fi", label: "Sci-fi" },
      { value: "classical", label: "Classical" },
      { value: "fantasy", label: "Fantasy" },
      { value: "friendly", label: "Friendly" },
      { value: "editorial", label: "Editorial" },
      { value: "playful", label: "Playful" },
    ],
  },
  {
    key: "serif_style",
    artKey: "serif_style",
    prompt: "How should strokes end?",
    options: [
      { value: "sans", label: "Plain" },
      { value: "serif", label: "Fine serif" },
      { value: "slab", label: "Slab" },
    ],
  },
  {
    key: "weight",
    artKey: "weight",
    prompt: "How much ink should it carry?",
    options: [
      { value: "light", label: "Light" },
      { value: "regular", label: "Regular" },
      { value: "bold", label: "Bold" },
    ],
  },
  {
    key: "width",
    artKey: "width",
    prompt: "How much room should letters take?",
    options: [
      { value: "narrow", label: "Narrow" },
      { value: "regular", label: "Regular" },
      { value: "wide", label: "Wide" },
    ],
  },
  {
    key: "corners",
    artKey: "corners",
    prompt: "How should corners turn?",
    options: [
      { value: "sharp", label: "Sharp" },
      { value: "soft", label: "Soft" },
      { value: "round", label: "Round" },
    ],
  },
  {
    key: "contrast",
    artKey: "contrast",
    prompt: "How should thick and thin relate?",
    options: [
      { value: "even", label: "Even" },
      { value: "moderate", label: "Moderate" },
      { value: "dramatic", label: "Dramatic" },
    ],
  },
  {
    key: "regularity",
    artKey: "regularity",
    prompt: "How regular should it feel?",
    options: [
      { value: "precise", label: "Precise" },
      { value: "human", label: "Human" },
      { value: "expressive", label: "Expressive" },
    ],
  },
  {
    key: "slant",
    artKey: "slant",
    prompt: "How should it stand?",
    options: [
      { value: "upright", label: "Upright" },
      { value: "slight", label: "Inclined" },
      { value: "italic", label: "Italic" },
    ],
  },
  {
    key: "decoration",
    artKey: "decoration",
    prompt: "How much detail?",
    options: [
      { value: "minimal", label: "Minimal" },
      { value: "distinctive", label: "Distinctive" },
      { value: "ornate", label: "Ornate" },
    ],
  },
] as const;

const exploreQuestions = [guidedQuestions[1], guidedQuestions[0]] as const;

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function sessionFromResult(result: ToolResult): Session | null {
  if (!result.structuredContent || typeof result.structuredContent !== "object") return null;
  const content = result.structuredContent as Record<string, unknown>;
  if (typeof content.session_id === "string") return content as unknown as Session;
  return null;
}

function questionValue(brief: Brief, question: Question): string | string[] | null {
  return brief[question.key] as string | string[] | null;
}

function isQuestionAnswered(brief: Brief, question: Question): boolean {
  const value = questionValue(brief, question);
  return Array.isArray(value) ? value.length > 0 : Boolean(value);
}

function selectedTraits(brief: Brief): Trait[] {
  const traits: Trait[] = [];
  for (const question of guidedQuestions) {
    const value = questionValue(brief, question);
    const selected = Array.isArray(value) ? value : value ? [value] : [];
    for (const item of selected) {
      const option = question.options.find((candidate) => candidate.value === item);
      if (option) traits.push({ key: question.artKey, value: option.value, label: option.label });
    }
  }
  return traits;
}

function sampleClass(brief: Brief): string {
  const classes = ["specimen-input"];
  if (brief.construction) classes.push(`is-${brief.construction}`);
  if (brief.serif_style) classes.push(`is-${brief.serif_style}`);
  if (brief.weight) classes.push(`is-${brief.weight}`);
  if (brief.width) classes.push(`is-${brief.width}`);
  if (brief.slant) classes.push(`is-${brief.slant}`);
  return classes.join(" ");
}

function progressMarkup(current: number, visited: number, total: number, scope: "guided" | "explore"): string {
  return `<nav class="progress-dots" aria-label="${scope === "guided" ? "Guided questions" : "Explore questions"}">
    ${Array.from({ length: total }, (_, index) => {
      const state = index === current ? "is-current" : index <= visited ? "is-visited" : "";
      if (index <= visited) {
        return `<button class="progress-dot ${state}" data-progress="${index}" aria-label="Go to question ${index + 1}" ${index === current ? 'aria-current="step"' : ""}></button>`;
      }
      return `<span class="progress-dot ${state}" aria-hidden="true"></span>`;
    }).join("")}
  </nav>`;
}

function saveStatusMarkup(): string {
  if (saveState === "idle") return '<span id="save-status" class="save-status" aria-live="polite"></span>';
  const visual = saveState === "saving" ? icon("spinner") : saveState === "saved" ? icon("check") : icon("warning");
  return `<span id="save-status" class="save-status is-${saveState}" aria-live="polite">${visual}<span class="visually-hidden">${escapeHtml(saveMessage)}</span></span>`;
}

function headerMarkup(brief: Brief): string {
  const progress = phase === "guided"
    ? progressMarkup(guidedStep, guidedVisited, guidedQuestions.length, "guided")
    : phase === "explore"
      ? progressMarkup(exploreStep, exploreVisited, exploreQuestions.length, "explore")
      : "";
  const count = selectedTraits(brief).length;
  const back = phase === "landing"
    ? '<span class="header-spacer" aria-hidden="true"></span>'
    : `<button class="icon-button" data-action="exit" aria-label="Back" data-tooltip="Back">${icon("arrow-left")}</button>`;

  return `<header class="app-header">
    <div class="header-start">${back}<button class="wordmark" data-action="home">Font Maker</button></div>
    ${progress || '<span class="header-center" aria-hidden="true"></span>'}
    <div class="header-end">
      ${saveStatusMarkup()}
      <button id="brief-toggle" class="icon-button brief-button" data-action="drawer" aria-label="Open brief" data-tooltip="Brief" aria-expanded="${drawerOpen}">
        ${icon("brief")}${count ? `<span class="brief-count">${count}</span>` : ""}
      </button>
    </div>
  </header>`;
}

function drawerMarkup(brief: Brief): string {
  if (!drawerOpen) return "";
  const traits = selectedTraits(brief);
  return `<div class="drawer-layer" data-action="close-drawer">
    <aside id="brief-drawer" class="brief-drawer" role="dialog" aria-modal="true" aria-labelledby="brief-title">
      <header class="drawer-header">
        <h2 id="brief-title">Brief</h2>
        <button class="icon-button" data-action="close-drawer" aria-label="Close brief" data-tooltip="Close">${icon("close")}</button>
      </header>
      <div class="drawer-body">
        ${traits.length ? `<div class="trait-grid drawer-traits">${traits.map(traitMarkup).join("")}</div>` : '<p class="empty-state">No choices yet.</p>'}
        ${brief.description ? `<section class="brief-note"><h3>Direction</h3><p>${escapeHtml(brief.description)}</p></section>` : ""}
        ${brief.purpose ? `<section class="brief-note"><h3>For</h3><p>${escapeHtml(brief.purpose)}</p></section>` : ""}
      </div>
    </aside>
  </div>`;
}

function shell(content: string, brief: Brief): string {
  return `<div class="workbench">
    ${headerMarkup(brief)}
    <main class="main-flow">${content}</main>
  </div>${drawerMarkup(brief)}`;
}

function specimenMarkup(brief: Brief): string {
  return `<div class="specimen-board">
    <input id="sample-text" class="${sampleClass(brief)}" value="${escapeHtml(brief.sample_text)}" maxlength="72" aria-label="Sample text" spellcheck="false" />
    <button class="icon-button specimen-edit" data-action="edit-sample" aria-label="Edit sample text" data-tooltip="Edit sample">${icon("edit")}</button>
  </div>`;
}

function traitMarkup(trait: Trait): string {
  return `<div class="trait" aria-label="${escapeHtml(trait.label)}">
    <span class="trait-art">${optionArt(trait.key, trait.value)}</span>
    <strong>${escapeHtml(trait.label)}</strong>
  </div>`;
}

function choiceMarkup(question: Question, brief: Brief): string {
  const value = questionValue(brief, question);
  const selected = Array.isArray(value) ? value : value ? [value] : [];
  return `<div class="choice-grid ${question.options.length > 3 ? "is-dense" : ""}">
    ${question.options.map((option) => {
      const isSelected = selected.includes(option.value);
      return `<button class="choice ${isSelected ? "is-selected" : ""}" data-key="${question.key}" data-value="${option.value}" aria-pressed="${isSelected}" aria-label="${escapeHtml(option.label)}">
        <span class="choice-art">${optionArt(question.artKey, option.value)}</span>
        <strong>${escapeHtml(option.label)}</strong>
        ${isSelected ? `<span class="choice-check" aria-hidden="true">${icon("check")}</span>` : ""}
      </button>`;
    }).join("")}
  </div>`;
}

function navMarkup(canGoBack: boolean, canGoNext: boolean, nextLabel = "Next"): string {
  return `<div class="nav-row">
    <button class="nav-button" data-action="previous" aria-label="Previous question" data-tooltip="Previous" ${canGoBack ? "" : "disabled"}>${icon("arrow-left")}</button>
    <button class="nav-button is-forward" data-action="next" aria-label="${escapeHtml(nextLabel)}" data-tooltip="${escapeHtml(nextLabel)}" ${canGoNext ? "" : "disabled"}>${icon("arrow-right")}</button>
  </div>`;
}

function renderLanding(): void {
  if (!session) return;
  const content = `<section class="landing-screen" aria-labelledby="landing-title">
    <h1 id="landing-title" class="screen-title" tabindex="-1">How do you want to start?</h1>
    ${specimenMarkup(session.brief)}
    <div class="route-grid">
      ${(["describe", "explore", "guided"] as const).map((mode) => {
        const label = mode === "describe" ? "Describe" : mode === "explore" ? "Explore" : "Guide me";
        return `<button class="route" data-mode="${mode}"><span class="route-art">${routeArt(mode)}</span><strong>${label}</strong><span class="route-arrow" aria-hidden="true">${icon("arrow-right")}</span></button>`;
      }).join("")}
    </div>
  </section>`;
  root.innerHTML = shell(content, session.brief);
  bindShared();
  root.querySelectorAll<HTMLButtonElement>("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.dataset.mode as Mode;
      session!.brief.mode = mode;
      phase = mode;
      guidedStep = 0;
      guidedVisited = 0;
      exploreStep = 0;
      exploreVisited = 0;
      queueSave();
      renderAndFocus();
    });
  });
}

function renderDescribe(): void {
  if (!session) return;
  const brief = session.brief;
  const content = `<section class="describe-screen" aria-labelledby="describe-title">
    <h1 id="describe-title" class="screen-title" tabindex="-1">Describe the font.</h1>
    ${specimenMarkup(brief)}
    <div class="writing-fields">
      <label class="visually-hidden" for="description">Font description</label>
      <textarea id="description" rows="5" placeholder="Wide, awkward sci-fi letters printed on old laboratory equipment…">${escapeHtml(brief.description)}</textarea>
      <label class="visually-hidden" for="purpose">What the font is for</label>
      <input class="text-field" id="purpose" value="${escapeHtml(brief.purpose)}" placeholder="A game title, café sign, book cover…" />
    </div>
    <div class="primary-row"><button class="primary-action" data-action="review">Review ${icon("arrow-right")}</button></div>
  </section>`;
  root.innerHTML = shell(content, brief);
  bindShared();
  bindText("description", "description");
  bindText("purpose", "purpose");
  root.querySelector<HTMLButtonElement>("[data-action='review']")?.addEventListener("click", () => {
    phase = "review";
    void saveNow().then(renderAndFocus);
  });
}

function renderExplore(): void {
  if (!session) return;
  const brief = session.brief;
  const question = exploreQuestions[exploreStep];
  const content = `<section class="question-screen" aria-labelledby="question-title">
    <h1 id="question-title" class="screen-title" tabindex="-1">${escapeHtml(question.prompt)}</h1>
    ${specimenMarkup(brief)}
    ${choiceMarkup(question, brief)}
    ${navMarkup(exploreStep > 0, isQuestionAnswered(brief, question), exploreStep === exploreQuestions.length - 1 ? "Make directions" : "Next")}
  </section>`;
  root.innerHTML = shell(content, brief);
  bindShared();
  bindChoices(question);
  bindProgress("explore");
  root.querySelector<HTMLButtonElement>("[data-action='previous']")?.addEventListener("click", () => {
    if (exploreStep > 0) exploreStep -= 1;
    renderAndFocus();
  });
  root.querySelector<HTMLButtonElement>("[data-action='next']")?.addEventListener("click", () => {
    if (!isQuestionAnswered(brief, question)) return;
    if (exploreStep < exploreQuestions.length - 1) {
      exploreStep += 1;
      exploreVisited = Math.max(exploreVisited, exploreStep);
      renderAndFocus();
      return;
    }
    void requestDirections();
  });
}

function renderGuided(): void {
  if (!session) return;
  const brief = session.brief;
  const question = guidedQuestions[guidedStep];
  const content = `<section class="question-screen" aria-labelledby="question-title">
    <h1 id="question-title" class="screen-title" tabindex="-1">${escapeHtml(question.prompt)}</h1>
    ${specimenMarkup(brief)}
    ${choiceMarkup(question, brief)}
    ${navMarkup(guidedStep > 0, isQuestionAnswered(brief, question), guidedStep === guidedQuestions.length - 1 ? "Review" : "Next")}
  </section>`;
  root.innerHTML = shell(content, brief);
  bindShared();
  bindChoices(question);
  bindProgress("guided");
  root.querySelector<HTMLButtonElement>("[data-action='previous']")?.addEventListener("click", () => {
    if (guidedStep > 0) guidedStep -= 1;
    renderAndFocus();
  });
  root.querySelector<HTMLButtonElement>("[data-action='next']")?.addEventListener("click", () => {
    if (!isQuestionAnswered(brief, question)) return;
    if (guidedStep < guidedQuestions.length - 1) {
      guidedStep += 1;
      guidedVisited = Math.max(guidedVisited, guidedStep);
      renderAndFocus();
      return;
    }
    phase = "review";
    void saveNow().then(renderAndFocus);
  });
}

function renderReview(): void {
  if (!session) return;
  const brief = session.brief;
  const traits = selectedTraits(brief);
  const missing = session.missing_fields.length > 0;
  const content = `<section class="review-screen" aria-labelledby="review-title">
    <h1 id="review-title" class="screen-title" tabindex="-1">Ready?</h1>
    ${specimenMarkup(brief)}
    ${traits.length ? `<div class="trait-grid review-traits">${traits.map(traitMarkup).join("")}</div>` : ""}
    ${missing ? `<div class="warning-block">${icon("warning")}<p>${escapeHtml(session.missing_fields.join(", "))}</p></div>` : ""}
    <details class="agent-prompt">
      <summary>${icon("code")}<span>Agent prompt</span>${icon("chevron-down")}</summary>
      <pre>${escapeHtml(session.prompt)}</pre>
    </details>
    <div class="review-actions">
      <button class="secondary-action" data-action="directions">Explore directions</button>
      <button class="primary-action" data-action="send" ${busy || missing ? "disabled" : ""}>Make this font ${icon("arrow-right")}</button>
    </div>
  </section>`;
  root.innerHTML = shell(content, brief);
  bindShared();
  root.querySelector<HTMLButtonElement>("[data-action='directions']")?.addEventListener("click", () => void requestDirections());
  root.querySelector<HTMLButtonElement>("[data-action='send']")?.addEventListener("click", () => void sendBrief());
}

function renderConcepts(): void {
  if (!session) return;
  const concepts = session.concepts;
  const content = concepts.length
    ? `<section class="concept-screen" aria-labelledby="concept-title">
        <h1 id="concept-title" class="screen-title" tabindex="-1">Choose a direction.</h1>
        <div class="concept-grid">
          ${concepts.map((concept) => `<button class="concept-card" data-concept="${concept.concept_id}" aria-label="Choose ${escapeHtml(concept.title)}">
            ${concept.image_uri ? `<img src="${escapeHtml(concept.image_uri)}" alt="" />` : `<span class="concept-fallback">${escapeHtml((concept.title || "Aa").slice(0, 2))}</span>`}
            <strong>${escapeHtml(concept.title)}</strong>
          </button>`).join("")}
        </div>
        <div class="primary-row"><button class="primary-action" data-action="review">Review ${icon("arrow-right")}</button></div>
      </section>`
    : `<section class="waiting-screen" aria-labelledby="waiting-title"><span class="making-mark" aria-hidden="true">${icon("spinner")}</span><h1 id="waiting-title" tabindex="-1">Making directions…</h1></section>`;
  root.innerHTML = shell(content, session.brief);
  bindShared();
  root.querySelectorAll<HTMLButtonElement>("[data-concept]").forEach((button) => {
    button.addEventListener("click", () => {
      root.querySelectorAll(".concept-card").forEach((card) => card.classList.remove("is-selected"));
      button.classList.add("is-selected");
    });
  });
  root.querySelector<HTMLButtonElement>("[data-action='review']")?.addEventListener("click", () => {
    phase = "review";
    renderAndFocus();
  });
}

function renderSent(): void {
  if (!session) return;
  root.innerHTML = shell(`<section class="sent-screen" aria-labelledby="sent-title"><span aria-hidden="true">${icon("check")}</span><h1 id="sent-title" tabindex="-1">Sent.</h1></section>`, session.brief);
  bindShared();
}

function render(): void {
  if (!session) return;
  if (phase === "landing") renderLanding();
  else if (phase === "describe") renderDescribe();
  else if (phase === "explore") renderExplore();
  else if (phase === "guided") renderGuided();
  else if (phase === "review") renderReview();
  else if (phase === "concepts") renderConcepts();
  else renderSent();
}

function renderAndFocus(): void {
  render();
  window.scrollTo(0, 0);
  window.requestAnimationFrame(() => root.querySelector<HTMLElement>("main h1")?.focus({ preventScroll: true }));
}

function bindShared(): void {
  root.querySelectorAll<HTMLElement>("[data-action='home']").forEach((element) => {
    element.addEventListener("click", () => {
      phase = "landing";
      drawerOpen = false;
      renderAndFocus();
    });
  });
  root.querySelector<HTMLButtonElement>("[data-action='exit']")?.addEventListener("click", handleExit);
  root.querySelector<HTMLButtonElement>("[data-action='drawer']")?.addEventListener("click", openDrawer);
  root.querySelectorAll<HTMLElement>("[data-action='close-drawer']").forEach((element) => {
    element.addEventListener("click", (event) => {
      if (event.currentTarget === event.target || (event.currentTarget as HTMLElement).closest("button")) closeDrawer();
    });
  });
  const drawer = root.querySelector<HTMLElement>("#brief-drawer");
  drawer?.addEventListener("keydown", trapDrawerFocus);

  const sample = root.querySelector<HTMLInputElement>("#sample-text");
  sample?.addEventListener("input", () => {
    if (!session) return;
    session.brief.sample_text = sample.value;
    queueSave();
  });
  root.querySelector<HTMLButtonElement>("[data-action='edit-sample']")?.addEventListener("click", () => {
    sample?.focus();
    sample?.select();
  });
}

function handleExit(): void {
  if (phase === "concepts") phase = "review";
  else if (phase === "review") {
    if (session?.brief.mode === "guided") {
      phase = "guided";
      guidedStep = Math.max(0, Math.min(guidedVisited, guidedQuestions.length - 1));
    } else if (session?.brief.mode === "explore") {
      phase = "explore";
      exploreStep = Math.max(0, Math.min(exploreVisited, exploreQuestions.length - 1));
    } else phase = "describe";
  } else phase = "landing";
  renderAndFocus();
}

function openDrawer(): void {
  drawerOpen = true;
  render();
  window.requestAnimationFrame(() => root.querySelector<HTMLButtonElement>("button[data-action='close-drawer']")?.focus());
}

function closeDrawer(): void {
  drawerOpen = false;
  render();
  root.querySelector<HTMLButtonElement>("#brief-toggle")?.focus();
}

function trapDrawerFocus(event: KeyboardEvent): void {
  if (event.key === "Escape") {
    event.preventDefault();
    closeDrawer();
    return;
  }
  if (event.key !== "Tab") return;
  const drawer = root.querySelector<HTMLElement>("#brief-drawer");
  const focusable = Array.from(drawer?.querySelectorAll<HTMLElement>('button, [href], input, textarea, select, details > summary, [tabindex]:not([tabindex="-1"])') ?? []).filter((element) => !element.hasAttribute("disabled"));
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function bindProgress(scope: "guided" | "explore"): void {
  root.querySelectorAll<HTMLButtonElement>("[data-progress]").forEach((button) => {
    button.addEventListener("click", () => {
      const index = Number(button.dataset.progress);
      if (scope === "guided") guidedStep = index;
      else exploreStep = index;
      renderAndFocus();
    });
  });
}

function bindChoices(question: Question): void {
  root.querySelectorAll<HTMLButtonElement>(".choice").forEach((button) => {
    button.addEventListener("click", () => {
      if (!session) return;
      const selectedValue = button.dataset.value ?? "";
      if (question.multiple) {
        const current = [...session.brief.personalities];
        const index = current.indexOf(selectedValue);
        if (index >= 0) current.splice(index, 1);
        else {
          if (current.length === 2) current.shift();
          current.push(selectedValue);
        }
        session.brief.personalities = current;
      } else {
        (session.brief as unknown as Record<string, unknown>)[question.key] = selectedValue;
      }
      queueSave();
      render();
      window.requestAnimationFrame(() => root.querySelector<HTMLButtonElement>(`.choice[data-value="${CSS.escape(selectedValue)}"]`)?.focus());
    });
  });
}

function bindText(id: string, key: "description" | "purpose"): void {
  const input = root.querySelector<HTMLInputElement | HTMLTextAreaElement>(`#${id}`);
  input?.addEventListener("input", () => {
    if (!session) return;
    session.brief[key] = input.value;
    queueSave();
  });
}

function queueSave(): void {
  saveState = "saving";
  saveMessage = "Saving";
  updateSaveStatus();
  if (saveTimer !== null) window.clearTimeout(saveTimer);
  saveTimer = window.setTimeout(() => void saveNow(), 400);
}

function updateSaveStatus(): void {
  const current = root.querySelector<HTMLElement>("#save-status");
  if (!current) return;
  const wrapper = document.createElement("div");
  wrapper.innerHTML = saveStatusMarkup();
  current.replaceWith(wrapper.firstElementChild as HTMLElement);
}

async function saveNow(): Promise<void> {
  if (!session || standalonePreview) {
    saveState = "saved";
    saveMessage = "Saved";
    updateSaveStatus();
    scheduleSaveClear();
    return;
  }
  if (saveTimer !== null) window.clearTimeout(saveTimer);
  saveTimer = null;
  saveState = "saving";
  saveMessage = "Saving";
  updateSaveStatus();
  try {
    const result = (await app.callServerTool({
      name: "update_font_brief",
      arguments: { session_id: session.session_id, patch: session.brief },
    })) as ToolResult;
    if (result.isError) throw new Error("Save failed");
    const updated = sessionFromResult(result);
    if (updated) session = updated;
    saveState = "saved";
    saveMessage = "Saved";
    scheduleSaveClear();
  } catch {
    saveState = "error";
    saveMessage = "Save failed";
  }
  updateSaveStatus();
}

function scheduleSaveClear(): void {
  if (savedTimer !== null) window.clearTimeout(savedTimer);
  savedTimer = window.setTimeout(() => {
    saveState = "idle";
    saveMessage = "";
    updateSaveStatus();
  }, 1500);
}

async function requestDirections(): Promise<void> {
  if (!session || busy) return;
  busy = true;
  await saveNow();
  phase = "concepts";
  renderAndFocus();
  if (standalonePreview) {
    busy = false;
    return;
  }
  try {
    const result = (await app.callServerTool({
      name: "finalize_font_brief",
      arguments: { session_id: session.session_id },
    })) as ToolResult;
    if (result.isError) throw new Error("Finalize failed");
    const updated = sessionFromResult(result);
    if (updated) session = updated;
    const message = await app.sendMessage({
      role: "user",
      content: [
        {
          type: "text",
          text: `${session.prompt}\n\nGenerate the three concept specimens now, then call submit_font_concepts with their image URIs for session ${session.session_id}.`,
        },
      ],
    });
    if (message.isError) throw new Error("Message rejected");
    startPolling();
  } catch {
    saveState = "error";
    saveMessage = "Could not make directions";
    busy = false;
    phase = "review";
    renderAndFocus();
  }
}

function startPolling(): void {
  if (pollTimer !== null) window.clearInterval(pollTimer);
  pollTimer = window.setInterval(() => void refreshSession(), 1500);
  void refreshSession();
}

async function refreshSession(): Promise<void> {
  if (!session || standalonePreview) return;
  try {
    const result = (await app.callServerTool({
      name: "read_font_design",
      arguments: { session_id: session.session_id },
    })) as ToolResult;
    const updated = sessionFromResult(result);
    if (updated) session = updated;
    if (session.concepts.length > 0) {
      if (pollTimer !== null) window.clearInterval(pollTimer);
      pollTimer = null;
      busy = false;
    }
    render();
  } catch {
    if (pollTimer !== null) window.clearInterval(pollTimer);
    pollTimer = null;
    busy = false;
    saveState = "error";
    saveMessage = "Could not load directions";
    phase = "review";
    renderAndFocus();
  }
}

async function sendBrief(): Promise<void> {
  if (!session || busy) return;
  busy = true;
  await saveNow();
  if (standalonePreview) {
    busy = false;
    phase = "sent";
    renderAndFocus();
    return;
  }
  try {
    const result = (await app.callServerTool({
      name: "finalize_font_brief",
      arguments: { session_id: session.session_id },
    })) as ToolResult;
    if (result.isError) throw new Error("Send failed");
    const updated = sessionFromResult(result);
    if (updated) session = updated;
    const message = await app.sendMessage({
      role: "user",
      content: [
        {
          type: "text",
          text: `${session.prompt}\n\nUse this finalized brief to start the font project.`,
        },
      ],
    });
    if (message.isError) throw new Error("Message rejected");
    busy = false;
    phase = "sent";
    renderAndFocus();
  } catch {
    busy = false;
    saveState = "error";
    saveMessage = "Send failed";
    render();
  }
}

function defaultSession(): Session {
  return {
    session_id: "standalone-preview",
    status: "draft",
    brief: {
      mode: null,
      sample_text: "Signal in the static",
      purpose: "",
      languages: ["Latin"],
      description: "",
      construction: null,
      personalities: [],
      serif_style: null,
      weight: null,
      width: null,
      corners: null,
      contrast: null,
      regularity: null,
      slant: null,
      decoration: null,
      constraints: "",
    },
    concepts: [],
    prompt: "Use this visual brief to design a complete, usable typeface direction.",
    missing_fields: [],
    completion: 0,
  };
}

app.ontoolresult = (result) => {
  const incoming = sessionFromResult(result as ToolResult);
  if (incoming) session = incoming;
  render();
};

if (standalonePreview) {
  session = defaultSession();
  if (previewState === "concepts") {
    session.concepts = [
      { concept_id: "signal-cut", title: "Signal Cut", description: "", image_uri: null },
      { concept_id: "soft-machine", title: "Soft Machine", description: "", image_uri: null },
      { concept_id: "archive-mono", title: "Archive Mono", description: "", image_uri: null },
    ];
    phase = "concepts";
  } else if (previewState === "review") {
    phase = "review";
  } else if (previewState === "save-error") {
    phase = "guided";
    saveState = "error";
    saveMessage = "Save failed";
  }
  render();
} else {
  void app.connect().then(() => {
    if (!session) session = defaultSession();
    render();
  });
}

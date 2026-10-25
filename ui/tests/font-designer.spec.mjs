import { expect, test } from "@playwright/test";

const questions = [
  ["How are the edges made?", "Smooth"],
  ["What world does it belong to?", "Sci-fi"],
  ["How should strokes end?", "Plain"],
  ["How much ink should it carry?", "Light"],
  ["How much room should letters take?", "Narrow"],
  ["How should corners turn?", "Sharp"],
  ["How should thick and thin relate?", "Even"],
  ["How regular should it feel?", "Precise"],
  ["How should it stand?", "Upright"],
  ["How much detail?", "Minimal"],
];

test.beforeEach(async ({ page }) => {
  await page.goto("/font-designer.html");
});

test("landing is visual-first and all three entry routes work", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "How do you want to start?" })).toBeVisible();
  for (const route of ["Describe", "Explore", "Guide me"]) {
    const button = page.getByRole("button", { name: route });
    await expect(button).toBeVisible();
    await expect(button.locator("svg")).toHaveCount(2);
  }
  await expect(page.getByText(/Guided interview|Your test|Live direction|Question 1 of/i)).toHaveCount(0);

  await page.getByRole("button", { name: "Describe" }).click();
  await expect(page.getByRole("heading", { name: "Describe the font." })).toBeVisible();
  await page.getByRole("button", { name: "Font Maker" }).click();
  await page.getByRole("button", { name: "Explore" }).click();
  await expect(page.getByRole("heading", { name: "What world does it belong to?" })).toBeVisible();
});

test("guided route completes all ten illustrated questions", async ({ page }) => {
  await page.getByRole("button", { name: "Guide me" }).click();

  for (let index = 0; index < questions.length; index += 1) {
    const [heading, choice] = questions[index];
    await expect(page.getByRole("heading", { name: heading })).toBeVisible();
    const choices = page.locator(".choice");
    await expect(choices).toHaveCount(index === 1 ? 6 : 3);
    await expect(choices.first().locator("svg")).toHaveCount(1);
    const next = page.getByRole("button", { name: index === questions.length - 1 ? "Review" : "Next" });
    await expect(next).toBeDisabled();
    await page.getByRole("button", { name: choice, exact: true }).click();
    await expect(page.getByRole("button", { name: choice, exact: true })).toHaveAttribute("aria-pressed", "true");
    await expect(next).toBeEnabled();
    await next.click();
  }

  await expect(page.getByRole("heading", { name: "Ready?" })).toBeVisible();
  await expect(page.getByText("Agent prompt")).toBeVisible();
  await expect(page.locator("details.agent-prompt")).not.toHaveAttribute("open", "");
  await expect(page.locator(".review-traits .trait")).toHaveCount(10);
});

test("sample editing, drawer escape, and focus restoration work", async ({ page }) => {
  await page.getByRole("button", { name: "Guide me" }).click();
  await page.getByRole("textbox", { name: "Sample text" }).fill("A very long specimen line with 0123456789 and punctuation!? — still contained");
  await page.getByRole("button", { name: "Pixel", exact: true }).click();
  await page.getByRole("button", { name: "Open brief" }).click();
  await expect(page.getByRole("dialog", { name: "Brief" })).toBeVisible();
  await expect(page.getByRole("dialog").getByText("Pixel")).toBeVisible();
  await expect(page.getByRole("button", { name: "Close brief" })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Open brief" })).toBeFocused();
});

test("describe review keeps the prompt collapsed and can send", async ({ page }) => {
  await page.getByRole("button", { name: "Describe" }).click();
  await page.getByRole("textbox", { name: "Font description" }).fill("A quiet high-contrast book face");
  await page.getByRole("textbox", { name: "What the font is for" }).fill("A novel cover");
  await page.getByRole("button", { name: "Review" }).click();
  const details = page.locator("details.agent-prompt");
  await expect(details).not.toHaveAttribute("open", "");
  await details.locator("summary").click();
  await expect(details).toHaveAttribute("open", "");
  await page.getByRole("button", { name: "Make this font" }).click();
  await expect(page.getByRole("heading", { name: "Sent." })).toBeVisible();
});

test("explore produces the reduced waiting state", async ({ page }) => {
  await page.getByRole("button", { name: "Explore" }).click();
  await page.getByRole("button", { name: "Editorial", exact: true }).click();
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("button", { name: "Smooth", exact: true }).click();
  await page.getByRole("button", { name: "Make directions" }).click();
  await expect(page.getByRole("heading", { name: "Making directions…" })).toBeVisible();
  await expect(page.locator(".waiting-screen p")).toHaveCount(0);
});

test("concept results remain usable when generated artwork is absent", async ({ page }) => {
  await page.goto("/font-designer.html?preview=concepts");
  await expect(page.getByRole("heading", { name: "Choose a direction." })).toBeVisible();
  await expect(page.locator(".concept-card")).toHaveCount(3);
  await expect(page.locator(".concept-fallback")).toHaveCount(3);
  const concept = page.getByRole("button", { name: "Choose Soft Machine" });
  await concept.click();
  await expect(concept).toHaveClass(/is-selected/);
});

test("empty review and save failure have explicit non-color states", async ({ page }) => {
  await page.goto("/font-designer.html?preview=review");
  await expect(page.getByRole("heading", { name: "Ready?" })).toBeVisible();
  await expect(page.locator(".review-traits")).toHaveCount(0);

  await page.goto("/font-designer.html?preview=save-error");
  const error = page.locator("#save-status");
  await expect(error).toContainText("Save failed");
  await expect(error.locator("svg")).toHaveCount(1);
  await expect(error).toHaveCSS("border-top-style", "solid");
});

test("keyboard activation, visited progress, and mobile containment", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.getByRole("button", { name: "Guide me" }).focus();
  await page.keyboard.press("Enter");
  const smooth = page.getByRole("button", { name: "Smooth", exact: true });
  await smooth.focus();
  await page.keyboard.press(" ");
  await expect(smooth).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("button", { name: "Go to question 1" }).click();
  await expect(page.getByRole("heading", { name: questions[0][0] })).toBeVisible();
  const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth }));
  expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.client);
  await expect(page.locator(".choice").first()).toBeVisible();
});

test("target viewport matrix has no horizontal page overflow", async ({ page }) => {
  const sizes = [
    { width: 1440, height: 900 },
    { width: 768, height: 1024 },
    { width: 375, height: 812 },
    { width: 320, height: 568 },
    { width: 720, height: 450 }, // 1440×900 at an effective 200% layout zoom
  ];

  for (const size of sizes) {
    await page.setViewportSize(size);
    await page.goto("/font-designer.html");
    await page.getByRole("button", { name: "Guide me" }).click();
    await expect(page.getByRole("heading", { name: questions[0][0] })).toBeVisible();
    await expect(page.getByRole("textbox", { name: "Sample text" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Smooth", exact: true })).toBeVisible();
    const dimensions = await page.evaluate(() => ({
      scroll: document.documentElement.scrollWidth,
      client: document.documentElement.clientWidth,
    }));
    expect(dimensions.scroll, `${size.width}×${size.height}`).toBeLessThanOrEqual(dimensions.client);
  }
});

test("selection is communicated by inversion and a check, with reduced motion honored", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.getByRole("button", { name: "Guide me" }).click();
  const pixel = page.getByRole("button", { name: "Pixel", exact: true });
  await pixel.click();
  await expect(pixel.locator(".choice-check svg")).toHaveCount(1);
  await expect(pixel).toHaveCSS("color", "rgb(255, 255, 255)");
  const motion = await page.locator(".choice").first().evaluate((element) => getComputedStyle(element).transitionDuration);
  expect(Number.parseFloat(motion)).toBeLessThanOrEqual(0.00001);
});

test("1280×720 keeps the full decision sequence identifiable", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.getByRole("button", { name: "Guide me" }).click();
  await page.getByRole("button", { name: "Smooth", exact: true }).click();
  for (const locator of [
    page.getByRole("heading", { name: questions[0][0] }),
    page.getByRole("textbox", { name: "Sample text" }),
    page.getByRole("button", { name: "Rough", exact: true }),
    page.getByRole("button", { name: "Next" }),
  ]) {
    await expect(locator).toBeInViewport();
  }
});

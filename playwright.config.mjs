import { existsSync } from "node:fs";
import { defineConfig } from "@playwright/test";

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

export default defineConfig({
  testDir: "./ui/tests",
  timeout: 20_000,
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:5173",
    browserName: "chromium",
    headless: true,
    launchOptions: existsSync(chromePath) ? { executablePath: chromePath } : {},
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run dev",
    url: "http://127.0.0.1:5173/font-designer.html",
    reuseExistingServer: true,
  },
});

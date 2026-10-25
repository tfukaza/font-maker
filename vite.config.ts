import { resolve } from "node:path";

import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  root: resolve(import.meta.dirname, "ui"),
  plugins: [viteSingleFile()],
  build: {
    outDir: resolve(import.meta.dirname, "src/font_maker/ui"),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(import.meta.dirname, "ui/font-designer.html"),
    },
  },
});

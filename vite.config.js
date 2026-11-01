import { readdirSync, rmSync } from "node:fs";
import { resolve } from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ command }) => {
  const config = {
    plugins: [
      react(),
      {
        // emptyOutDir is off (static/ also holds icons and the service worker), so drop
        // previously built hashed chunks ourselves or they pile up in git.
        name: "clean-hashed-chunks",
        apply: "build",
        buildStart() {
          const dir = resolve(__dirname, "src/openspoofen/static");
          for (const file of readdirSync(dir)) {
            if (/-[A-Za-z0-9_-]{8}\.js$/.test(file)) rmSync(resolve(dir, file));
          }
        },
      },
      {
        name: "dashboard-css-name",
        generateBundle(_, bundle) {
          for (const asset of Object.values(bundle)) {
            if (asset.type === "asset" && asset.fileName === "main.css") asset.fileName = "dashboard-app.css";
          }
        },
      },
    ],
    define: {
      "process.env.NODE_ENV": JSON.stringify("production"),
    },
    build: {
      outDir: resolve(__dirname, "src/openspoofen/static"),
      emptyOutDir: false,
      target: "chrome88",
      cssCodeSplit: true,
      lib: {
        entry: resolve(__dirname, "frontend/main.jsx"),
        formats: ["es"],
        fileName: () => "dashboard-app.js",
        cssFileName: "dashboard-app",
      },
    },
  };

  if (command === "serve") {
    config.server = {
      host: "0.0.0.0",
      proxy: {
        "/api": "http://openspoofen.local:8080",
        "/setup": "http://openspoofen.local:8080",
        "/login": "http://openspoofen.local:8080",
        "/logout": "http://openspoofen.local:8080",
        "/healthz": "http://openspoofen.local:8080",
        "/connect": "http://openspoofen.local:8080",
        "/disconnect": "http://openspoofen.local:8080",
        "/provider": "http://openspoofen.local:8080",
      },
    };
  }

  return config;
});
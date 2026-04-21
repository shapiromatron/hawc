import react from "@vitejs/plugin-react";
import fs from "fs";
import path from "path";
import {defineConfig} from "vite";
import {viteExternalsPlugin} from "vite-plugin-externals";

const outDir = "../hawc/static/bundles";

export default defineConfig({
    root: ".",
    base: "/static/bundles",
    plugins: [
        react(),
        viteExternalsPlugin({
            $: "$",
        }),
        {
            name: "create-empty-gitkeep",
            closeBundle() {
                const dest = path.resolve(__dirname, outDir, ".gitkeep");
                fs.writeFileSync(dest, "");
            },
        },
    ],
    build: {
        outDir,
        emptyOutDir: true,
        manifest: "manifest.json",
        rollupOptions: {
            input: {
                main: "index.js",
            },
            output: {
                manualChunks: function manualChunks(id) {
                    if (id.includes("node_modules")) {
                        if (id.includes("plotly")) {
                            return "plotly";
                        } else if (id.includes("d3")) {
                            return "d3";
                        } else if (
                            id.includes("react") ||
                            id.includes("mobx") ||
                            id.includes("quill")
                        ) {
                            return "ui";
                        } else {
                            return "vendor";
                        }
                    }
                    return null;
                },
            },
        },
    },
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "."),
        },
    },
    server: {
        port: 8050,
        host: "0.0.0.0",
        strictPort: true,
        cors: true,
        hmr: true,
    },
    optimizeDeps: {
        include: [
            "react",
            "react-dom",
            "react/jsx-runtime",
            "react/jsx-dev-runtime",
            "react-dom/client",
            "react-plotly.js",
        ],
    },
    oxc: {
        decorator: {legacy: true},
    },
});

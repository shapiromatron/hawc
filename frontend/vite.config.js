import fs from "fs";
import path from "path";
import react from "@vitejs/plugin-react";
import {defineConfig} from "vite";
import {viteExternalsPlugin} from "vite-plugin-externals";

const outDir = "../hawc/static/bundles";

export default defineConfig({
    root: ".",
    base: "/static/bundles",
    plugins: [
        react({
            babel: {
                presets: [
                    [
                        "@babel/preset-react",
                        {
                            runtime: "classic",
                            importSource: undefined,
                        },
                    ],
                ],
                plugins: [
                    ["@babel/plugin-proposal-decorators", {legacy: true}],
                    ["@babel/plugin-proposal-class-properties", {loose: false}],
                ],
            },
        }),
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
        manifest: true,
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
            // Application module aliases
            animal: path.resolve(__dirname, "animal"),
            assessment: path.resolve(__dirname, "assessment"),
            bmd: path.resolve(__dirname, "bmd"),
            eco: path.resolve(__dirname, "eco"),
            epi: path.resolve(__dirname, "epi"),
            epiv2: path.resolve(__dirname, "epiv2"),
            epimeta: path.resolve(__dirname, "epimeta"),
            invitro: path.resolve(__dirname, "invitro"),
            lit: path.resolve(__dirname, "lit"),
            mgmt: path.resolve(__dirname, "mgmt"),
            riskofbias: path.resolve(__dirname, "riskofbias"),
            shared: path.resolve(__dirname, "shared"),
            study: path.resolve(__dirname, "study"),
            summary: path.resolve(__dirname, "summary"),
            // React 18 compatibility: resolve legacy CommonJS paths to ESM
            "react/cjs/react.production.min": "react",
            "react/cjs/react.development": "react",
        },
        // Prioritize ESM modules for React 18 compatibility
        conditions: ["import", "module", "browser", "default"],
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
            "react-dom/client"
        ],
        esbuildOptions: {
            loader: {
                ".js": "jsx",
            },
        },
    },
    esbuild: {
        loader: "jsx",
        include: /.*\.jsx?$/,
        exclude: [],
    },
});

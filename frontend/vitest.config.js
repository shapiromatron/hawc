import {defineConfig} from "vitest/config";

import viteConfig from "./vite.config.js";

export default defineConfig({
    ...viteConfig,
    test: {
        environment: "jsdom",
        globals: true,
        include: ["tests/**/*.js"],
        testTimeout: 20000,
    },
});

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: '.',
  plugins: [
    react({
      jsxImportSource: undefined, // use classic React JSX transform
      babel: {
        presets: [
          [
            '@babel/preset-react',
            {
              runtime: 'classic',
              importSource: undefined,
            },
          ],
        ],
        plugins: [
          [
            '@babel/plugin-proposal-decorators',
            { legacy: true }
          ],
          [
            '@babel/plugin-proposal-class-properties',
            { loose: false }
          ]
        ],
      },
      include: /frontend\/.*\.js$/,
    }),
  ],
  build: {
    outDir: '../hawc/static/bundles',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: './index.js',
      },
      output: {
        entryFileNames: '[name].[hash].js',
        chunkFileNames: '[name].[hash].js',
        assetFileNames: '[name].[hash].[ext]',
      },
      external: ["$"],
    },
  },
  resolve: {
    alias: {
      animal: path.resolve(__dirname, 'animal'),
      assessment: path.resolve(__dirname, 'assessment'),
      bmd: path.resolve(__dirname, 'bmd'),
      eco: path.resolve(__dirname, 'eco'),
      epi: path.resolve(__dirname, 'epi'),
      epiv2: path.resolve(__dirname, 'epiv2'),
      epimeta: path.resolve(__dirname, 'epimeta'),
      invitro: path.resolve(__dirname, 'invitro'),
      lit: path.resolve(__dirname, 'lit'),
      mgmt: path.resolve(__dirname, 'mgmt'),
      riskofbias: path.resolve(__dirname, 'riskofbias'),
      shared: path.resolve(__dirname, 'shared'),
      study: path.resolve(__dirname, 'study'),
      summary: path.resolve(__dirname, 'summary'),
    },
  },
  server: {
    port: 8050,
    host: '0.0.0.0',
    strictPort: true,
    cors: true,
    origin: 'http://localhost:8050',
  },
  esbuild: {
    loader: {
      '.js': 'jsx',
    },
    include: /frontend\/.*\.js$/,
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react/jsx-runtime',
      'react/jsx-dev-runtime'
    ]
  },
});

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import reactJsSupport from 'vite-plugin-react-js-support';
import commonjs from '@rollup/plugin-commonjs';
import path from 'path';

export default defineConfig({
  plugins: [
    reactJsSupport(),
    react({
      jsxRuntime: 'classic',
      babel: {
        plugins: [
          ['@babel/plugin-proposal-decorators', { legacy: true }],
          ['@babel/plugin-transform-class-properties', { loose: true }],
        ],
      },
    }),
    commonjs(),
  ],

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

  build: {
    outDir: '../hawc/static/bundles',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: './index.js',
      external: ['$', 'quill'],
      plugins: [
        {
          name: 'disable-import-analysis',
          buildStart() {
            // Try to disable the import analysis plugin
            this.resolveId = () => null;
          }
        }
      ],
      output: {
        entryFileNames: '[name].[hash].js',
        chunkFileNames: '[name].[hash].js',
        assetFileNames: '[name].[hash].[ext]',
        globals: {
          $: '$',
          quill: 'Quill',
        },
      },
    },
  },

  server: {
    port: 8050,
    host: '0.0.0.0',
    cors: {
      origin: '*',
      allowedHeaders: ['Origin', 'X-Requested-With', 'Content-Type', 'Accept'],
    },
  },
});
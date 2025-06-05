// This file is used to map Vite's manifest.json to Django's expected webpack-stats.json format.
// Run this after `vite build` to generate the file Django expects.
const fs = require('fs');
const path = require('path');

const manifestPath = path.resolve(__dirname, '../hawc/static/bundles/manifest.json');
const outputPath = path.resolve(__dirname, '../hawc/webpack-stats.json');

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));

const stats = {
  status: 'done',
  publicPath: '/static/bundles/',
  chunks: {
    main: [manifest['index.js'] ? manifest['index.js'].file : Object.values(manifest)[0].file],
  },
  assetsByChunkName: {
    main: manifest['index.js'] ? manifest['index.js'].file : Object.values(manifest)[0].file,
  },
};

fs.writeFileSync(outputPath, JSON.stringify(stats, null, 2));
console.log('Generated webpack-stats.json for Django integration.');

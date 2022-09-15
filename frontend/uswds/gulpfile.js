/* gulpfile.js */

const uswds = require("@uswds/compile");

/**
 * USWDS version
 * Set the version of USWDS you're using (2 or 3)
 */

uswds.settings.version = 3;

/**
 * Path settings
 * Set as many as you need
 */

uswds.paths.dist.css = '../../hawc/static/css';
uswds.paths.dist.sass = '../../sass';
uswds.paths.dist.theme = '../../frontend/sass';
uswds.paths.dist.img = '../../hawc/static/vendor/uswds/3.1.0/img';
uswds.paths.dist.fonts = '../../hawc/static/vendor/uswds/3.1.0/fonts';
uswds.paths.dist.js = '../../hawc/static/vendor/uswds/3.1.0/js';
uswds.paths.dist.css = '../../hawc/static/vendor/uswds/3.1.0/css';
uswds.paths.src.uswds = './node_modules/@uswds';
uswds.paths.src.sass = './node_modules/@uswds/uswds/packages';
uswds.paths.src.theme = './node_modules/@uswds/uswds/dist/theme';
uswds.paths.src.fonts = './node_modules/@uswds/uswds/dist/fonts';
uswds.paths.src.img = './node_modules/@uswds/uswds/dist/img';
uswds.paths.src.js = './node_modules/@uswds/uswds/dist/js';
uswds.paths.src.projectSass = './sass';

/**
 * Exports
 * Add as many as you need
 */

exports.init = uswds.init;
exports.compile = uswds.compile;
exports.compileIcons = uswds.compileIcons;
exports.compileSass = uswds.compileSass;

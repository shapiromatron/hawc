const uswds = require("@uswds/compile");

uswds.settings.version = 3;

// input paths
uswds.paths.src.fonts = "../node_modules/@uswds/uswds/dist/fonts";
uswds.paths.src.img = "../node_modules/@uswds/uswds/dist/img";
uswds.paths.src.js = "../node_modules/@uswds/uswds/dist/js";
uswds.paths.src.projectSass = "./sass";
uswds.paths.src.sass = "../node_modules/@uswds/uswds/packages";
uswds.paths.src.theme = "../node_modules/@uswds/uswds/dist/theme";
uswds.paths.src.uswds = "../node_modules/@uswds";

// output paths
uswds.paths.dist.css = "../../hawc/static/vendor/uswds/3.1.0/css";
uswds.paths.dist.fonts = "../../hawc/static/vendor/uswds/3.1.0/fonts";
uswds.paths.dist.img = "../../hawc/static/vendor/uswds/3.1.0/img";
uswds.paths.dist.js = "../../hawc/static/vendor/uswds/3.1.0/js";

// exports
exports.compile = uswds.compile;
exports.compileSass = uswds.compileSass;
exports.copyAssets = uswds.copyAssets;
exports.init = uswds.init;

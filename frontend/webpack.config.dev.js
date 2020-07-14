var config = require("./webpack.base.js"),
    port = 8050;

config.devtool = "cheap-module-eval-source-map";

config.output.publicPath = "http://localhost:" + port + "/dist/";

module.exports = config;

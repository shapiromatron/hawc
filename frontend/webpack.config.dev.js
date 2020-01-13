var config = require("./webpack.base.js"),
    port = 8001;

config.devtool = "cheap-module-eval-source-map";

config.output.publicPath = "http://localhost:" + port + "/dist/";

module.exports = config;

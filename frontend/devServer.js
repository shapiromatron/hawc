const CaseSensitivePathsPlugin = require("case-sensitive-paths-webpack-plugin"),
    getConfig = function(host, port) {
        var config = require("./webpack.base.js");
        config.devtool = "cheap-module-eval-source-map";
        config.output.publicPath = `http://${host}:${port}/dist/`;
        config.plugins.push(new CaseSensitivePathsPlugin());
        return config;
    },
    express = require("express"),
    middleware = require("webpack-dev-middleware"),
    webpack = require("webpack"),
    host = process.env.CI ? process.env.LIVESERVER_HOST : "localhost",
    port = 8050,
    config = getConfig(host, port),
    app = express(),
    compiler = webpack(config);

app.use(
    middleware(compiler, {
        noInfo: true,
        publicPath: config.output.publicPath,
    })
);

app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

app.listen(port, "0.0.0.0", function(err) {
    if (err) {
        console.error(err);
        return;
    }
    // eslint-disable-next-line no-console
    console.info(`Listening at http://${host}:${port}`);
});

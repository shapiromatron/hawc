const _ = require("lodash"),
    express = require("express"),
    middleware = require("webpack-dev-middleware"),
    webpack = require("webpack"),
    CaseSensitivePathsPlugin = require("case-sensitive-paths-webpack-plugin"),
    prodConfig = require("./webpack.config.js");

let getConfig = function (host, port) {
        let config = _.cloneDeep(prodConfig);
        config.mode = "development";
        config.devtool = "eval";
        config.output.publicPath = `http://${host}:${port}/dist/`;
        config.plugins.push(new CaseSensitivePathsPlugin());
        return config;
    },
    host = process.env.CI ? process.env.LIVESERVER_HOST : "localhost",
    port = 8050,
    devConfig = getConfig(host, port),
    app = express(),
    compiler = webpack(devConfig);

app.use(
    middleware(compiler, {
        publicPath: devConfig.output.publicPath,
    })
);

app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

app.listen(port, "0.0.0.0", function (err) {
    if (err) {
        console.error(err);
        return;
    }
    // eslint-disable-next-line no-console
    console.info(`Listening at http://${host}:${port}`);
});

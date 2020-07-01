const express = require("express"),
    middleware = require("webpack-dev-middleware"),
    webpack = require("webpack"),
    config = require("./webpack.config.dev"),
    port = 8050,
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
    console.info("Listening at http://localhost:" + port);
});

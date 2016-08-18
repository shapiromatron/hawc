var args = process.argv.slice(2),
    express = require('express'),
    webpack = require('webpack'),
    config = require('./webpack.config.dev'),
    Dashboard = require('webpack-dashboard'),
    DashboardPlugin = require('webpack-dashboard/plugin');

if (args.indexOf('--testProduction')>=0){
    console.log('Using test production;');
    config.plugins.unshift(new webpack.DefinePlugin({
        'process.env': {
            'NODE_ENV': JSON.stringify('production'),
        },
    }));
}

var app = express(),
    compiler = webpack(config);

compiler.apply(new DashboardPlugin());

app.use(require('webpack-dev-middleware')(compiler, {
    quiet: true,
    publicPath: config.output.publicPath,
}));

app.use(require('webpack-hot-middleware')(compiler, {
    log: () => {},
}));

app.use(function(req, res, next) {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
});

app.listen(config.devPort, 'localhost', function(err) {
    if (err) {
        console.log(err);
        return;
    }
    console.log('Listening at http://localhost:' + config.devPort);
});

var config = require('./webpack.base.js'),
    path = require('path'),
    webpack = require('webpack');


config.devtool = 'source-map';

config.output.path = path.resolve('./static/bundles');

config.plugins.unshift.apply(config.plugins, [
    new webpack.DefinePlugin({
        'process.env': {
            'NODE_ENV': JSON.stringify('production'),
        },
    }),
    new webpack.optimize.UglifyJsPlugin({
        compressor: {
            warnings: false,
        },
    }),
]);

config.module = {
    loaders: [{
        test: /\.js$/,
        loader: 'babel',
        include: path.join(__dirname, 'assets'),
    }, {
        test: /\.css$/, loader: 'style!css',
    }],
};

module.exports = config;

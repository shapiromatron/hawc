var config = require('./webpack.base.js'),
    path = require('path'),
    webpack = require('webpack');


config.devtool = 'source-map';

config.entry =  ['./src/index'];

config.output.publicPath = '/static/';
config.plugins.unshift([
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
        include: path.join(__dirname, 'src'),
    }],
};

module.exports = config;

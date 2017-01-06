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
        sourceMap: true,
    }),
    new webpack.LoaderOptionsPlugin({
        minimize: true,
    }),
]);

config.module = {
    loaders: [{
        test: /\.js$/,
        loader: 'babel-loader',
        include: path.join(__dirname, 'assets'),
    }, {
        test: /\.css$/, loader: 'style-loader!css-loader',
    }],
};

module.exports = config;

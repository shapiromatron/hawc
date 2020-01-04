var config = require('./webpack.base.js'),
    path = require('path'),
    webpack = require('webpack');

config.devtool = 'source-map';

config.output.path = path.resolve('../project/static/bundles');
config.output.publicPath = '/static/bundles/';

config.plugins.unshift.apply(config.plugins, [
    new webpack.DefinePlugin({
        'process.env': {
            NODE_ENV: JSON.stringify('production'),
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
    rules: [
        {
            test: /\.js$/,
            use: 'babel-loader',
            include: config.resolve.modules.slice(0, -1),
        },
        {
            test: /\.css$/,
            loader: 'style-loader!css-loader',
        },
    ],
};

module.exports = config;

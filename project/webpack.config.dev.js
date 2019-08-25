var config = require('./webpack.base.js'),
    path = require('path'),
    webpack = require('webpack'),
    port = 3001,
    HappyPack = require('happypack');

config.devtool = 'cheap-module-eval-source-map';

config.output.publicPath = 'http://localhost:' + port + '/dist/';

config.plugins.unshift(
    new HappyPack({
        id: 'js',
        loaders: [
            {
                loader: 'babel-loader',
                options: {
                    plugins: [
                        ['transform-object-rest-spread'],
                        ['syntax-object-rest-spread'],
                        ['syntax-dynamic-import'],
                        ['dynamic-import-webpack'],
                    ],
                },
            },
        ],
        verbose: false,
        threads: 4,
    })
);

config.module = {
    noParse: /node_modules\/quill\/dist\/quill\.js/,
    rules: [
        {
            test: /\.js$/,
            use: 'happypack/loader?id=js',
            include: config.resolve.modules.slice(0, -1),
        },
        {
            test: /\.css$/,
            loader: 'style-loader!css-loader',
        },
    ],
};

module.exports = config;

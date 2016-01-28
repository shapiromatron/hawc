var config = require('./webpack.base.js'),
    path = require('path'),
    webpack = require('webpack');

config.devtool = 'cheap-module-eval-source-map';
config.entry = [
    'webpack-hot-middleware/client?path=http://localhost:3000/__webpack_hmr',
    './assets/js/index',
];
config.output.publicPath = 'http://localhost:3000/dist/';

config.plugins.unshift(new webpack.HotModuleReplacementPlugin());

config.module = {
    loaders: [{
        test: /\.js$/,
        loader: 'babel',
        include: path.join(__dirname, 'assets/js'),
        query: {
            plugins: [
                ['react-transform', {
                    transforms: [{
                        transform: 'react-transform-hmr',
                        imports: ['react'],
                        locals: ['module'],
                    }, {
                        'transform': 'react-transform-catch-errors',
                        'imports': ['react', 'redbox-react'],
                    }],
                }],
            ],
        },
    }, {
        test: /\.css$/, loader: 'style!css',
    }],
};

module.exports = config;

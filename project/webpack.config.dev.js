var config = require('./webpack.base.js'),
    path = require('path'),
    webpack = require('webpack'),
    devPort = 3000;

config.devPort = devPort;
config.devtool = 'cheap-module-eval-source-map';
config.entry = [
    'webpack-hot-middleware/client?path=http://localhost:' + devPort + '/__webpack_hmr',
    './assets/index',
];
config.output.publicPath = 'http://localhost:' + devPort + '/dist/';

config.plugins.unshift(new webpack.HotModuleReplacementPlugin());

config.module = {
    noParse: /node_modules\/quill\/dist\/quill\.js/,
    loaders: [{
        test: /\.js$/,
        loader: 'babel',
        include: path.join(__dirname, 'assets'),
        query: {
            plugins: [
                ['transform-object-rest-spread'],
                ['syntax-object-rest-spread'],
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

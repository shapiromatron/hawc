var config = require('./webpack.base.js'),
    path = require('path'),
    webpack = require('webpack'),
    port = 3000,
    HappyPack = require('happypack');

config.devtool = 'cheap-module-eval-source-map';
config.entry.main = [
    'webpack-hot-middleware/client?path=http://localhost:' + port + '/__webpack_hmr',
    './assets/index',
];
config.output.publicPath = 'http://localhost:' + port + '/dist/';

config.plugins.unshift(new webpack.HotModuleReplacementPlugin());
config.plugins.unshift(new HappyPack({
    id: 'js',
    loaders: [{
        path: 'babel-loader',
        options: {
            plugins: [
                ['transform-object-rest-spread'],
                ['syntax-object-rest-spread'],
                ['syntax-dynamic-import'],
                ['dynamic-import-webpack'],
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
    }],
    verbose: false,
    threads: 4,
}));

config.module = {
    noParse: /node_modules\/quill\/dist\/quill\.js/,
    rules: [{
        test: /\.js$/,
        use: 'happypack/loader?id=js',
        include: path.join(__dirname, 'assets'),
    }, {
        test: /\.css$/, loader: 'style-loader!css-loader',
    }],
};

module.exports = config;

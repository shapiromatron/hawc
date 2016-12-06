var config = require('./webpack.base.js'),
    path = require('path'),
    webpack = require('webpack'),
    devPort = 3000,
    HappyPack = require('happypack');

config.devPort = devPort;
config.devtool = 'eval-source-map';
config.entry = [
    'webpack-hot-middleware/client?path=http://localhost:' + devPort + '/__webpack_hmr',
    './assets/index',
];
config.output.publicPath = 'http://localhost:' + devPort + '/dist/';

config.plugins.unshift(new webpack.HotModuleReplacementPlugin());
config.plugins.unshift(new HappyPack({ id: 'js', verbose: false, threads: 4 }));

config.module = {
    noParse: /node_modules\/quill\/dist\/quill\.js/,
    loaders: [{
        test: /\.js$/,
        loader: 'babel',
        happy: { id: 'js' },
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
    },{
        test: require.resolve('vega'),
        loaders: [
            'transform?vega/scripts/strip-schema.js',
      ]
    },{
        test: /\.json$/,
        loader: 'json-loader'
    }],
};

module.exports = config;

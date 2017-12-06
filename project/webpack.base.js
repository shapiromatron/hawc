var path = require('path'),
    webpack = require('webpack'),
    BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    context: __dirname,

    resolve: {
        modules: [
            path.join(__dirname, 'assets'),
            path.join(__dirname, 'animal', 'assets'),
            path.join(__dirname, 'assessment', 'assets'),
            path.join(__dirname, 'bmd', 'assets'),
            path.join(__dirname, 'epi', 'assets'),
            path.join(__dirname, 'epimeta', 'assets'),
            path.join(__dirname, 'invitro', 'assets'),
            path.join(__dirname, 'lit', 'assets'),
            path.join(__dirname, 'mgmt', 'assets'),
            path.join(__dirname, 'riskofbias', 'assets'),
            path.join(__dirname, 'study', 'assets'),
            path.join(__dirname, 'summary', 'assets'),
            path.join(__dirname, 'utils', 'assets'),
            'node_modules',
        ],
        extensions: ['.js', '.css'],
    },

    entry: {
        main: [
            './assets/index',
            './animal/assets/index',
            './assessment/assets/index',
            './bmd/assets/index',
            './epi/assets/index',
            './epimeta/assets/index',
            './invitro/assets/index',
            './lit/assets/index',
            './mgmt/assets/index',
            './riskofbias/assets/index',
            './study/assets/index',
            './summary/assets/index',
            './utils/assets/index',
        ],
    },

    output: {
        path: path.join(__dirname, 'dist'),
        filename: '[name].[hash].js',
        chunkFilename: '[name].[hash].js',
    },

    externals: {
        $: '$',
    },

    plugins: [
        new webpack.optimize.CommonsChunkPlugin({
            name: 'vendor',
            filename: 'vendor.[hash].js',
            minChunks: (module, count) => {
                // puts imported node_modules module code into vendor chunk
                const userRequest = module.userRequest;
                return userRequest && userRequest.indexOf('node_modules') >= 0;
            },
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'manifest',
            filename: 'manifest.[hash].js',
        }),
        new webpack.NoEmitOnErrorsPlugin(),
        new BundleTracker({
            filename: './webpack-stats.json',
        }),
    ],
};

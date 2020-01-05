var path = require('path'),
    webpack = require('webpack'),
    BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    context: __dirname,

    resolve: {
        alias: {
            assets: path.join(__dirname, 'assets'),
            animal: path.join(__dirname, 'animal'),
            assessment: path.join(__dirname, 'assessment'),
            bmd: path.join(__dirname, 'bmd'),
            epi: path.join(__dirname, 'epi'),
            epimeta: path.join(__dirname, 'epimeta'),
            invitro: path.join(__dirname, 'invitro'),
            lit: path.join(__dirname, 'lit'),
            mgmt: path.join(__dirname, 'mgmt'),
            riskofbias: path.join(__dirname, 'riskofbias'),
            study: path.join(__dirname, 'study'),
            summary: path.join(__dirname, 'summary'),
            utils: path.join(__dirname, 'utils'),
        },
        modules: [
            path.join(__dirname, 'animal'),
            path.join(__dirname, 'assessment'),
            path.join(__dirname, 'assets'),
            path.join(__dirname, 'bmd'),
            path.join(__dirname, 'epi'),
            path.join(__dirname, 'epimeta'),
            path.join(__dirname, 'invitro'),
            path.join(__dirname, 'lit'),
            path.join(__dirname, 'mgmt'),
            path.join(__dirname, 'riskofbias'),
            path.join(__dirname, 'study'),
            path.join(__dirname, 'summary'),
            path.join(__dirname, 'utils'),
            'node_modules',
        ],
        extensions: ['.js', '.css'],
    },

    entry: {
        main: [
            './animal/index',
            './assessment/index',
            './assets/index',
            './bmd/index',
            './epi/index',
            './epimeta/index',
            './invitro/index',
            './lit/index',
            './mgmt/index',
            './riskofbias/index',
            './study/index',
            './summary/index',
            './utils/index',
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
            filename: '../project/webpack-stats.json',
        }),
    ],
};

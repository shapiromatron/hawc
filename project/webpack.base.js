var path = require('path'),
    webpack = require('webpack'),
    BundleTracker = require('webpack-bundle-tracker');


module.exports = {

    context: __dirname,

    resolve: {
        modules: [
            path.join(__dirname, 'assets'),
            'node_modules',
        ],
        extensions: ['.js', '.css'],
    },

    entry: {
        main: './assets/index',
    },

    output: {
        path: path.join(__dirname, 'dist'),
        filename: '[name].[hash].js',
        chunkFilename: '[name].js',
    },

    externals: {
        $: '$',
        Outcome: 'Outcome',
    },

    plugins: [
        new webpack.optimize.CommonsChunkPlugin({
            name: 'vendor',
            filename: 'vendor.js',
            minChunks: (module, count) => {
                // puts imported node_modules module code into vendor chunk
                const userRequest = module.userRequest;
                return userRequest && userRequest.indexOf('node_modules') >= 0;
            },
        }),
        new webpack.optimize.CommonsChunkPlugin({name: 'manifest', filename: 'manifest.js'}),
        new webpack.NoErrorsPlugin(),
        new BundleTracker({filename: './webpack-stats.json'}),
    ],
};

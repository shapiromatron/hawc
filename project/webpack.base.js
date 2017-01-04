var path = require('path'),
    webpack = require('webpack'),
    BundleTracker = require('webpack-bundle-tracker');


module.exports = {

    context: __dirname,

    resolve: {
        modules: [
            path.join(__dirname, "assets"),
            "node_modules"
        ],
        extensions: ['.js', '.css'],
    },

    entry: [
        './assets/index',
    ],

    output: {
        path: path.join(__dirname, 'dist'),
        filename: 'bundle.js',
    },

    externals: {
        $: '$',
        Outcome: 'Outcome',
    },

    plugins: [
        new webpack.NoErrorsPlugin(),
        new BundleTracker({filename: './webpack-stats.json'}),
    ],
};

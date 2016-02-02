var path = require('path'),
    webpack = require('webpack'),
    BundleTracker = require('webpack-bundle-tracker');



module.exports = {

    context: __dirname,

    resolve: {
        root: path.resolve(__dirname, 'assets/js'),
        extensions: ['', '.js', '.css'],
    },

    entry: [
        './assets/js/index',
    ],

    output: {
        path: path.join(__dirname, 'dist'),
        filename: 'bundle.js',
    },

    plugins: [
        new webpack.optimize.OccurenceOrderPlugin(),
        new webpack.NoErrorsPlugin(),
        new BundleTracker({filename: './webpack-stats.json'}),
    ],
};

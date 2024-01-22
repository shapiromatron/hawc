const path = require("path"),
    BundleTracker = require("webpack-bundle-tracker");

module.exports = {
    context: __dirname,

    entry: {
        main: ["./index.js"],
    },

    externals: {
        $: "$",
    },

    mode: "production",

    module: {
        noParse: /node_modules\/quill\/dist\/quill\.js/,
        rules: [
            {
                exclude: /node_modules/,
                test: /\.js$/,
                use: {
                    loader: "babel-loader",
                    options: {
                        plugins: [["@babel/plugin-transform-class-properties", {loose: false}]],
                    },
                },
            },
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
        ],
    },

    output: {
        filename: "[name].[contenthash].js",
        chunkFilename: "[name].[contenthash].js",
        path: path.resolve(__dirname, "../hawc/static/bundles"),
        publicPath: "/static/bundles/",
    },

    plugins: [
        new BundleTracker({
            path: path.resolve(__dirname, "../hawc"),
            filename: "webpack-stats.json",
        }),
    ],

    resolve: {
        roots: [__dirname],
        alias: {
            animal: path.join(__dirname, "animal"),
            assessment: path.join(__dirname, "assessment"),
            bmd: path.join(__dirname, "bmd"),
            eco: path.join(__dirname, "eco"),
            epi: path.join(__dirname, "epi"),
            epiv2: path.join(__dirname, "epiv2"),
            epimeta: path.join(__dirname, "epimeta"),
            invitro: path.join(__dirname, "invitro"),
            lit: path.join(__dirname, "lit"),
            mgmt: path.join(__dirname, "mgmt"),
            riskofbias: path.join(__dirname, "riskofbias"),
            shared: path.join(__dirname, "shared"),
            study: path.join(__dirname, "study"),
            summary: path.join(__dirname, "summary"),
        },
    },
};

const path = require("path"),
    BundleTracker = require("webpack-bundle-tracker");

module.exports = {
    context: __dirname,

    entry: {
        main: ["./index"],
    },

    externals: {
        $: "$",
    },

    mode: "development",

    module: {
        noParse: /node_modules\/quill\/dist\/quill\.js/,
        rules: [
            {
                exclude: /node_modules/,
                test: /\.js$/,
                use: {
                    loader: "babel-loader",
                    options: {
                        plugins: [
                            "@babel/plugin-syntax-dynamic-import",
                            ["@babel/plugin-proposal-class-properties", {loose: false}],
                        ],
                    },
                },
            },
            {
                test: /\.css$/,
                loader: "style-loader!css-loader",
            },
        ],
    },

    output: {
        filename: "[name].[hash].js",
        chunkFilename: "[name].[hash].js",
        path: path.resolve("../hawc/static/bundles"),
        publicPath: "/static/bundles/",
    },

    plugins: [
        new BundleTracker({
            filename: "../hawc/webpack-stats.json",
        }),
    ],

    resolve: {
        alias: {
            assets: path.join(__dirname, "assets"),
            admin: path.join(__dirname, "admin"),
            animal: path.join(__dirname, "animal"),
            assessment: path.join(__dirname, "assessment"),
            bmd: path.join(__dirname, "bmd"),
            epi: path.join(__dirname, "epi"),
            epimeta: path.join(__dirname, "epimeta"),
            invitro: path.join(__dirname, "invitro"),
            lit: path.join(__dirname, "lit"),
            main: path.join(__dirname, "main"),
            mgmt: path.join(__dirname, "mgmt"),
            riskofbias: path.join(__dirname, "riskofbias"),
            study: path.join(__dirname, "study"),
            summary: path.join(__dirname, "summary"),
            utils: path.join(__dirname, "utils"),
        },
        modules: [path.join(__dirname, "assets"), path.join(__dirname, "utils"), "node_modules"],
        extensions: [".js", ".css"],
    },
};

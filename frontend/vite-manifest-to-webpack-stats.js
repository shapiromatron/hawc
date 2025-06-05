const fs = require("fs"),
    path = require("path"),
    manifestPath = path.resolve(__dirname, "../hawc/static/bundles/manifest.json"),
    outputPath = path.resolve(__dirname, "../hawc/webpack-stats.json"),
    manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8")),
    stats = {
        status: "done",
        publicPath: "/static/bundles/",
        chunks: {
            main: [
                manifest["index.js"] ? manifest["index.js"].file : Object.values(manifest)[0].file,
            ],
        },
        assets: {
            main: manifest["index.js"]
                ? manifest["index.js"].file
                : Object.values(manifest)[0].file,
        },
    };

fs.writeFileSync(outputPath, JSON.stringify(stats, null, 2));

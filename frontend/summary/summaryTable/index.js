export const summaryTableViewStartup = function(cb) {
        import("./viewing/index.js").then(app => cb(app.default));
    },
    summaryTableEditStartup = function(cb) {
        import("./editing/index.js").then(app => cb(app.default));
    };

window.app.litStartup = function(callback) {
    import("./split.js").then(lit => callback(lit.default));
};

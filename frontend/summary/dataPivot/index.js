const dataPivotStartup = function(cb) {
    import("./split.js").then(dataPivot => {
        cb(dataPivot.default);
    });
};

export default dataPivotStartup;

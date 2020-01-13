const epiStartup = function(cb) {
    import("./split.js").then(epi => {
        cb(epi.default);
    });
};

window.app.epiStartup = epiStartup;

export default epiStartup;

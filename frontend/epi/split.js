const startup = function(cb) {
    import("./index.js").then(epi => {
        cb(epi.default);
    });
};

export default startup;

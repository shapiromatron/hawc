const startup = function(cb) {
    import("./index.js").then(smartTags => {
        cb(smartTags.default);
    });
};

export default startup;

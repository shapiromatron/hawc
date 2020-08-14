const startup = function(cb) {
    import("./split.js").then(app => {
        cb(app.default);
    });
};
export default startup;

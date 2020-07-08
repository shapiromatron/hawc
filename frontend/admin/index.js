const adminStartup = function(cb) {
    import("./split.js").then(app => {
        cb(app.default);
    });
};

window.app = {};
window.app.adminStartup = adminStartup;

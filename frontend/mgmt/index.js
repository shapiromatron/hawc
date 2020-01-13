const mgmtStartup = function(cb) {
    import("./split.js").then(mgmt => {
        cb(mgmt.default);
    });
};

window.app.mgmtStartup = mgmtStartup;

export default mgmtStartup;

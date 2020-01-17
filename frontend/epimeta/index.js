const epimetaStartup = function(cb) {
    import("./split.js").then(epimeta => {
        cb(epimeta.default);
    });
};

window.app.epimetaStartup = epimetaStartup;

export default epimetaStartup;

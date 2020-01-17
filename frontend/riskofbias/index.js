const riskofbiasStartup = function(cb) {
    import("./split.js").then(riskofbias => {
        cb(riskofbias.default);
    });
};

window.app.riskofbiasStartup = riskofbiasStartup;

export default riskofbiasStartup;

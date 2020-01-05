const litStartup = function(cb) {
    import('./split.js').then((lit) => {
        cb(lit.default);
    });
};

window.app.litStartup = litStartup;

export default litStartup;

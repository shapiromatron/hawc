const startup = function(cb) {
    import('./index.js').then((lit) => {
        cb(lit.default);
    });
};

export default startup;

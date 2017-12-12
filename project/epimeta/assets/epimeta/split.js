const startup = function(cb) {
    import('./index.js').then((epimeta) => {
        cb(epimeta.default);
    });
};

export default startup;

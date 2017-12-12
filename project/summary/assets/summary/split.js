const startup = function(cb) {
    import('./index.js').then((summary) => {
        cb(summary.default);
    });
};

export default startup;

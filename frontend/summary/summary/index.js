const startup = function(cb) {
    import('./split.js').then((summary) => {
        cb(summary.default);
    });
};

export default startup;

const startup = function(cb) {
    import('./index.js').then((study) => {
        cb(study.default);
    });
};

export default startup;

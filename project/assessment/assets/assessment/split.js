const startup = function(cb) {
    import('./index.js').then(assessment => {
        cb(assessment.default);
    });
};

export default startup;

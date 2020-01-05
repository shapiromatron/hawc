const startup = function(cb) {
    import('./split.js').then((summaryForms) => {
        cb(summaryForms.default);
    });
};

export default startup;

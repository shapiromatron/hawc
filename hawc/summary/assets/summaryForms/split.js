const startup = function(cb) {
    import('./index.js').then((summaryForms) => {
        cb(summaryForms.default);
    });
};

export default startup;

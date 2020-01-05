const studyStartup = function(cb) {
    import('./split.js').then((study) => {
        cb(study.default);
    });
};

window.app.studyStartup = studyStartup;

export default studyStartup;

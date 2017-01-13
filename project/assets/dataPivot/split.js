const startup = function(cb) {
    import('./index.js').then((dataPivot) => {
        cb(dataPivot.default);
    });

}

export default startup;

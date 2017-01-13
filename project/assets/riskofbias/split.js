const startup = function(cb) {
    import('./index.js').then((riskofbias) => {
        cb(riskofbias.default);
    });

}

export default startup;

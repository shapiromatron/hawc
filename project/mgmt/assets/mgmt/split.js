const startup = function(cb) {
    import('./index.js').then((mgmt) => {
        cb(mgmt.default);
    });
};

export default startup;

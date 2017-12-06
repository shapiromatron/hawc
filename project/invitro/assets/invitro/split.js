const startup = function(cb) {
    import('./index.js').then(invitro => {
        cb(invitro.default);
    });
};

export default startup;

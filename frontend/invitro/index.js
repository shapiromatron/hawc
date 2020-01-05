const invitroStartup = function(cb) {
    import('./split.js').then((invitro) => {
        cb(invitro.default);
    });
};

window.app.invitroStartup = invitroStartup;

export default invitroStartup;

const startup = function(cb) {
    import('./index.js').then((animal) => {
        cb(animal.default);
    });
}

export default startup;

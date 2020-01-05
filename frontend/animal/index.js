const animalStartup = function(cb) {
    import('./split.js').then((animal) => {
        cb(animal.default);
    });
};

window.app = {};
window.app.animalStartup = animalStartup;

export default animalStartup;

class Observee {
    constructor() {
        this._observers = [];
    }

    addObserver(obj) {
        this._observers.push(obj);
    }

    removeObserver(obj) {
        var idx = this._observers.indexOf(obj);
        if (idx >= 0) {
            this._observers.splice(idx, 1);
        }
    }

    notifyObservers(msg) {
        this._observers.forEach(function (d) {
            d.update(msg);
        });
    }
}

export default Observee;

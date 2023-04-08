class LocalStorageItem {
    // Persistently store item once class is instantiated using `window.localStorage`.
    constructor(key, defaultValue) {
        this.key = key;
        this.value = this.get();
        if (this.value === null) {
            this.set(defaultValue);
        }
    }
    get() {
        return window.localStorage.getItem(this.key);
    }
    set(value) {
        this.value = value;
        window.localStorage.setItem(this.key, value);
    }
}

class LocalStorageBoolean extends LocalStorageItem {
    // Storage designed specifically for boolean true/false fields. LocalStorage can only
    // store string-values, so this takes care of casting item to a boolean.
    get() {
        const value = super.get();
        switch (value) {
            case "true":
                return true;
            case "false":
                return false;
            case null:
                return null;
            default:
                throw `Unknown boolean value ${value}`;
        }
    }
    toggle() {
        this.set(!this.value);
    }
}

export {LocalStorageBoolean, LocalStorageItem};

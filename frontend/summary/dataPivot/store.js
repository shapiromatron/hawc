import {action, observable, toJS} from "mobx";

import {
    moveArrayElementUp,
    moveArrayElementDown,
    deleteArrayElement,
} from "shared/components/EditableRowData";
import {NULL_CASE} from "./shared";

class SortStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
        this.settings = this.rootStore.dp.settings.sorts;
    }

    @observable settings = null;

    @action.bound createNew() {
        this.settings.push({
            field_name: NULL_CASE,
            ascending: true,
        });
        this.rootStore.sync();
    }
    @action.bound moveUp(idx) {
        moveArrayElementUp(this.settings, idx);
        this.rootStore.sync();
    }
    @action.bound moveDown(idx) {
        moveArrayElementDown(this.settings, idx);
        this.rootStore.sync();
    }
    @action.bound delete(idx) {
        deleteArrayElement(this.settings, idx);
        this.rootStore.sync();
    }
    @action.bound updateElement(idx, field, value) {
        this.settings[idx][field] = value;
        this.rootStore.sync();
    }
}

class Store {
    constructor(dp) {
        this.dp = dp;
        this.sortStore = new SortStore(this);
    }
    sync() {
        // sync state in store to global object - TODO - remove?
        this.dp.settings.sorts = toJS(this.sortStore.settings);
    }
}

export default Store;

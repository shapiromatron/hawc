import _ from "lodash";
import {action, observable, toJS} from "mobx";
import {
    deleteArrayElement,
    moveArrayElementDown,
    moveArrayElementUp,
} from "shared/components/EditableRowData";

import {NULL_CASE, OrderChoices} from "./shared";

class SortStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
        this.settings = this.rootStore.dp.settings.sorts;
    }

    @observable settings = null;

    @action.bound createNew() {
        this.settings.push({
            field_name: NULL_CASE,
            order: OrderChoices.asc,
            custom: null,
        });
        this.rootStore.resetRowOverrides();
        this.rootStore.sync();
    }
    @action.bound moveUp(idx) {
        moveArrayElementUp(this.settings, idx);
        this.rootStore.resetRowOverrides();
        this.rootStore.sync();
    }
    @action.bound moveDown(idx) {
        moveArrayElementDown(this.settings, idx);
        this.rootStore.resetRowOverrides();
        this.rootStore.sync();
    }
    @action.bound delete(idx) {
        deleteArrayElement(this.settings, idx);
        this.rootStore.resetRowOverrides();
        this.rootStore.sync();
    }
    @action.bound updateElement(idx, field, value) {
        this.settings[idx][field] = value;
        this.rootStore.resetRowOverrides();
        this.rootStore.sync();
    }
    @action.bound updateOrder(idx, value) {
        if (value === OrderChoices.custom) {
            this.settings[idx].custom = this.getSortItems(idx);
        } else {
            this.settings[idx].custom = null;
        }
        this.settings[idx].order = value;
        this.rootStore.resetRowOverrides();
        this.rootStore.sync();
    }
    @action.bound changeOrder(idx, oldIndex, newIndex) {
        const items = _.cloneDeep(toJS(this.settings[idx].custom)),
            item = items.splice(oldIndex, 1)[0];
        items.splice(newIndex, 0, item);
        this.settings[idx].custom = items;
        this.rootStore.resetRowOverrides();
        this.rootStore.sync();
    }
    getSortItems(idx) {
        const key = this.settings[idx].field_name;
        if (key === NULL_CASE) {
            return [];
        }
        return _.chain(this.rootStore.dp.data)
            .map(key)
            .uniq()
            .sort()
            .value();
    }
}

class ColumnNameStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
        this.settings = this.rootStore.dp.settings.sorts;
    }
}

class Store {
    constructor(dp) {
        this.dp = dp;
        this.sortStore = new SortStore(this);
        this.columnNameStore = new ColumnNameStore(this);
    }
    // TODO - remove methods below (after rewrite to React from jQuery)
    sync() {
        this.dp.settings.sorts = toJS(this.sortStore.settings);
    }
    handleOverrideRefresh = null;
    resetRowOverrides() {
        this.handleOverrideRefresh();
    }
    @action.bound setOverrideRefreshHandler(fn) {
        this.handleOverrideRefresh = fn;
    }
    // END TODO - remove methods above (after rewrite to React from jQuery)
}

export default Store;

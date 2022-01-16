import _ from "lodash";
import {action, observable, toJS} from "mobx";

import {
    moveArrayElementUp,
    moveArrayElementDown,
    deleteArrayElement,
} from "shared/components/EditableRowData";
import {NULL_CASE, OrderChoices, FilterLogicChoices} from "./shared";

class PlotSettingsStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
        this.settings = this.rootStore.dp.settings.plot_settings;
    }

    @observable settings = null;

    @action.bound updateFilterLogic(value) {
        this.settings.filter_logic = value;
        if (value !== FilterLogicChoices.custom) {
            this.settings.filter_query = "";
        }
        this.rootStore.resetRowOverrides();
        this.rootStore.sync();
    }
    @action.bound updateFilterQuery(value) {
        this.settings.filter_query = value;
        this.rootStore.resetRowOverrides();
        this.rootStore.sync();
    }
}
class FilterStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
        this.settings = this.rootStore.dp.settings.filters;
    }

    @observable settings = null;

    @action.bound createNew() {
        this.settings.push({
            field_name: NULL_CASE,
            quantifier: "contains",
            value: "",
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
}
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
    @action.bound updateOrder(idx, value) {
        if (value === OrderChoices.custom) {
            this.settings[idx].custom = this.getSortItems(idx);
        } else {
            this.settings[idx].custom = null;
        }
        this.settings[idx].order = value;
        this.rootStore.sync();
    }
    @action.bound changeOrder(idx, oldIndex, newIndex) {
        const items = _.cloneDeep(toJS(this.settings[idx].custom)),
            item = items.splice(oldIndex, 1)[0];
        items.splice(newIndex, 0, item);
        this.settings[idx].custom = items;
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

class Store {
    constructor(dp) {
        this.dp = dp;
        this.plotSettingsStore = new PlotSettingsStore(this);
        this.sortStore = new SortStore(this);
        this.filterStore = new FilterStore(this);
    }
    overrideRefresh = null;
    sync() {
        // sync state in store to global object - TODO - remove?
        this.dp.settings.plot_settings = toJS(this.plotSettingsStore.settings);
        this.dp.settings.filters = toJS(this.filterStore.settings);
        this.dp.settings.sorts = toJS(this.sortStore.settings);
    }
    resetRowOverrides() {
        this.dp.settings.row_overrides.forEach(v => (v.index = null));
        this.overrideRefresh();
    }
    @action.bound setOverrideRefreshHandler(fn) {
        this.overrideRefresh = fn;
    }
}

export default Store;

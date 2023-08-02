import _ from "lodash";
import {action, computed, observable} from "mobx";

class ReactiveDataStore {
    @observable data = null;
    @observable activeFilters = [];
    @computed get filteredDataStack() {
        if (!this.data) {
            return null;
        }
        let currentData = this.data,
            filteredDataStack = [currentData];
        this.activeFilters.forEach(filter => {
            currentData = filter.filter(currentData);
            filteredDataStack.push(currentData);
        });
        return filteredDataStack;
    }
    @computed get filteredData() {
        if (!this.data) {
            return null;
        }
        return this.filteredDataStack[this.filteredDataStack.length - 1];
    }
    @action.bound setData(data) {
        this.data = data;
        this.activeFilters = [];
    }
    @action.bound changeFilter(value) {
        let idx = _.findIndex(this.activeFilters, d => d.field === value.field);
        if (idx >= 0) {
            if (value.isEmpty()) {
                // delete
                this.activeFilters.splice(idx, 1);
            } else {
                // update
                this.activeFilters[idx] = value;
            }
        } else {
            // add
            this.activeFilters.push(value);
        }
    }
    getDataStack = (field, dataStack, activeFilters) => {
        const idx = _.findIndex(activeFilters, d => d.field === field);
        if (idx < 0) {
            return dataStack[dataStack.length - 1];
        }
        return dataStack[idx];
    };
}

export {ReactiveDataStore};

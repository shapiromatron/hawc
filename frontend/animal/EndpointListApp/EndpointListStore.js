import _ from "lodash";
import {action, computed, observable} from "mobx";
import h from "shared/utils/helpers";

// TODO - generalize this store; create a subclass that does this additional year filtering
// TODO - move to common components

class EndpointListStore {
    @observable config = null;
    @observable data = null;
    @observable activeFilters = [];
    constructor(config) {
        this.config = config;
        this.getDataset();
    }
    @action.bound getDataset() {
        const {data_url} = this.config;
        fetch(data_url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                json.year = _.map(json, d => {
                    const cit = d["study citation"],
                        year = cit.match(/\d{4}/);
                    d.year = year ? parseInt(year[0]) : null;
                });
                this.data = json;
            });
    }
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
}

export default EndpointListStore;

import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";
import {DataFilterStore} from "shared/dashboard/stores";
import h from "shared/utils/helpers";

const CRITICAL_VALUES = ["noel", "loel", "fel", "bmd", "bmdl"];

class EndpointListStore {
    config = null;
    @observable data = null;
    @observable settings = null;
    constructor(config) {
        this.config = config;
        this.filterStore = new DataFilterStore();
        this.setDefaultConfig();
        this.getDataset();
    }
    @computed get filteredData() {
        if (this.data === null) {
            return null;
        }
        return this.filterStore.filteredData;
    }
    @computed get plotData() {
        if (this.filteredData === null) {
            return null;
        }
        return _.chain(toJS(this.data))
            .map(d => {
                return this.settings.criticalValues.map(type => {
                    return {data: d, dose: d[type], type};
                });
            })
            .flatten()
            .filter(d => d.dose !== null && d.dose > 0)
            .sortBy("dose")
            .value();
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
                this.filterStore.setData(json);
                this.data = json;
            });
    }
    @action.bound setDefaultConfig() {
        this.settings = {
            approximateXValues: true,
            criticalValues: CRITICAL_VALUES,
        };
    }
}

export default EndpointListStore;

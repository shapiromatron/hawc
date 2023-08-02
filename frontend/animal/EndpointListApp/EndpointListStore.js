import _ from "lodash";
import {action, computed, observable} from "mobx";
import {ReactiveDataStore} from "shared/dashboard/stores";
import h from "shared/utils/helpers";

const CRITICAL_VALUES = ["noel", "loel", "fel", "bmd", "bmdl"];

class EndpointListStore {
    config = null;
    @observable data = null;
    @observable settings = null;
    constructor(config) {
        this.config = config;
        this.filterStore = new ReactiveDataStore();
        this.setDefaultConfig();
        this.getDataset();
    }
    @computed get filteredData() {
        if (this.data === null) {
            return null;
        }
        return this.filterStore.filteredData;
    }
    @action.bound getDataset() {
        const {data_url} = this.config;
        fetch(data_url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                const data = _.chain(json)
                    .map(d =>
                        this.settings.criticalValues.map(type => _.extend({type, dose: d[type]}, d))
                    )
                    .flatten()
                    .filter(d => d.dose !== null && d.dose > 0)
                    .sortBy("dose")
                    .value();
                this.filterStore.setData(data);
                this.data = data;
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

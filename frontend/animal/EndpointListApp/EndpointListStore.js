import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";

import h from "shared/utils/helpers";

class EndpointListStore {
    config = null;

    @observable rawDataset = null;

    constructor(config) {
        this.config = config;
        this.getDataset();
    }
    @computed get plottingDataset() {
        if (this.rawDataset === null) {
            return null;
        }
        return _.chain(toJS(this.rawDataset))
            .map(d => {
                return [
                    {data: d, dose: d.noel, type: "noel"},
                    {data: d, dose: d.loel, type: "loel"},
                    {data: d, dose: d.fel, type: "fel"},
                    {data: d, dose: d.bmd, type: "bmd"},
                    {data: d, dose: d.bmdl, type: "bmdl"},
                ];
            })
            .flatten()
            .filter(d => d.dose !== null && d.dose > 0)
            .sortBy("dose")
            .value();
    }

    @computed get hasDataset() {
        return this.dataset !== null;
    }
    @action.bound getDataset() {
        const {data_url} = this.config;
        fetch(data_url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.rawDataset = json;
            });
    }
}

export default EndpointListStore;

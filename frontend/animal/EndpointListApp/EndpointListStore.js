import h from "shared/utils/helpers";
import {action, computed, observable, toJS} from "mobx";

class EndpointListStore {
    config = null;

    @observable dataset = null;

    constructor(config) {
        this.config = config;
        this.getDataset();
    }

    @computed get hasDataset() {
        return this.dataset !== null;
    }
    @action.bound getDataset() {
        const {data_url} = this.config;
        fetch(data_url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.dataset = json;
            });
    }
}

export default EndpointListStore;

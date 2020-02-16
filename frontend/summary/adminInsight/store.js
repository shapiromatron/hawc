import $ from "$";
import {observable, action} from "mobx";

import {modelChoices, grouperChoices} from "./constants";

class RootStore {
    constructor() {
        this.growthStore = new GrowthStore(this);
    }
}

class GrowthStore {
    constructor(rootStore) {
        this.rootStore = rootStore;
    }

    @observable query = {
        model: modelChoices[0].id,
        grouper: grouperChoices[0].id,
    };

    @observable isFetchingPlot = false;
    @observable plotData = null;

    @action.bound changeQueryValue(field, value) {
        this.query[field] = value;
        this.fetchNewChart();
    }
    @action.bound fetchNewChart() {
        this.isFetchingPlot = true;
        this.plotData = null;
        let url = "/assessment/api/dashboard/growth/",
            params = $.param(this.query);

        fetch(`${url}?${params}`)
            .then(resp => resp.json())
            .then(json => {
                this.isFetchingPlot = false;
                this.plotData = json;
            });
    }
}

const store = new RootStore();

// singleton pattern
export default store;

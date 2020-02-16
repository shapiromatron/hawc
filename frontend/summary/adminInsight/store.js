import $ from "$";
import {observable, action} from "mobx";

import h from "shared/utils/helpers";
import {selectedModelChoices, selectedModelChoiceMap} from "./constants";

class AdminInsightStore {
    @observable selectedModel = selectedModelChoices[0].id;
    @observable isFetchingData = false;
    @observable plotData = null;
    @action.bound changeSelectedModel(newModel) {
        this.selectedModel = newModel;
        this.fetchNewChart();
    }
    @action.bound fetchNewChart() {
        this.isFetchingData = true;
        this.plotData = null;
        let url = "/assessment/api/dashboard/growth/",
            params = {model: selectedModelChoiceMap[this.selectedModel].model};

        fetch(`${url}?${$.param(params)}`)
            .then(resp => resp.json())
            .then(json => {
                this.isFetchingData = false;
                this.plotData = json;
            });
    }
}

const store = new AdminInsightStore();

// singleton pattern
export default store;

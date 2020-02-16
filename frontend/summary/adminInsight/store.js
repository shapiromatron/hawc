import {observable, action} from "mobx";

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
        let url = selectedModelChoiceMap[this.selectedModel].url;
        fetch(url)
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

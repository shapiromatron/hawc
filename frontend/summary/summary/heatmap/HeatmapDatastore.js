import {observable, action} from "mobx";

class HeatmapDatastore {
    @observable dataset = null;
    @observable settings = null;
    @observable selectedTableData = [];

    constructor(settings, dataset) {
        this.settings = settings;
        this.dataset = dataset;
    }

    @action.bound updateSelectedTableData(selectedTableData) {
        this.selectedTableData = selectedTableData;
    }
}

export default HeatmapDatastore;

import {observable, action, computed} from "mobx";

import _ from "lodash";
import h from "shared/utils/helpers";

class ExploratoryHeatmapStore {
    constructor(rootStore) {
        this.root = rootStore;
    }

    getDefaultSettings() {
        return {
            data_url: "",
            title: "",
            x_label: "",
            y_label: "",
            x_fields: [],
            y_fields: [],
            all_fields: [],
        };
    }

    @observable settings = null;
    @observable datasetOptions = null;
    @observable columnNames = null;

    @action setFromJsonSettings(settings, firstTime) {
        this.settings = settings;
        if (this.settings.data_url && firstTime) {
            this.root.base.dataUrl = this.settings.data_url;
            this.root.base.getDataset();
        }
    }

    @action.bound changeSettings(key, value) {
        this.settings[key] = value;
    }

    @action.bound changeSettingsMultiSelect(key, values) {
        // TODO - move this to a new selectmultiple component; make the select multi false by default
        let selected = _.chain(event.target.options)
            .filter(opt => opt.selected)
            .map(opt => opt.value)
            .value();

        this.settings[key] = selected;
    }

    @action.bound changeDatasetUrl(value) {
        if (this.settings.data_url === value) {
            return;
        }
        this.root.dataset = null;
        this.settings.data_url = value;
        this.root.base.dataRefreshRequired = true;
        this.root.base.dataUrl = value.length > 0 ? value : null;
    }

    @action.bound afterGetDataset() {
        this.columnNames = _.keys(this.root.base.dataset[0]);
    }

    @computed get hasSettings() {
        return this.settings !== null;
    }

    @action.bound getDatasetOptions() {
        const url = this.root.base.config.api_heatmap_datasets;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                let datasets = json.datasets;
                datasets.unshift({
                    type: "",
                    name: "<none>",
                    url: "",
                });
                datasets.forEach(d => {
                    d.label = d.type === "Dataset" ? `${d.type}: ${d.name}` : d.name;
                    d.id = d.url;
                });
                this.datasetOptions = datasets;
            })
            .catch(error => {
                this.setDataError(error);
            });
    }

    @computed get getColumnsOptions() {
        return this.columnNames.map(d => {
            return {id: d, label: d};
        });
    }
}

export default ExploratoryHeatmapStore;

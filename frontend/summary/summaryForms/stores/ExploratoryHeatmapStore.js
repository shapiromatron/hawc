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
            title: {text: "", x: 0, y: 0, rotate: 0},
            x_label: {text: "", x: 0, y: 0, rotate: 0},
            y_label: {text: "", x: 0, y: 0, rotate: 0},
            x_fields: [],
            y_fields: [],
            all_fields: [],
            padding: {top: 0, left: 0, bottom: 0, right: 0},
            cell_width: 50,
            cell_height: 50,
            x_tick_rotate: 0,
            y_tick_rotate: 0,
            color_range: ["white", "green"],
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

    @action.bound changeSettings(path, value) {
        _.set(this.settings, path, value);
    }

    @action.bound changeSettingsMultiSelect(key, values) {
        // TODO HEATMAP - create new SelectMultiple; remove Select multi={true/false} property
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

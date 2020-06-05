import {observable, action, computed} from "mobx";

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
        };
    }

    @observable settings = null;
    @observable datasetOptions = null;

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

    @action.bound changeDatasetUrl(value) {
        if (this.settings.data_url === value) {
            return;
        }
        this.root.dataset = null;
        this.settings.data_url = value;
        this.root.base.dataRefreshRequired = true;
        this.root.base.dataUrl = value.length > 0 ? value : null;
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
}

export default ExploratoryHeatmapStore;

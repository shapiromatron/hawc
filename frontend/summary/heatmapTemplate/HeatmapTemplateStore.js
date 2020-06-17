import h from "shared/utils/helpers";
import {action, computed, observable} from "mobx";

class HeatmapTemplateStore {
    config = null;

    @observable settings = null;
    @observable dataset = null;

    constructor(config) {
        this.config = config;
        this.settings = this.getDefaultSettings();
    }

    getDefaultSettings() {
        return {
            cell_height: 25,
            cell_width: 75,
            hawc_interactivity: true,
            color_range: ["#ffffff", "#2339a9"],
            data_url: this.config.data_url,
            filter_widgets: [
                {column: "study citation", delimiter: "", on_click_event: "study"},
                {column: "experiment name", delimiter: "", on_click_event: "experiment"},
            ],
            padding: {top: 30, left: 30, bottom: 30, right: 30},
            table_fields: [
                {column: "study citation", on_click_event: "study"},
                {column: "experiment name", on_click_event: "experiment"},
                {column: "species", on_click_event: "animal_group"},
                {column: "strain", on_click_event: "---"},
                {column: "system", on_click_event: "---"},
                {column: "organ", on_click_event: "---"},
                {column: "effect", on_click_event: "---"},
                {column: "endpoint name", on_click_event: "endpoint_complete"},
            ],
            title: {text: "Endpoint summary", x: 0, y: 0, rotate: 0},
            x_fields: [
                {column: "species", delimiter: ""},
                {column: "sex", delimiter: ""},
            ],
            x_label: {text: "Species and Sex", x: 0, y: 0, rotate: 0},
            x_tick_rotate: 0,
            y_fields: [{column: "system", delimiter: ""}],
            y_label: {text: "System", x: 0, y: 0, rotate: -90},
            y_tick_rotate: 0,
            show_grid: true,
            show_axis_border: true,
            show_tooltip: true,
            compress_y: true,
        };
    }

    @action.bound setDataset(dataset) {
        this.dataset = dataset;
    }

    @computed get settingsHash() {
        return h.hashString(this.settings);
    }
}

export default HeatmapTemplateStore;

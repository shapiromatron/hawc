import _ from "lodash";
import h from "shared/utils/helpers";
import {action, computed, observable, toJS} from "mobx";

import {AXIS_OPTIONS, FILTER_OPTIONS, TABLE_FIELDS} from "./constants";

class HeatmapTemplateStore {
    config = null;

    @observable dataset = null;
    @observable filterOptions = [];
    @observable axisOptions = [];

    @observable selectedXAxis = null;
    @observable selectedYAxis = null;
    @observable selectedFilters = [];

    constructor(config) {
        this.config = config;
        this.axisOptions = AXIS_OPTIONS.filter(d => _.includes(d.data_classes, config.data_class));
        this.filterOptions = FILTER_OPTIONS.filter(d =>
            _.includes(d.data_classes, config.data_class)
        );
        this.selectedXAxis = this.axisOptions[0];
        this.selectedYAxis = this.axisOptions[1];
        this.selectedFilters = this.filterOptions.slice(0, 3);
    }

    @action.bound changeAxis(name, key) {
        const item = _.find(this.axisOptions, {id: key});
        if (name === "selectedXAxis") {
            this.selectedXAxis = item;
        } else if (name === "selectedYAxis") {
            this.selectedYAxis = item;
        }
    }

    @action.bound changeSelectedFilters(values) {
        this.selectedFilters = values.map(value => _.find(this.filterOptions, {id: value}));
    }

    @action.bound setDataset(dataset) {
        this.dataset = dataset;
    }

    @computed get settings() {
        return {
            cell_height: 25,
            cell_width: 75,
            hawc_interactivity: true,
            color_range: ["#ffffff", "#2339a9"],
            data_url: this.config.data_url,
            filter_widgets: toJS(this.selectedFilters.map(d => d.settings)),
            padding: {top: 30, left: 30, bottom: 30, right: 30},
            table_fields: TABLE_FIELDS[this.config.data_class],
            title: {text: this.config.title, x: 0, y: 0, rotate: 0},
            x_fields: toJS(this.selectedXAxis.settings),
            x_label: {text: this.selectedXAxis.label, x: 0, y: 0, rotate: 0},
            x_tick_rotate: 0,
            y_fields: toJS(this.selectedYAxis.settings),
            y_label: {text: this.selectedYAxis.label, x: 0, y: 0, rotate: -90},
            y_tick_rotate: 0,
            show_grid: true,
            show_axis_border: true,
            show_tooltip: true,
            compress_y: true,
        };
    }

    @computed get settingsHash() {
        return h.hashString(this.settings);
    }
}

export default HeatmapTemplateStore;

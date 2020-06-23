import _ from "lodash";
import h from "shared/utils/helpers";
import {action, computed, observable, toJS} from "mobx";

import {AXIS_OPTIONS, FILTER_OPTIONS, TABLE_FIELDS, DASHBOARDS} from "./constants";

class HeatmapTemplateStore {
    config = null;

    @observable dataset = null;
    @observable dashboardOptions = [];
    @observable filterOptions = [];
    @observable axisOptions = [];

    @observable selectedDashboard = null;
    @observable selectedXAxis = null;
    @observable selectedYAxis = null;
    @observable selectedFilters = [];

    constructor(config) {
        this.config = config;
        this.dashboardOptions = DASHBOARDS.filter(d => d.data_class === config.data_class);
        this.axisOptions = AXIS_OPTIONS.filter(d => _.includes(d.data_classes, config.data_class));
        this.filterOptions = FILTER_OPTIONS.filter(d =>
            _.includes(d.data_classes, config.data_class)
        );
        this.changeDashboard(this.dashboardOptions[0].id);
    }

    @action.bound changeDashboard(id) {
        const dashboard = _.find(this.dashboardOptions, {id});
        this.selectedDashboard = dashboard;
        this.selectedXAxis = _.find(this.axisOptions, {id: dashboard.x_axis});
        this.selectedYAxis = _.find(this.axisOptions, {id: dashboard.y_axis});
        this.selectedFilters = dashboard.filters.map(id => _.find(this.filterOptions, {id}));
    }

    @action.bound changeAxis(name, key) {
        const item = _.find(this.axisOptions, {id: key});
        if (name === "selectedXAxis") {
            this.selectedXAxis = item;
        } else if (name === "selectedYAxis") {
            this.selectedYAxis = item;
        }
    }

    @action.bound flipAxes() {
        const temp = this.selectedXAxis;
        this.selectedXAxis = this.selectedYAxis;
        this.selectedYAxis = temp;
    }

    @action.bound changeSelectedFilters(values) {
        this.selectedFilters = values.map(value => _.find(this.filterOptions, {id: value}));
    }

    @action.bound setDataset(dataset) {
        this.dataset = dataset;
    }

    @computed get settings() {
        const title = `${this.config.assessment}: ${this.selectedDashboard.label}`;
        return {
            autosize_cells: true,
            autorotate_tick_labels: true,
            cell_height: 25,
            cell_width: 75,
            color_range: ["#ffffff", "#2339a9"],
            compress_x: true,
            compress_y: true,
            data_url: this.config.data_url,
            filter_widgets: this.selectedFilters.map(d => d.settings),
            hawc_interactivity: true,
            padding: {top: 30, left: 30, bottom: 30, right: 30},
            show_axis_border: true,
            show_grid: true,
            show_tooltip: true,
            table_fields: TABLE_FIELDS[this.config.data_class],
            title: {text: title, x: 0, y: 0, rotate: 0},
            x_fields: this.selectedXAxis.settings,
            x_label: {text: this.selectedXAxis.label, x: 0, y: 0, rotate: 0},
            x_tick_rotate: 0,
            y_fields: this.selectedYAxis.settings,
            y_label: {text: this.selectedYAxis.label, x: 0, y: 0, rotate: -90},
            y_tick_rotate: 0,
        };
    }

    @computed get settingsHash() {
        return h.hashString(JSON.stringify(toJS(this.settings)));
    }
}

export default HeatmapTemplateStore;

import _ from "lodash";
import h from "shared/utils/helpers";
import {action, computed, observable, toJS} from "mobx";

import {OPTIONS} from "./constants";

class HeatmapTemplateStore {
    config = null;

    @observable dataset = null;
    @observable dashboardOptions = [];
    @observable filterOptions = [];
    @observable axisOptions = [];
    @observable tableOptions = [];

    @observable selectedDashboard = null;
    @observable selectedXAxis = null;
    @observable selectedYAxis = null;
    @observable selectedFilters = [];
    @observable selectedTableFields = [];

    constructor(config) {
        this.config = config;
        const options = OPTIONS[config.data_class];
        this.dashboardOptions = options.DASHBOARDS;
        this.axisOptions = options.AXIS_OPTIONS;
        this.filterOptions = options.FILTER_OPTIONS;
        this.tableOptions = options.TABLE_FIELDS;
        this.changeDashboard(this.dashboardOptions[0].id);
    }

    @action.bound changeDashboard(id) {
        const dashboard = _.find(this.dashboardOptions, {id});
        this.selectedDashboard = dashboard;
        this.selectedXAxis = _.find(this.axisOptions, {id: dashboard.x_axis});
        this.selectedYAxis = _.find(this.axisOptions, {id: dashboard.y_axis});
        this.selectedFilters = dashboard.filters.map(id => _.find(this.filterOptions, {id}));
        this.selectedTableFields = dashboard.table_fields.map(id =>
            _.find(this.tableOptions, {id})
        );
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

    @action.bound changeSelectedTableFields(values) {
        this.selectedTableFields = values.map(value => _.find(this.tableOptions, {id: value}));
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
            table_fields: this.selectedTableFields.map(d => d.settings),
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

import {observable, action, computed} from "mobx";

import _ from "lodash";
import h from "shared/utils/helpers";
import {NULL_VALUE} from "../../summary/constants";
import {DATA_FILTER_CONTAINS, DATA_FILTER_LOGIC_AND} from "../../summary/filters";
import DataPivotExtension from "summary/dataPivot/DataPivotExtension";
import {
    moveArrayElementUp,
    moveArrayElementDown,
    deleteArrayElement,
} from "shared/components/EditableRowData";

let createDefaultAxisItem = function() {
        return {column: NULL_VALUE, wrap_text: 0, delimiter: ""};
    },
    createDefaultFilterWidget = function() {
        return {column: NULL_VALUE, header: "", delimiter: "", on_click_event: NULL_VALUE};
    },
    createTableRow = function() {
        return {column: NULL_VALUE, header: "", delimiter: "", on_click_event: NULL_VALUE};
    },
    createFilterRow = function() {
        return {column: NULL_VALUE, type: DATA_FILTER_CONTAINS, value: ""};
    };

class ExploratoryHeatmapStore {
    constructor(rootStore) {
        this.root = rootStore;
    }

    getDefaultSettings() {
        return {
            cell_height: 50,
            cell_width: 50,
            color_range: [h.COLORS.WHITE, h.COLORS.BLUE],
            compress_x: false,
            compress_y: false,
            data_url: "",
            hawc_interactivity: true,
            filter_widgets: [],
            padding: {top: 30, left: 30, bottom: 30, right: 30},
            show_axis_border: true,
            show_grid: true,
            show_tooltip: true,
            show_totals: true,
            show_null: true,
            autosize_cells: true,
            autorotate_tick_labels: true,
            filters: [],
            filtersLogic: DATA_FILTER_LOGIC_AND,
            table_fields: [
                createTableRow(),
                createTableRow(),
                createTableRow(),
                createTableRow(),
                createTableRow(),
            ],
            title: {text: "", x: 0, y: 0, rotate: 0},
            x_fields: [createDefaultAxisItem()],
            x_label: {text: "", x: 0, y: 0, rotate: 0},
            x_tick_rotate: 0,
            y_fields: [createDefaultAxisItem()],
            y_label: {text: "", x: 0, y: 0, rotate: 0},
            y_tick_rotate: -90,
            x_axis_bottom: true,
        };
    }

    @observable settings = null;
    @observable datasetOptions = null;
    @observable columnNames = null;
    @observable dpeOptions = [];

    @action.bound moveArrayElementUp(key, index) {
        const arr = _.cloneDeep(this.settings[key]);
        moveArrayElementUp(arr, index);
        this.settings[key] = arr;
    }

    @action.bound moveArrayElementDown(key, index) {
        const arr = _.cloneDeep(this.settings[key]);
        moveArrayElementDown(arr, index);
        this.settings[key] = arr;
    }

    @action.bound deleteArrayElement(key, index) {
        const arr = this.settings[key];
        deleteArrayElement(arr, index);
        this.settings[key] = arr;
    }

    @action.bound createNewAxisLabel(key) {
        this.settings[key].push(createDefaultAxisItem());
    }

    @action.bound createNewFilter() {
        this.settings.filters.push(createFilterRow());
    }

    @action.bound createNewFilterWidget() {
        this.settings.filter_widgets.push(createDefaultFilterWidget());
    }

    @action.bound createNewTableRow() {
        this.settings.table_fields.push(createTableRow());
    }

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

    @action.bound changeArraySettings(arrayKey, index, key, value) {
        this.settings[arrayKey][index][key] = value;
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
        if (this.settings.hawc_interactivity) {
            this.dpeOptions = DataPivotExtension.values.filter(d =>
                _.includes(this.columnNames, d._dpe_key)
            );
        }
    }

    @computed get getDpeSettings() {
        let options = this.dpeOptions.map(d => {
            return {id: d._dpe_name, label: d._dpe_option_txt};
        });
        options.unshift({id: NULL_VALUE, label: "<none>"});
        return options;
    }

    @computed get hasSettings() {
        return this.settings !== null;
    }

    @action.bound getDatasetOptions() {
        const url = this.root.base.config.api_heatmap_datasets;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                let datasets = json.datasets.map(d => {
                    return {id: d.url, label: d.name};
                });
                datasets.unshift({
                    id: NULL_VALUE,
                    label: "<none>",
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

    @computed get getColumnsOptionsWithNull() {
        let columns = [...this.getColumnsOptions]; // shallow-copy
        columns.unshift({id: NULL_VALUE, label: "<none>"});
        return columns;
    }

    @observable visualCustomizationPanelActiveTab = 0;
    @action.bound changeActiveVisualCustomizationTab(index) {
        this.visualCustomizationPanelActiveTab = index;
        return true;
    }
}

export default ExploratoryHeatmapStore;

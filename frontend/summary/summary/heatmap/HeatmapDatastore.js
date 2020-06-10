import _ from "lodash";
import {observable, action, toJS} from "mobx";

import HAWCModal from "utils/HAWCModal";

class HeatmapDatastore {
    @observable dataset = null;
    @observable settings = null;
    @observable selectedTableData = [];
    @observable intersection = null;
    @observable filterWidgetState = null;

    constructor(settings, dataset) {
        this.modal = new HAWCModal();
        this.settings = settings;
        this.dataset = dataset;
        this.intersection = this.setIntersection();
        this.filterWidgetState = this.setFilterWidgetState();
    }

    setIntersection() {
        /*
        here, we have "red" in the color column with element index 1, 2, and 3
        intersection["color"]["red"] = Set([1,2,3])
        */
        let intersection = {},
            addColumnsToMap = row => {
                const columnName = row.column,
                    delimiter = row.delimiter;
                // create column array if needed
                if (intersection[columnName] === undefined) {
                    intersection[columnName] = {};
                }
                this.dataset.forEach((d, idx) => {
                    const values =
                        delimiter !== "" ? d[columnName].split(delimiter) : [d[columnName]];
                    for (let value of values) {
                        if (intersection[columnName][value] === undefined) {
                            intersection[columnName][value] = [];
                        }
                        intersection[columnName][value].push(idx);
                    }
                });
            };

        this.settings.x_fields_new.map(addColumnsToMap);
        this.settings.y_fields_new.map(addColumnsToMap);
        this.settings.filter_widgets.map(addColumnsToMap);

        // convert arrays to Sets
        _.each(intersection, (dataColumn, columnName) => {
            _.each(dataColumn, (rows, value) => {
                dataColumn[value] = new Set(rows);
            });
        });

        return intersection;
    }

    setFilterWidgetState() {
        let state = {};
        _.each(this.intersection, (items, column) => {
            state[column] = {};
            _.each(items, (value, key) => (state[column][key] = true));
        });
        return state;
    }

    @action.bound updateSelectedTableData(selectedTableData) {
        this.selectedTableData = selectedTableData;
    }

    @action.bound selectAllFilterWidget(column) {
        const keys = _.keys(toJS(this.filterWidgetState[column]));
        keys.forEach(item => {
            this.filterWidgetState[column][item] = true;
        });
    }
    @action.bound selectNoneFilterWidget(column) {
        const keys = _.keys(toJS(this.filterWidgetState[column]));
        keys.forEach(item => {
            this.filterWidgetState[column][item] = false;
        });
    }
    @action.bound showFilterWidgetModal(column, item) {
        console.log("showFilterWidgetModal", column, item);
    }
    @action.bound toggleItemSelection(column, item, visible) {
        this.filterWidgetState[column][item] = visible;
    }
}

export default HeatmapDatastore;

import _ from "lodash";
import {observable, computed, action, toJS} from "mobx";

import h from "shared/utils/helpers";

import HAWCModal from "utils/HAWCModal";

class HeatmapDatastore {
    scales = null;
    intersection = null;
    matrixDatasetCache = {};

    @observable dataset = null;
    @observable settings = null;
    @observable selectedTableData = [];
    @observable filterWidgetState = null;

    constructor(settings, dataset) {
        this.modal = new HAWCModal();
        this.settings = settings;
        this.dataset = dataset;
        this.intersection = this.setIntersection();
        this.filterWidgetState = this.setFilterWidgetState();
        this.scales = this.setScales();
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

    setScales() {
        const setScales = function(fields, intersection) {
            const columns = fields.map(field => field.column),
                items = columns.map(column => _.keys(intersection[column])),
                permutations = h.cartesian(items);

            if (columns.length <= 1) {
                return permutations.map(item => {
                    return {
                        [columns[0]]: item,
                    };
                });
            } else {
                return permutations.map(permutation => {
                    return _.zipObject(columns, permutation);
                });
            }
        };
        const x = setScales(toJS(this.settings.x_fields_new), toJS(this.intersection)),
            y = setScales(toJS(this.settings.y_fields_new), toJS(this.intersection));

        return {x, y};
    }

    @computed
    get getFilterHash() {
        return h.hashString(JSON.stringify(toJS(this.filterWidgetState)));
    }

    @computed
    get rowsRemovedByFilters() {
        // returns a Set of row indexes to remove
        let removedRows = new Set(),
            i;
        const {intersection} = this;
        _.each(this.filterWidgetState, (items, column) => {
            _.each(items, (include, name) => {
                if (include === false) {
                    for (i of intersection[column][name]) {
                        removedRows.add(i);
                    }
                }
            });
        });
        return removedRows;
    }

    @computed
    get matrixDataset() {
        // build the dataset required to generate the matrix
        const hash = this.getFilterHash;
        if (this.matrixDatasetCache[hash]) {
            // already computed; grab from cache
            return this.matrixDatasetCache[hash];
        }
        // we need to compute again
        let {scales, intersection} = this,
            removedRows = this.rowsRemovedByFilters,
            getIntersection = function(arr, set2) {
                return arr.filter(x => set2.has(x));
            },
            getRows = filters => {
                let rows;
                _.each(_.keys(filters), (columnName, idx) => {
                    if (idx === 0) {
                        rows = [...intersection[columnName][filters[columnName]]];
                    } else {
                        rows = getIntersection(rows, intersection[columnName][filters[columnName]]);
                    }
                });
                return h.setDifference(rows, removedRows);
            },
            xy_map = scales.x
                .map((x, i) => {
                    return scales.y.map((y, j) => {
                        return {
                            x_filter: x,
                            y_filter: y,
                            x_step: i,
                            y_step: j,
                            rows: getRows(Object.assign({}, x, y)),
                        };
                    });
                })
                .flat();
        this.matrixDatasetCache[hash] = xy_map;
        return xy_map;
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

    @action.bound toggleItemSelection(column, item, visible) {
        this.filterWidgetState[column][item] = visible;
    }
}

export default HeatmapDatastore;

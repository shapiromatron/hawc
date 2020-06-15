import _ from "lodash";
import d3 from "d3";
import {observable, computed, action, toJS} from "mobx";

import h from "shared/utils/helpers";

import HAWCModal from "utils/HAWCModal";

import DataPivotExtension from "summary/dataPivot/DataPivotExtension";

class HeatmapDatastore {
    scales = null;
    totals = null;
    intersection = null;
    matrixDatasetCache = {};
    dpe = null;
    colorScale = null;
    maxValue = null;

    @observable dataset = null;
    @observable settings = null;
    @observable selectedTableData = [];
    @observable filterWidgetState = null;
    @observable tableDataFilters = null;

    constructor(settings, dataset) {
        this.getDetailUrl = this.getDetailUrl.bind(this);
        this.modal = new HAWCModal();
        this.settings = settings;
        this.dataset = dataset;
        this.dpe = new DataPivotExtension();
        this.intersection = this.setIntersection();
        this.filterWidgetState = this.setFilterWidgetState();
        this.scales = this.setScales();
        this.totals = this.setTotals();
        this.setColorScale();
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

        this.settings.x_fields.map(addColumnsToMap);
        this.settings.y_fields.map(addColumnsToMap);
        this.settings.filter_widgets.map(addColumnsToMap);

        // convert arrays to Sets
        _.each(_.values(intersection), dataColumn => {
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

            if (columns.length === 0) {
                return {};
            } else if (columns.length === 1) {
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

        const x = setScales(toJS(this.settings.x_fields), toJS(this.intersection)),
            y = setScales(toJS(this.settings.y_fields), toJS(this.intersection));

        return {x, y};
    }

    setTotals() {
        // set grand totals for all x and y items, indexed based
        const setGrandTotals = (intersection, scale) => {
                return scale
                    .map(d => {
                        let rows,
                            first = true;
                        _.each(d, (val, keys, idx) => {
                            rows = first
                                ? intersection[keys][val]
                                : h.setIntersection(rows, intersection[keys][val]);
                            first = false;
                        });
                        return rows;
                    })
                    .map(d => {
                        return d.size;
                    });
            },
            x = setGrandTotals(toJS(this.intersection), this.scales.x),
            y = setGrandTotals(toJS(this.intersection), this.scales.y);

        return {x, y};
    }

    setColorScale() {
        this.maxValue = d3.max(this.matrixDataset, d => d.rows.length);
        this.colorScale = d3.scale
            .linear()
            .domain([0, this.maxValue])
            .range(this.settings.color_range);
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
            index = -1,
            removedRows = this.rowsRemovedByFilters,
            getIntersection = (arr, set2) => arr.filter(x => set2.has(x)),
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
            {compress_x, compress_y} = this.settings,
            xy_map = scales.x
                .filter((d, i) => (compress_x ? this.totals.x[i] > 0 : true))
                .map((x, i) => {
                    return scales.y
                        .filter((d, i) => (compress_y ? this.totals.y[i] > 0 : true))
                        .map((y, j) => {
                            index += 1;
                            return {
                                index,
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

    @computed
    get getTableData() {
        let rows;
        if (this.tableDataFilters) {
            rows = _.find(this.matrixDataset, {
                x_step: this.tableDataFilters.x_step,
                y_step: this.tableDataFilters.y_step,
            }).rows;
        } else {
            rows = [
                ...h.setDifference(
                    new Set(_.range(this.dataset.length)),
                    this.rowsRemovedByFilters
                ),
            ];
        }
        return rows.map(index => this.dataset[index]);
    }

    @action.bound updateTableDataFilters(d) {
        this.tableDataFilters = d;
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

    @action.bound showModalClick(on_click_event, column, item) {
        let row = _.find(this.dataset, {[column]: item}),
            extension = _.find(DataPivotExtension.values, {_dpe_name: on_click_event});
        // TODO HEATMAP - handle case where row ids are non-unique
        this.dpe.render_plottip(extension, row);
    }

    getDetailUrl(on_click_event, row) {
        let extension = _.find(DataPivotExtension.values, {_dpe_name: on_click_event});
        return this.dpe.get_detail_url(extension, row);
    }
}

export default HeatmapDatastore;

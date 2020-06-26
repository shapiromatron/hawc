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
    @observable tableDataFilters = new Set();

    constructor(settings, dataset) {
        this.getDetailUrl = this.getDetailUrl.bind(this);
        this.modal = new HAWCModal();
        this.settings = settings;
        this.dataset = this.setDataset(dataset);
        this.dpe = new DataPivotExtension();
        this.intersection = this.setIntersection();
        this.filterWidgetState = this.setFilterWidgetState();
        this.scales = this.setScales();
        this.totals = this.setTotals();
        this.setColorScale();
    }

    setDataset(dataset) {
        if (this.settings.show_null) {
            return dataset;
        } else {
            let x_fields = toJS(this.settings.x_fields),
                y_fields = toJS(this.settings.y_fields);
            return dataset.filter(row => {
                for (const field of [...x_fields, ...y_fields]) {
                    if (!row[field.column]) {
                        return false;
                    }
                }
                return true;
            });
        }
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
                    // get column value or empty string to handle null or undefined edge cases,
                    // such as when an epi outcome is created but with no associated exposure.
                    const text = d[columnName] || "",
                        values = delimiter ? text.split(delimiter) : [text];

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
        const setScales = (fields, intersection) => {
            const columns = fields.map(field => field.column),
                items = columns.map(column => _.keys(intersection[column]).sort()),
                permutations = h.cartesian(items);
            if (columns.length == 0) {
                return [];
            } else if (columns.length == 1) {
                return permutations.map(item => {
                    return [{column: columns[0], value: item}];
                });
            } else {
                return permutations.map(permutation => {
                    return _.zipWith(columns, permutation, (c, p) => {
                        return {column: c, value: p};
                    });
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
                        _.each(d, e => {
                            rows = first
                                ? intersection[e.column][e.value]
                                : h.setIntersection(rows, intersection[e.column][e.value]);
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
        this.maxValue = d3.max(this.matrixDataset, d => (d.type == "cell" ? d.rows.length : 0));
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
        let removedRows = [];
        const {intersection} = this;
        _.each(this.filterWidgetState, (items, column) => {
            let removed = [],
                included = [];
            _.each(items, (include, name) => {
                if (include === false) {
                    removed.push(...intersection[column][name]);
                } else {
                    included.push(...intersection[column][name]);
                }
            });
            removedRows.push(..._.without(removed, ...included));
        });
        return new Set(removedRows);
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
            getIntersection = function(arr, set2) {
                return arr.filter(x => set2.has(x));
            },
            getRows = filters => {
                let rows;
                _.each(filters, (filter, idx) => {
                    if (idx == 0) {
                        rows = [...intersection[filter.column][filter.value]];
                    } else {
                        rows = getIntersection(rows, intersection[filter.column][filter.value]);
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
                                type: "cell",
                                x_filters: x,
                                y_filters: y,
                                x_step: i,
                                y_step: j,
                                rows: getRows(x.concat(y)),
                            };
                        });
                })
                .flat();
        if (this.settings.show_totals) {
            const x_steps = scales.x.filter((d, i) => (compress_x ? this.totals.x[i] > 0 : true))
                    .length,
                y_steps = scales.y.filter((d, i) => (compress_y ? this.totals.y[i] > 0 : true))
                    .length;
            xy_map.push(
                ...scales.x
                    .filter((d, i) => (compress_x ? this.totals.x[i] > 0 : true))
                    .map((x, i) => {
                        index += 1;
                        return {
                            index,
                            type: "total",
                            x_filters: x,
                            y_filters: [],
                            x_step: i,
                            y_step: y_steps,
                            rows: getRows(x),
                        };
                    }),
                ...scales.y
                    .filter((d, i) => (compress_y ? this.totals.y[i] > 0 : true))
                    .map((y, i) => {
                        index += 1;
                        return {
                            index,
                            type: "total",
                            x_filters: [],
                            y_filters: y,
                            x_step: x_steps,
                            y_step: i,
                            rows: getRows(y),
                        };
                    }),
                {
                    index: ++index,
                    type: "total",
                    x_filters: [],
                    y_filters: [],
                    x_step: x_steps,
                    y_step: y_steps,
                    rows: h.setDifference(
                        new Set(_.range(this.dataset.length)),
                        this.rowsRemovedByFilters
                    ),
                }
            );
        }
        this.matrixDatasetCache[hash] = xy_map;
        return xy_map;
    }

    @computed
    get getTableData() {
        let rows;
        if (this.tableDataFilters.size > 0) {
            let all_rows = [...this.tableDataFilters].map(
                d => _.find(this.matrixDataset, {x_step: d.x_step, y_step: d.y_step}).rows
            );
            rows = _.union(...all_rows);
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

    @action.bound setTableDataFilters(d) {
        if (d instanceof Set) this.tableDataFilters = d;
        else {
            this.tableDataFilters.clear();
            this.tableDataFilters.add(d);
        }
    }

    @action.bound addTableDataFilters(d) {
        this.tableDataFilters.add(d);
    }

    @action.bound deleteTableDataFilters(d) {
        this.tableDataFilters.delete(d);
    }

    @action.bound toggleTableDataFilters(d) {
        let value = this.tableDataFilters.delete(d);
        if (!value) this.tableDataFilters.add(d);
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

    @action.bound showModalClick(on_click_event, row) {
        let extension = _.find(DataPivotExtension.values, {_dpe_name: on_click_event});
        this.dpe.render_plottip(extension, row);
    }

    getDetailUrl(on_click_event, row) {
        let extension = _.find(DataPivotExtension.values, {_dpe_name: on_click_event});
        return this.dpe.get_detail_url(extension, row);
    }
}

export default HeatmapDatastore;

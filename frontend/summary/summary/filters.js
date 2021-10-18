import _ from "lodash";

import {NULL_VALUE} from "./constants";
import Query from "shared/parsers/query";

export const DATA_FILTER_CONTAINS = "contains",
    DATA_FILTER_OPTIONS = [
        {id: "gt", label: ">"},
        {id: "gte", label: "≥"},
        {id: "lt", label: "<"},
        {id: "lte", label: "≤"},
        {id: "exact", label: "exact"},
        {id: DATA_FILTER_CONTAINS, label: "contains"},
        {id: "not_contains", label: "does not contain"},
    ],
    DATA_FILTER_LOGIC_AND = "and",
    DATA_FILTER_LOGIC_OR = "or",
    DATA_FILTER_LOGIC_CUSTOM = "custom",
    DATA_FILTER_LOGIC_OPTIONS = [
        {id: DATA_FILTER_LOGIC_AND, label: "AND"},
        {id: DATA_FILTER_LOGIC_OR, label: "OR"},
        {id: DATA_FILTER_LOGIC_CUSTOM, label: "CUSTOM"},
    ],
    filterFunction = function(filterType) {
        switch (filterType) {
            case "lt":
                return (val, target) => val < target;
            case "lte":
                return (val, target) => val <= target;
            case "gt":
                return (val, target) => val > target;
            case "gte":
                return (val, target) => val >= target;
            case "contains":
                return (val, target) =>
                    val &&
                    val
                        .toString()
                        .toLowerCase()
                        .includes(target.toString().toLowerCase());
            case "not_contains":
                return (val, target) =>
                    _.isEmpty(val) ||
                    !val
                        .toString()
                        .toLowerCase()
                        .includes(target.toString().toLowerCase());
            case "exact":
                return (val, target) => val == target;
            default:
                console.error(`Unrecognized filter: ${filterType}`);
        }
    },
    normalizeTargetValue = function(filter) {
        switch (filter.type) {
            case "contains":
            case "not_contains":
                return filter.value.toString().toLowerCase();
            case "gt":
            case "gte":
            case "lt":
            case "lte":
                return parseFloat(filter.value);
            case "exact":
                return filter.value;
            default:
                console.error(`Unrecognized filter: ${filter.type}`);
        }
    },
    applyRowFilters = function(arr, filters, filter_logic, filter_string) {
        if (filters.length === 0 || arr.length == 0) {
            return arr;
        }

        let includes = new Set(),
            excludes = new Set();
        if (filter_logic === DATA_FILTER_LOGIC_AND) {
            includes = new Set(_.range(arr.length));
        } else if (filter_logic === DATA_FILTER_LOGIC_OR) {
            excludes = new Set(_.range(arr.length));
        } else if (filter_logic === DATA_FILTER_LOGIC_CUSTOM) {
            let getValue = i => {
                    i -= 1; // i uses 1 based indexing
                    let filter = filters[i];
                    if (filter.column === NULL_VALUE) {
                        return arr;
                    }
                    let target = normalizeTargetValue(filter),
                        func = filterFunction(filter.type);
                    if (func) {
                        return arr.filter(e => func(e[filter.column], target));
                    } else {
                        console.error(`Unrecognized filter: ${filter.type}`);
                    }
                },
                negateValue = v => _.difference(arr, v),
                andValues = (l, r) => _.intersection(l, r),
                orValues = (l, r) => _.union(l, r);
            return Query.parse(filter_string, {getValue, negateValue, andValues, orValues});
        } else {
            console.error(`Unrecognized filter_logic: ${filter_logic}`);
        }

        filters
            .filter(d => d.column !== NULL_VALUE)
            .forEach(filter => {
                let target = normalizeTargetValue(filter),
                    func = filterFunction(filter.type);

                if (func) {
                    if (filter_logic === DATA_FILTER_LOGIC_AND) {
                        includes.forEach(i => {
                            if (!func(arr[i][filter.column], target)) {
                                includes.delete(i);
                            }
                        });
                    } else {
                        excludes.forEach(i => {
                            if (func(arr[i][filter.column], target)) {
                                excludes.delete(i);
                                includes.add(i);
                            }
                        });
                    }
                } else {
                    console.error(`Unrecognized filter: ${filter.type}`);
                }
            });
        return arr.filter((_, i) => includes.has(i));
    };

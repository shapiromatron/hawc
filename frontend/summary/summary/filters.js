import _ from "lodash";

import {NULL_VALUE} from "./constants";

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
    DATA_FILTER_LOGIC_OPTIONS = [
        {id: DATA_FILTER_LOGIC_AND, label: "AND"},
        {id: DATA_FILTER_LOGIC_OR, label: "OR"},
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
    applyRowFilters = function(arr, filters, filter_logic) {
        if (filters.length === 0 || arr.length == 0) {
            return arr;
        }

        let includes = new Set(),
            excludes = new Set();
        if (filter_logic === DATA_FILTER_LOGIC_AND) {
            includes = new Set(_.range(arr.length));
        } else {
            excludes = new Set(_.range(arr.length));
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
                    } else if (filter_logic === DATA_FILTER_LOGIC_OR) {
                        excludes.forEach(i => {
                            if (func(arr[i][filter.column], target)) {
                                excludes.delete(i);
                                includes.add(i);
                            }
                        });
                    } else {
                        console.error(`Unrecognized filter_logic: ${filter_logic}`);
                    }
                } else {
                    console.error(`Unrecognized filter: ${filter.type}`);
                }
            });
        return arr.filter((_, i) => includes.has(i));
    };

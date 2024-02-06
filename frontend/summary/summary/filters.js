import _ from "lodash";
import Query from "shared/parsers/query";

import {NULL_VALUE} from "./constants";

export const DATA_FILTER_CONTAINS = "contains",
    DATA_FILTER_OPTIONS = [
        {id: DATA_FILTER_CONTAINS, label: "contains"},
        {id: "not_contains", label: "does not contain"},
        {id: "exact", label: "exact"},
        {id: "gt", label: ">"},
        {id: "gte", label: "≥"},
        {id: "lt", label: "<"},
        {id: "lte", label: "≤"},
    ],
    DATA_FILTER_LOGIC_AND = "and",
    DATA_FILTER_LOGIC_OR = "or",
    DATA_FILTER_LOGIC_CUSTOM = "custom",
    DATA_FILTER_LOGIC_OPTIONS = [
        {id: DATA_FILTER_LOGIC_AND, label: "AND"},
        {id: DATA_FILTER_LOGIC_OR, label: "OR"},
        {id: DATA_FILTER_LOGIC_CUSTOM, label: "CUSTOM"},
    ],
    filterLogicHelpText =
        "Should multiple filter criteria be required for ALL rows (AND), ANY row (OR), or a custom query?",
    filterQueryHelpText =
        "Custom query using criteria row # and logic operators; e.g., 1 AND (2 OR 3) AND NOT 4",
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
            case DATA_FILTER_CONTAINS:
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
    applyCustomQueryFilters = function(arr, filters, filter_query) {
        let getValue = i => {
                let filter = filters[i - 1]; // convert 1 to 0 indexing
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
        try {
            return Query.parse(filter_query, {getValue, negateValue, andValues, orValues});
        } catch (err) {
            console.error(err);
            return [];
        }
    },
    readableCustomQueryFilters = function(filters, filter_query) {
        let getValue = i => {
                let filter = filters[i - 1]; // convert 1 to 0 indexing
                return `"${filter.column}"[${filter.type}]"${filter.value}"{${i}}`;
            },
            negateValue = v => {
                return ["NOT", v];
            },
            andValues = (l, r) => {
                return [l, "AND", r];
            },
            orValues = (l, r) => {
                return [l, "OR", r];
            },
            stringify = (arr, depth) => {
                if (!Array.isArray(arr)) {
                    return `${"  ".repeat(depth)}${arr}`;
                }
                let flat_arr = [];
                for (const v of arr) {
                    flat_arr.push(stringify(v, depth + 1));
                }
                return `${"  ".repeat(depth)}(\n${flat_arr.join("\n")}\n${"  ".repeat(depth)})`;
            };
        try {
            let parsed = Query.parse(filter_query, {getValue, negateValue, andValues, orValues});
            return stringify(parsed, 0);
        } catch (err) {
            return "Unable to parse query";
        }
    },
    applyFilterLogic = function(arr, filters, filter_logic, includes, excludes) {
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
                    }
                } else {
                    console.error(`Unrecognized filter: ${filter.type}`);
                }
            });
        return arr.filter((_, i) => includes.has(i));
    },
    applyRowFilters = function(arr, filters, filter_logic, filter_query) {
        if (filters.length === 0 || arr.length == 0) {
            return arr;
        }
        switch (filter_logic) {
            case DATA_FILTER_LOGIC_CUSTOM:
                return applyCustomQueryFilters(arr, filters, filter_query);
            case DATA_FILTER_LOGIC_AND:
                return applyFilterLogic(
                    arr,
                    filters,
                    filter_logic,
                    new Set(_.range(arr.length)),
                    new Set()
                );
            case DATA_FILTER_LOGIC_OR:
                return applyFilterLogic(
                    arr,
                    filters,
                    filter_logic,
                    new Set(),
                    new Set(_.range(arr.length))
                );
            default:
                console.error(`Unrecognized filter_logic: ${filter_logic}`);
                return;
        }
    };

import _ from "lodash";
import h from "shared/utils/helpers";

export const getColumnValues = function (dataset, column, delimiter) {
    // Get column values for a column in a dataset.  Returns unique values, and removes
    // cases where multiple falsy-like values are represented.
    return _.chain(dataset)
        .map(d => d[column])
        .map(d => (delimiter && d ? d.split(delimiter) : [d]))
        .flatten()
        .uniq()
        .sort()
        .map(d => {
            return d ? {id: d, label: d} : {id: "", label: h.nullString};
        })
        .uniqBy("id")
        .value();
};

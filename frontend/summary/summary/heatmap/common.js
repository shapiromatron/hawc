import _ from "lodash";

export const getColumnValues = function(dataset, column, delimiter) {
    // Get column values for a column in a dataset.
    return _.chain(dataset)
        .map(d => d[column])
        .map(d => (delimiter && d ? d.split(delimiter) : [d]))
        .flatten()
        .uniq()
        .sort()
        .map(d => {
            return {id: d, label: d, included: true};
        })
        .value();
};

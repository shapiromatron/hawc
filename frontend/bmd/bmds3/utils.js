import _ from "lodash";

const getLabel = function(value, items) {
        for (let index = 0; index < items.length; index++) {
            const item = items[index];
            if (item.id === value) {
                return item.label;
            }
        }
        return `Unknown -> ${value}`;
    },
    bmrLabel = function(dtype, bmr_type, bmr_value) {
        const key = `${dtype}-${bmr_type}`;
        switch (key) {
            case "D-0":
                return `${bmr_value * 100}% Added Risk`;
            case "D-1":
                return `${bmr_value * 100}% Extra Risk`;
            case "C-1":
                return `${bmr_value}% Absolute Deviation`;
            case "C-2":
                return `${bmr_value} Standard Deviation`;
            case "C-3":
                return `${bmr_value * 100}% Relative Deviation`;
            default:
                return `${dtype} - ${bmr_value} + ${bmr_type} (TODO)`;
        }
    },
    doseDropOptions = function(dtype, endpoint) {
        const getNumModelableDoses = function(groups) {
            return groups.filter(group => {
                let values;
                switch (dtype) {
                    case "C":
                        values = [group.n, group.response, group.variance];
                        break;
                    case "D":
                        values = [group.n, group.incidence];
                        break;
                    default:
                        throw Error("Unknown data type");
                }
                return _.every(values, _.isNumber);
            }).length;
        };
        let numDoses = getNumModelableDoses(endpoint.data.groups),
            options = [{id: 0, label: "<none>"}];

        if (numDoses > 3) {
            for (let index = 1; index < numDoses - 2; index++) {
                options.push({id: index, label: index.toString()});
            }
        }

        return options;
    };

export {bmrLabel, doseDropOptions, getLabel};

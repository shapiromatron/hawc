import _ from "lodash";
import h from "shared/utils/helpers";

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
    },
    addDoseUnitsToModels = function(outputs, dose_units_id) {
        // modify models to include dose units at root level; necessary for plotting with current
        // abstractions. In the future this should be revised to no longer be necessary
        if (outputs && outputs.models) {
            outputs.models.map(model => {
                model.id = model.name;
                model.dose_units = dose_units_id;
            });
        }
    },
    getModelFromIndex = function(model_index, models) {
        // return output model content or null, based on model index. If value is -1, return
        // null; this is the default case when no model is selected.
        return model_index >= 0 ? models[model_index] : null;
    },
    hexToRgbA = (hex, alpha) => {
        var c;
        if (/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)) {
            c = hex.substring(1).split("");
            if (c.length == 3) {
                c = [c[0], c[0], c[1], c[1], c[2], c[2]];
            }
            c = "0x" + c.join("");
            return "rgba(" + [(c >> 16) & 255, (c >> 8) & 255, c & 255].join(",") + `,${alpha})`;
        }
        throw new Error("Bad Hex");
    },
    getBmdDiamond = function(name, bmd, bmdl, bmdu, bmd_y, hexColor) {
        const hasBmd = bmd > 0;

        // prettier-ignore
        const template = `<b>${name}</b><br />BMD: ${h.ff(bmd)}<br />BMDL: ${h.ff(bmdl)}<br />BMDU: ${h.ff(bmdu)}<br />BMR: ${h.ff(bmd_y)}<extra></extra>`;

        if (hasBmd) {
            return {
                x: [bmd],
                y: [bmd_y],
                mode: "markers",
                type: "scatter",
                hoverinfo: "x",
                hovertemplate: template,
                marker: {
                    color: hexColor,
                    size: 16,
                    symbol: "diamond-tall",
                    line: {
                        color: "white",
                        width: 2,
                    },
                },
                legendgroup: name,
                showlegend: false,
                error_x: {
                    array: [bmdu > 0 ? bmdu - bmd : 0],
                    arrayminus: [bmdl > 0 ? bmd - bmdl : 0],
                    color: hexToRgbA(hexColor, 0.6),
                    thickness: 12,
                    width: 0,
                },
            };
        }
    },
    getPlotlyDrCurve = function(model, hexColor) {
        // https://plotly.com/python/marker-style/
        // https://plotly.com/javascript/reference/scatter/
        const data = [
            {
                x: model.results.plotting.dr_x,
                y: model.results.plotting.dr_y,
                mode: "lines",
                name: model.name,
                hoverinfo: "y",
                line: {
                    color: hexToRgbA(hexColor, 0.8),
                    width: 4,
                    opacity: 0.5,
                },
                legendgroup: model.name,
            },
        ];

        const diamond = getBmdDiamond(
            model.name,
            model.results.bmd,
            model.results.bmdl,
            model.results.bmdu,
            model.results.plotting.bmd_y,
            hexColor
        );
        if (diamond) {
            data.push(diamond);
        }
        return data;
    };

export {
    addDoseUnitsToModels,
    bmrLabel,
    doseDropOptions,
    getLabel,
    getModelFromIndex,
    getPlotlyDrCurve,
};

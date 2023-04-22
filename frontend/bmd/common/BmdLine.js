import _ from "lodash";

import {buildModelFormula} from "./constants";

const getPlotDataV1 = function(model) {
        let bmd = model.output.BMD,
            bmdl = model.output.BMDL,
            {params, formula} = buildModelFormula(
                model.name,
                model.output.parameters,
                model.output.fit_estimated
            ),
            func = xs => {
                return _.chain(xs)
                    .filter(d => d >= 0)
                    .map(d => (d === 0 ? 1e-8 : d))
                    .map(x => {
                        return {x, y: formula(x, params)};
                    })
                    .value();
            };

        return {
            id: model.name,
            dose_units_id: model.dose_units,
            name: model.name,
            getData: func,
            bmd_line: bmd && bmd > 0 ? {x: bmd, y: formula(bmd, params)} : undefined,
            bmdl_line: bmdl && bmdl > 0 ? {x: bmdl, y: formula(bmdl, params)} : undefined,
        };
    },
    getPlotDataV2 = function(model) {
        const {dose_units, name} = model,
            {bmd, bmdl} = model.results,
            {bmd_y, dr_x, dr_y} = model.results.plotting;

        return {
            id: model.name,
            dose_units_id: dose_units,
            name,
            dr_data: _.zip(dr_x, dr_y).map(d => {
                return {x: d[0], y: d[1]};
            }),
            bmd_line: bmd && bmd > 0 ? {x: bmd, y: bmd_y} : undefined,
            bmdl_line: bmdl && bmdl > 0 ? {x: bmdl, y: bmd_y} : undefined,
        };
    };

class BmdLine {
    /*
    Draw a BmdLine on a d3 plot.
    */
    constructor(model, plot, color) {
        this.model = model;
        this.plot = plot;
        this.color = color;
    }

    render() {
        let data = this._getPlotData();
        this.plot.add_bmd_line(data);
    }

    destroy() {
        this.plot.remove_bmd_line(this.model.name);
    }

    _getPlotData() {
        let data;
        if (this.model.output) {
            data = getPlotDataV1(this.model);
        } else if (this.model.results) {
            data = getPlotDataV2(this.model);
        } else {
            console.error("Unknown model type");
        }
        return _.merge(data, {stroke: this.color});
    }
}

export default BmdLine;

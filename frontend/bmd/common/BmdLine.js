import _ from "lodash";

import {buildModelFormula} from "./constants";

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
        this.plot.remove_bmd_line(this.model.id);
    }

    _getPlotData() {
        let bmd = this.model.output.BMD,
            bmdl = this.model.output.BMDL,
            {params, formula} = buildModelFormula(
                this.model.name,
                this.model.output.parameters,
                this.model.output.fit_estimated
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
            id: this.model.id,
            dose_units_id: this.model.dose_units,
            name: this.model.name,
            stroke: this.color,
            getData: func,
            bmd_line: bmd && bmd > 0 ? {x: bmd, y: formula(bmd, params)} : undefined,
            bmdl_line: bmdl && bmdl > 0 ? {x: bmdl, y: formula(bmdl, params)} : undefined,
        };
    }
}

export default BmdLine;

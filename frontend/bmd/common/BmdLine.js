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

    _getModel() {
        return buildModelFormula(
            this.model.name,
            this.model.output.fit_estimated,
            this.model.output.parameters
        );
    }

    _getPlotData() {
        let model = this._getModel(),
            bmd = this.model.output.BMD,
            bmdl = this.model.output.BMDL,
            bmd_line,
            bmdl_line,
            bmd_y;

        // x must be defined since we're calling "eval" in the javascript models
        // eslint-disable-next-line no-unused-vars
        var x;

        if (bmd && bmd > 0) {
            x = bmd;
            bmd_y = eval(model);
            bmd_line = {
                x: bmd,
                y: bmd_y,
            };
        }

        if (bmdl && bmdl > 0) {
            bmdl_line = {
                x: bmdl,
                y: bmd_y,
            };
        }

        return {
            id: this.model.id,
            dose_units_id: this.model.dose_units,
            name: this.model.name,
            stroke: this.color,
            getData(xs) {
                return _.chain(xs)
                    .filter(d => d >= 0)
                    .map(d => (d === 0 ? 1e-8 : d))
                    .map(x => {
                        return {
                            x,
                            y: eval(model),
                        };
                    })
                    .value();
            },
            bmd_line,
            bmdl_line,
        };
    }
}

export default BmdLine;

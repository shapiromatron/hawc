import _ from "lodash";

let formulas = {
    Polynomial:
        "{beta_0} + ({beta_1}*x) + ({beta_2}*Math.pow(x,2)) + ({beta_3}*Math.pow(x,3)) + ({beta_4}*Math.pow(x,4)) + ({beta_5}*Math.pow(x,5)) + ({beta_6}*Math.pow(x,6)) + ({beta_7}*Math.pow(x,7)) + ({beta_8}*Math.pow(x,8))",
    Linear: "{beta_0} + ({beta_1}*x)",
    "Exponential-M2": "{a} * Math.exp({isIncreasing}*{b}*x)",
    "Exponential-M3": "{a} * Math.exp({isIncreasing}*Math.pow({b}*x,{d}))",
    "Exponential-M4": "{a} * ({c}-({c}-1) * Math.exp(-1.*{b}*x))",
    "Exponential-M5": "{a} * ({c}-({c}-1) *  Math.exp(-1.*Math.pow({b}*x,{d})))",
    Power: "{control} + {slope} * Math.pow(x,{power})",
    Hill: "{intercept} + ({v}*Math.pow(x,{n})) / (Math.pow({k},{n}) + Math.pow(x,{n}))",
    Multistage:
        "{Background} + (1. - {Background}) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8)))",
    "Multistage-Cancer":
        "{Background} + (1. - {Background}) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8)))",
    Weibull:
        "{Background} + (1-{Background}) * (1 - Math.exp( -1.*{Slope} * Math.pow(x,{Power}) ))",
    LogProbit:
        "{background} + (1-{background}) * Math.normalcdf({intercept} + {slope}*Math.log(x))",
    Probit: "Math.normalcdf({intercept} + {slope}*x)",
    Gamma: "{Background} + (1 - {Background}) * Math.GammaCDF(x*{Slope},{Power})",
    LogLogistic:
        "{background} + (1-{background})/( 1 + Math.exp(-1.*{intercept}-1.*{slope}*Math.log(x) ) )",
    Logistic: "1/( 1 + Math.exp(-1*{intercept}-{slope}*x ))",
    "Dichotomous-Hill":
        "{v} * {g} + ({v} - {v} * {g}) / (1 + Math.exp(-1 * {intercept} - {slope} * Math.log(x)))",
};

class BMDLine {
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
        // Construct BMD model-form
        let params = {},
            formula = formulas[this.model.name],
            estimates = this.model.output.fit_estimated,
            params_in_formula = formula.match(/\{[\w()]+\}/g);

        // get parameter values for models
        _.each(this.model.output.parameters, (v, k) => {
            params[k] = v.estimate;
        });
        params["isIncreasing"] = estimates[0] < estimates[estimates.length - 1] ? 1 : -1;

        _.each(params_in_formula, function(param) {
            let unbracketed = param.slice(1, param.length - 1),
                v = params[unbracketed] !== undefined ? params[unbracketed] : 0,
                regex = param.replace("(", "\\(").replace(")", "\\)"), // escape ()
                re = new RegExp(regex, "g");
            formula = formula.replace(re, v);
        });
        return formula;
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

export {BMDLine};

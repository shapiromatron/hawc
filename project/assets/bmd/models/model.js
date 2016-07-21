import _ from 'underscore';


let formulas = {
    'Polynomial': '{beta_0} + ({beta_1}*x) + ({beta_2}*Math.pow(x,2)) + ({beta_3}*Math.pow(x,3)) + ({beta_4}*Math.pow(x,4)) + ({beta_5}*Math.pow(x,5)) + ({beta_6}*Math.pow(x,6)) + ({beta_7}*Math.pow(x,7)) + ({beta_8}*Math.pow(x,8))',
    'Linear': '{beta_0} + ({beta_1}*x)',
    'Exponential-M2': '{a} * Math.exp({sign}*{b}*x)',
    'Exponential-M3': '{a} * Math.exp({sign}*Math.pow({b}*x,{d}))',
    'Exponential-M4': '{a} * ({c}-({c}-1) * Math.exp(-1.*{b}*x))',
    'Exponential-M5': '{a} * ({c}-({c}-1) *  Math.exp(-1.*Math.pow({b}*x,{d})))',
    'Power': '{control} + {slope} * Math.pow(x,{power})',
    'Hill': '{intercept} + ({v}*Math.pow(x,{n})) / (Math.pow({k},{n}) + Math.pow(x,{n}))',
    'Multistage': '{Background} + (1. - {Background}) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8)))',
    'Multistage-Cancer': '{Background} + (1. - {Background}) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8)))',
    'Weibull': '{Background} + (1-{Background}) * (1 - Math.exp( -1.*{Slope} * Math.pow(x,{Power}) ))',
    'LogProbit': '{background} + (1-{background}) * Math.normalcdf(0,1,{intercept} + {slope}*Math.log(x))',
    'Probit': 'Math.normalcdf(0,1,{intercept} + {slope}*x)',
    'Gamma': '{Background} + (1 - {Background}) * Math.GammaCDF(x*{Slope},{Power})',
    'LogLogistic': '{background} + (1-{background})/( 1 + Math.exp(-1.*{intercept}-1.*{slope}*Math.log(x) ) )',
    'Logistic': '1/( 1 + Math.exp(-1*{intercept}-{slope}*x ))',
};

class BMDLine {

    constructor(model, plot, color){
        this.model = model;
        this.plot = plot;
        this.color = color;
    }

    render(){
        let data = this._getPlotData();
        this.plot.add_bmd_line(data);
    }

    destroy(){
        this.plot.remove_bmd_line(this.model.id);
    }

    _getModel(){
        // Construct BMD model-form
        let params = this.model.output.parameters,
            formula = formulas[this.model.name],
            params_in_formula = formula.match(/\{[\w\(\)]+\}/g);

        _.each(params_in_formula, function(param){
            let v = (params[param])? params[param].estimate: 0.,
                re = new RegExp(param, 'g');
            formula = formula.replace(re, v);
        });
        return formula;
    }

    _getPlotData(){
        let model = this._getModel(),
            data;

        data = _.chain(this.plot.x_scale.ticks(100))
            .filter((d) => d >= 0)
            .map((d) => (d === 0)? 1e-8: d)
            .map((x) => {
                return {
                    x,
                    y: eval(model) || 3,  // TODO - temporary; fix
                };
            })
            .value();

        return {
            id: this.model.id,
            name: this.model.name,
            stroke: this.color,
            data,
        };

    }
}

export {BMDLine};

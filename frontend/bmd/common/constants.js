import _ from "lodash";

import { normalCDF, gammaCDF } from "shared/utils/math";

const BmrHeaderMap = {
        Extra: "%",
        Added: "% AR",
        "Abs. Dev.": "AD",
        "Std. Dev.": "SD",
        "Rel. Dev.": "% RD",
        Point: "Pt",
    },
    // todo - get rid of this and the evals?
    formulas = {
        Polynomial: (x, p) => p.beta_0 + (p.beta_1*x) + (p.beta_2*Math.pow(x,2)) + (p.beta_3*Math.pow(x,3)) + (p.beta_4*Math.pow(x,4)) + (p.beta_5*Math.pow(x,5)) + (p.beta_6*Math.pow(x,6)) + (p.beta_7*Math.pow(x,7)) + (p.beta_8*Math.pow(x,8)),
        Linear: (x, p) =>p.beta_0 + (p.beta_1*x),
        "Exponential-M2": (x, p) =>p.a * Math.exp(p.isIncreasing*p.b*x),
        "Exponential-M3": (x, p) =>p.a * Math.exp(p.isIncreasing*Math.pow(p.b*x,p.d)),
        "Exponential-M4": (x, p) =>p.a * (p.c-(p.c-1) * Math.exp(-1.*p.b*x)),
        "Exponential-M5": (x, p) =>p.a * (p.c-(p.c-1) *  Math.exp(-1.*Math.pow(p.b*x,p.d))),
        Power: (x, p) => p.control + p.slope * Math.pow(x, p.power),
        Hill: (x, p) => p.intercept + (p.v * Math.pow(x, p.n)) / (Math.pow(p.k, p.n) + Math.pow(x, p.n)),
        // Multistage: (x, p) =>p.Background + (1. - p.Background) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8))),
        // "Multistage-Cancer": (x, p) =>p.Background + (1. - p.Background) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8))),
        Weibull:
            (x, p) =>p.Background + (1-p.Background) * (1 - Math.exp( -1.*p.Slope * Math.pow(x,p.Power) )),
        LogProbit: (x, p) =>p.background + (1-p.background) * normalCDF(p.intercept + p.slope*Math.log(x)),
        Probit: (x, p) =>normalCDF(p.intercept + p.slope*x),
        Gamma: (x, p) =>p.Background + (1 - p.Background) * gammaCDF(x*p.Slope,p.Power),
        LogLogistic:
            (x, p) =>p.background + (1-p.background)/( 1 + Math.exp(-1.*p.intercept-1.*p.slope*Math.log(x) ) ),
        Logistic: (x, p) => 1 / (1 + Math.exp(-1 * p.intercept - p.slope * x )),
        "Dichotomous-Hill":
            (x, p) =>p.v * p.g + (p.v - p.v * p.g) / (1 + Math.exp(-1 * p.intercept - p.slope * Math.log(x))),
    };

export const buildModelFormula = function(model_name, estimates, parameters) {
        let params = {},
            formula = formulas[model_name],
            params_in_formula = formula.match(/\{[\w()]+\}/g);

        // get parameter values for models
        parameters.map((v, k) => params[k] = v.estimate);
        params["isIncreasing"] = estimates[0] < estimates[estimates.length - 1] ? 1 : -1;
        // TODO - replace (6) w/ _6

        _.each(params_in_formula, function(param) {
            let unbracketed = param.slice(1, param.length - 1),
                v = params[unbracketed] !== undefined ? params[unbracketed] : 0,
                regex = param.replace("(", "\\(").replace(")", "\\)"), // escape ()
                re = new RegExp(regex, "g");
            formula = formula.replace(re, v);
        });
        return formula;
    },
    bmdLabelText = function(bmr) {
        let str, val;
        switch (bmr.type) {
            case "Extra":
            case "Added":
            case "Rel. Dev.":
                str = BmrHeaderMap[bmr.type];
                val = bmr.value * 100;
                break;
            case "Abs. Dev.":
            case "Std. Dev.":
            case "Point":
                str = BmrHeaderMap[bmr.type];
                val = bmr.value;
                break;
            default:
                str = bmr.type;
                val = bmr.value;
        }
        return `${val}${str}`;
    },
    CONTINUOUS = "C",
    DICHOTOMOUS = "D",
    DICHOTOMOUS_CANCER = "DC";

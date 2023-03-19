import _ from "lodash";

import {gammaCDF, normalCDF} from "/shared/utils/math";

const BmrHeaderMap = {
        Extra: "%",
        Added: "% AR",
        "Abs. Dev.": "AD",
        "Std. Dev.": "SD",
        "Rel. Dev.": "% RD",
        Point: "Pt",
    },
    formulas = {
        Polynomial: (x, p) =>
            p.beta_0 +
            p.beta_1 * x +
            (p.beta_2 || 0 * Math.pow(x, 2)) +
            (p.beta_3 || 0 * Math.pow(x, 3)) +
            (p.beta_4 || 0 * Math.pow(x, 4)) +
            (p.beta_5 || 0 * Math.pow(x, 5)) +
            (p.beta_6 || 0 * Math.pow(x, 6)) +
            (p.beta_7 || 0 * Math.pow(x, 7)) +
            (p.beta_8 || 0 * Math.pow(x, 8)),
        Linear: (x, p) => p.beta_0 + p.beta_1 * x,
        "Exponential-M2": (x, p) => p.a * Math.exp(p.isIncreasing * p.b * x),
        "Exponential-M3": (x, p) => p.a * Math.exp(p.isIncreasing * Math.pow(p.b * x, p.d)),
        "Exponential-M4": (x, p) => p.a * (p.c - (p.c - 1) * Math.exp(-1 * p.b * x)),
        "Exponential-M5": (x, p) => p.a * (p.c - (p.c - 1) * Math.exp(-1 * Math.pow(p.b * x, p.d))),
        Power: (x, p) => p.control + p.slope * Math.pow(x, p.power),
        Hill: (x, p) =>
            p.intercept + (p.v * Math.pow(x, p.n)) / (Math.pow(p.k, p.n) + Math.pow(x, p.n)),
        Multistage: (x, p) =>
            p.background +
            (1 - p.background) *
                (1 -
                    Math.exp(
                        -1 * p.beta_1 * x -
                            (p.beta_2 || 0 * Math.pow(x, 2)) -
                            (p.beta_3 || 0 * Math.pow(x, 3)) -
                            (p.beta_4 || 0 * Math.pow(x, 4)) -
                            (p.beta_5 || 0 * Math.pow(x, 5)) -
                            (p.beta_6 || 0 * Math.pow(x, 6)) -
                            (p.beta_7 || 0 * Math.pow(x, 7)) -
                            (p.beta_8 || 0 * Math.pow(x, 8))
                    )),
        "Multistage-Cancer": (x, p) =>
            p.background +
            (1 - p.background) *
                (1 -
                    Math.exp(
                        -1 * p.beta_1 * x -
                            (p.beta_2 || 0 * Math.pow(x, 2)) -
                            (p.beta_3 || 0 * Math.pow(x, 3)) -
                            (p.beta_4 || 0 * Math.pow(x, 4)) -
                            (p.beta_5 || 0 * Math.pow(x, 5)) -
                            (p.beta_6 || 0 * Math.pow(x, 6)) -
                            (p.beta_7 || 0 * Math.pow(x, 7)) -
                            (p.beta_8 || 0 * Math.pow(x, 8))
                    )),
        Weibull: (x, p) =>
            p.background + (1 - p.background) * (1 - Math.exp(-1 * p.slope * Math.pow(x, p.power))),
        LogProbit: (x, p) =>
            p.background + (1 - p.background) * normalCDF(p.intercept + p.slope * Math.log(x)),
        Probit: (x, p) => normalCDF(p.intercept + p.slope * x),
        Gamma: (x, p) => p.background + (1 - p.background) * gammaCDF(x * p.slope, p.power),
        LogLogistic: (x, p) =>
            p.background +
            (1 - p.background) / (1 + Math.exp(-1 * p.intercept - 1 * p.slope * Math.log(x))),
        Logistic: (x, p) => 1 / (1 + Math.exp(-1 * p.intercept - p.slope * x)),
        "Dichotomous-Hill": (x, p) =>
            p.v * p.g +
            (p.v - p.v * p.g) / (1 + Math.exp(-1 * p.intercept - p.slope * Math.log(x))),
    },
    cleanParameters = function(parameters, estimates) {
        const cleanNames = _.chain(parameters)
                .keys()
                .map(d =>
                    d
                        .toLowerCase()
                        .replace("(", "_")
                        .replace(")", "")
                )
                .value(),
            paramValues = _.chain(parameters)
                .values()
                .map(d => d.estimate)
                .value(),
            mapping = _.zipObject(cleanNames, paramValues);

        mapping["isIncreasing"] = estimates[0] < estimates[estimates.length - 1] ? 1 : -1;
        return mapping;
    };

export const buildModelFormula = function(name, parameters, estimates) {
        const params = cleanParameters(parameters, estimates),
            formula = formulas[name];
        return {params, formula};
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

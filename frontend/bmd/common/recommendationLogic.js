import * as d3 from "d3";
import _ from "lodash";

import {ff} from "../bmds3/formatters";
import {CONTINUOUS, DICHOTOMOUS, DICHOTOMOUS_CANCER} from "./constants";

/*
Failure bins:
 - 0: no-bin change
 - 1: warning
 - 2: failure
*/

const SUFFICIENTLY_CLOSE_BMDL = 3,
    returnFailure = function(bin, notes) {
        return {
            bin,
            notes,
        };
    },
    validNumeric = function(val) {
        return val !== undefined && _.isNumber(val) && val !== -999;
    },
    minNonZeroDose = function(groups) {
        return d3.min(groups.filter(d => d.dose > 0).map(d => d.dose));
    },
    assertFieldExists = function(value, failure_bin, failure_text) {
        if (!validNumeric(value)) {
            return returnFailure(failure_bin, failure_text);
        }
    },
    assertLessThan = function(value, threshold, failure_bin, varname) {
        if (value > threshold) {
            return returnFailure(
                failure_bin,
                `${varname} (=${ff(value)}) is greater-than than threshold value (${threshold})`
            );
        }
    },
    assertGreaterThan = function(value, threshold, failure_bin, varname) {
        if (value < threshold) {
            return returnFailure(
                failure_bin,
                `${varname} (=${ff(value)}) is less-than than threshold value (${threshold})`
            );
        }
    },
    testCrosswalk = {
        BMD(logic, model, groups) {
            return assertFieldExists(
                model.output.BMD,
                logic.failure_bin,
                "A BMD value was not calculated."
            );
        },
        BMDL(logic, model, groups) {
            return assertFieldExists(
                model.output.BMDL,
                logic.failure_bin,
                "A BMDL value was not calculated."
            );
        },
        BMDU(logic, model, groups) {
            return assertFieldExists(
                model.output.BMDU,
                logic.failure_bin,
                "A BMDU value was not calculated."
            );
        },
        AIC(logic, model, groups) {
            return assertFieldExists(
                model.output.AIC,
                logic.failure_bin,
                "An AIC value was not calculated."
            );
        },
        "Variance Type"(logic, model, groups) {
            let cv =
                    model.overrides.constant_variance !== undefined
                        ? model.overrides.constant_variance
                        : model.defaults.constant_variance.d,
                p_value2 = model.output.p_value2;

            if (p_value2 == "<0.0001") {
                p_value2 = 0.0001;
            }

            if (validNumeric(p_value2)) {
                if ((cv === 1 && p_value2 >= 0.1) || (cv === 0 && p_value2 <= 0.1)) {
                    // pass!
                    return null;
                } else {
                    return returnFailure(
                        logic.failure_bin,
                        `Incorrect variance model (p-value 2 = ${p_value2})`
                    );
                }
            } else {
                return returnFailure(
                    logic.failure_bin,
                    `Correct variance model is undetermined (p-value 2 = ${p_value2})`
                );
            }
        },
        "Variance Fit"(logic, model, groups) {
            let val = model.output.p_value3;

            if (validNumeric(val)) {
                return assertGreaterThan(
                    val,
                    logic.threshold,
                    logic.failure_bin,
                    "Global variance model-fit"
                );
            }
        },
        GGOF(logic, model, groups) {
            let val = model.output.p_value4;
            if (val === "<0.0001") {
                val = 0.0001;
            }
            if (validNumeric(val)) {
                return assertGreaterThan(
                    val,
                    logic.threshold,
                    logic.failure_bin,
                    "Global goodness-of-fit"
                );
            }
        },
        "GGOF (Cancer)"(logic, model, groups) {
            let val = model.output.p_value4;
            if (val === "<0.0001") {
                val = 0.0001;
            }
            if (validNumeric(val)) {
                return assertGreaterThan(
                    val,
                    logic.threshold,
                    logic.failure_bin,
                    "Global goodness-of-fit"
                );
            }
        },
        "BMD/BMDL (serious)"(logic, model, groups) {
            let bmd = model.output.BMD,
                bmdl = model.output.BMDL;

            if (validNumeric(bmd) && validNumeric(bmdl)) {
                return assertLessThan(
                    bmd / bmdl,
                    logic.threshold,
                    logic.failure_bin,
                    "BMD/BMDL ratio"
                );
            }
        },
        "BMD/BMDL (warning)"(logic, model, groups) {
            let bmd = model.output.bmd,
                bmdl = model.output.bmdl;

            if (validNumeric(bmd) && validNumeric(bmdl)) {
                return assertLessThan(
                    bmd / bmdl,
                    logic.threshold,
                    logic.failure_bin,
                    "BMD/BMDL ratio"
                );
            }
        },
        "Residual of Interest"(logic, model, groups) {
            let val = model.output.residual_of_interest;
            if (validNumeric(val)) {
                return assertLessThan(
                    val,
                    logic.threshold,
                    logic.failure_bin,
                    "Residual of interest"
                );
            } else {
                return assertFieldExists(val, logic.failure_bin, "Residual of interest not found.");
            }
        },
        Warnings(logic, model, groups) {
            let vals = model.output.warnings;
            if (vals && vals.length > 0) {
                return returnFailure(logic.failure_bin, vals.join(" "));
            }
        },
        "BMD higher"(logic, model, groups) {
            let high_dose = d3.max(_.map(groups, "dose")),
                bmd = model.output.BMD;
            if (validNumeric(bmd)) {
                return assertLessThan(
                    bmd / high_dose,
                    logic.threshold,
                    logic.failure_bin,
                    "BMD/high-dose ratio"
                );
            }
        },
        "BMDL higher"(logic, model, groups) {
            let high_dose = d3.max(_.map(groups, "dose")),
                bmdl = model.output.BMDL;
            if (validNumeric(bmdl)) {
                return assertLessThan(
                    bmdl / high_dose,
                    logic.threshold,
                    logic.failure_bin,
                    "BMD/high-dose ratio"
                );
            }
        },
        "Low BMD (warning)"(logic, model, groups) {
            let minDose = minNonZeroDose(groups),
                bmd = model.output.BMD;

            if (validNumeric(bmd) && validNumeric(minDose)) {
                return assertLessThan(
                    minDose / bmd,
                    logic.threshold,
                    logic.failure_bin,
                    "BMD/low-dose ratio"
                );
            }
        },
        "Low BMDL (warning)"(logic, model, groups) {
            let minDose = minNonZeroDose(groups),
                bmdl = model.output.BMD;

            if (validNumeric(bmdl) && validNumeric(minDose)) {
                return assertLessThan(
                    minDose / bmdl,
                    logic.threshold,
                    logic.failure_bin,
                    "BMDL/low-dose ratio"
                );
            }
        },
        "Low BMD (serious)"(logic, model, groups) {
            let minDose = minNonZeroDose(groups),
                bmd = model.output.BMD;

            if (validNumeric(bmd) && validNumeric(minDose)) {
                return assertLessThan(
                    minDose / bmd,
                    logic.threshold,
                    logic.failure_bin,
                    "BMD/low-dose ratio"
                );
            }
        },
        "Low BMDL (serious)"(logic, model, groups) {
            let minDose = minNonZeroDose(groups),
                bmdl = model.output.BMD;

            if (validNumeric(bmdl) && validNumeric(minDose)) {
                return assertLessThan(
                    minDose / bmdl,
                    logic.threshold,
                    logic.failure_bin,
                    "BMDL/low-dose ratio"
                );
            }
        },
        "Control residual"(logic, model, groups) {
            if (model.output.fit_residuals === undefined) {
                return;
            }
            let val = Math.abs(model.output.fit_residuals[0]);
            if (validNumeric(val)) {
                return assertLessThan(val, logic.threshold, logic.failure_bin, "Control residual");
            }
        },
        "Control stdev"(logic, model, groups) {
            if (model.output.fit_est_stdev === undefined || model.output.fit_stdev === undefined) {
                return;
            }

            let modeled = model.output.fit_est_stdev[0],
                actual = model.output.fit_stdev[0];

            if (validNumeric(modeled) && validNumeric(actual)) {
                return assertLessThan(
                    Math.abs(modeled / actual),
                    logic.threshold,
                    logic.failure_bin,
                    "Control Stdev. Ratio"
                );
            }
        },
    };

const applyRecommendationLogic = function(logics, models, endpoint, doseUnitsId) {
    endpoint.doseUnits.activate(doseUnitsId);

    // get function associated with each test
    logics = _.chain(logics)
        .filter(d => {
            // filter by data-type
            switch (endpoint.data.data_type) {
                case CONTINUOUS:
                    return d.continuous_on;
                case DICHOTOMOUS:
                    return d.dichotomous_on;
                case DICHOTOMOUS_CANCER:
                    return d.cancer_dichotomous_on;
                default:
                    throw "Unknown data type";
            }
        })
        .each(d => {
            d.func = testCrosswalk[d.name];
        })
        .value();

    // apply unit-tests to each model
    models.forEach(model => {
        // set global recommendations
        model.recommended = false;
        model.recommended_variable = "";

        // set no warnings by default
        model.logic_bin = 0; // set innocent until proven guilty
        model.logic_notes = {
            0: [],
            1: [],
            2: [],
        };

        // apply tests for each model
        logics.forEach(logic => {
            let res = logic.func(logic, model, endpoint.data.groups);
            if (res && res.bin) {
                model.logic_bin = Math.max(res.bin, model.logic_bin);
            }
            if (res && res.notes) {
                model.logic_notes[res.bin].push(res.notes);
            }
        });
    });

    // apply model recommendations, with each bmr being independent.
    let bmr_indexes = _.chain(models)
        .map("bmr_index")
        .uniq()
        .value();

    bmr_indexes.forEach(bmr_index => {
        let subset = _.filter(models, {bmr_index, logic_bin: 0}),
            bmdls = _.chain(subset)
                .map(d => d.output.BMDL)
                .filter(d => _.isNumber(d) && d > 0)
                .value(),
            aics = _.chain(subset)
                .map(d => d.output.AIC)
                .filter(d => _.isNumber(d) && d > 0)
                .value(),
            ratio = d3.max(bmdls) / d3.min(bmdls);

        if (ratio <= SUFFICIENTLY_CLOSE_BMDL) {
            let targetValue = d3.min(aics);
            _.chain(subset)
                .filter(d => d.output.AIC === targetValue)
                .each(d => {
                    d.recommended = true;
                    d.recommended_variable = "AIC";
                })
                .value();
        } else {
            let targetValue = d3.min(bmdls);
            _.chain(subset)
                .filter(d => d.output.BMDL === targetValue)
                .each(d => {
                    d.recommended = true;
                    d.recommended_variable = "BMDL";
                })
                .value();
        }
    });
};

export {applyRecommendationLogic};

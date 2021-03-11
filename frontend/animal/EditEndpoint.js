import $ from "$";
import _ from "lodash";

import DRPlot from "./DRPlot";
import Endpoint from "./Endpoint";

class EditEndpoint {
    constructor(initialData) {
        this.initialData = initialData;
        this.endpoint = new Endpoint(initialData.endpoint_data);
        this.setupForm();
        this.updateEndpointFromForm();
    }

    setupForm() {
        const {initialData} = this,
            firstDoses = initialData.doses[0];

        // reorganize forms
        $("#endpointGroups").insertBefore($("div.form-actions"));

        // html5 enabled form
        $("#id_results_notes").quillify();
        $("#id_endpoint_notes").quillify();

        //update values in doses table
        $("#doses_title").html(`Dose<br>(${firstDoses.name})`);
        $(".doses").each(function(i, v) {
            $(v).html(firstDoses.values[i]);
        });

        // set NOEL, LOEL, FEL
        const {endpoint} = this;
        var fields = $("#id_NOEL, #id_LOEL, #id_FEL").html(
            "<option value=-999>&lt;None&gt;</option>"
        );

        $(".doses").each(function(i, v) {
            fields.append(`<option value="${i}">${v.textContent}</option>`);
        });

        $(`#id_NOEL option[value="${endpoint.data.NOEL}"]`).prop("selected", true);
        $(`#id_LOEL option[value="${endpoint.data.LOEL}"]`).prop("selected", true);
        $(`#id_FEL option[value="${endpoint.data.FEL}"]`).prop("selected", true);

        // toggle the name of the variance column header as the value changes
        $("#id_variance_type")
            .on("change", () => {
                var varHeader = $("#varianceHeader"),
                    getVarType = function() {
                        const varType = parseInt($("#id_variance_type").val());
                        switch (varType) {
                            case 0:
                                return "N/A";
                            case 1:
                                return "Standard Deviation";
                            case 2:
                                return "Standard Error";
                            case 3:
                                return "Not Reported";
                            default:
                                throw "Unknown variance_type";
                        }
                    };
                varHeader.html(getVarType());
            })
            .trigger("change");

        // change if endpoint-groups div should be shown
        $("#id_data_reported, #id_data_extracted")
            .on("change", () => {
                var egDiv = $("#endpointGroups"),
                    egsRequired =
                        $("#id_data_reported").prop("checked") &&
                        $("#id_data_extracted").prop("checked");
                egsRequired ? egDiv.fadeIn() : egDiv.fadeOut();
            })
            .trigger("change");

        // change required fields based on dataset-type
        $("#id_data_type")
            .on("change", function() {
                var varTypeDiv = $("#div_id_variance_type"),
                    CI = $("#div_id_confidence_interval"),
                    shows,
                    hides;

                switch (this.value) {
                    case "C":
                        shows = ".c_only,.pc_only";
                        hides = ".d_only,.p_only";
                        break;
                    case "D":
                    case "DC":
                        shows = ".d_only";
                        hides = ".c_only,.p_only,.pc_only";
                        break;
                    case "P":
                        shows = ".p_only,.pc_only";
                        hides = ".c_only,.d_only";
                        break;
                }
                $(shows).show();
                $(hides).hide();

                if (this.value === "C") {
                    varTypeDiv.fadeIn();
                } else {
                    varTypeDiv.fadeOut();
                    $("#id_variance_type").val(0);
                }

                if (this.value === "P") {
                    CI.fadeIn();
                } else {
                    CI.fadeOut();
                    $("#id_confidence_interval").val("");
                }
            })
            .trigger("change");

        // show/hide the litter_effects fields depending on the underlying experiment type
        var litEff = $("#id_litter_effects"),
            litEffNotes = $("#id_litter_effect_notes"),
            litterDiv = $("#row_id_litter_effects_2");

        if (initialData.litterEffectRequired) {
            litterDiv.show();
        } else {
            litterDiv.hide();
            litEff.val("NA");
            litEffNotes.val("");
        }

        // whenever input changes, update data form
        $("body")
            .on("keyup", "input", () => this.updateEndpointFromForm())
            .on("change", "select", () => this.updateEndpointFromForm());
    }

    updateEndpointFromForm() {
        let vals = _.cloneDeep(this.endpoint.data);
        vals.groups = [];

        // save form values
        $("#endpoint :input").each(function() {
            if (!this.name.includes("form-")) {
                vals[this.name] = $(this).val();
            }
        });
        vals["NOEL"] = $("#id_NOEL option:selected").val();
        vals["LOEL"] = $("#id_LOEL option:selected").val();
        vals["FEL"] = $("#id_FEL option:selected").val();

        // save endpoint-group data
        $("#eg")
            .find("tbody > tr")
            .each(function(i, tr) {
                var row = {};
                $(tr)
                    .find(":input")
                    .each(function(i, d) {
                        const name = d.name.split("-").pop(),
                            valueMaybe = parseFloat(d.value),
                            value = $.isNumeric(valueMaybe) ? valueMaybe : null;
                        row[name] = value;
                    });
                row["isReported"] = $.isNumeric(row["response"]) || $.isNumeric(row["incidence"]);
                row["hasVariance"] = $.isNumeric(row["variance"]);
                vals.groups.push(row);
            });
        delete vals[""]; // cleanup
        this.endpoint.data = vals;
        this._calculate_confidence_intervals();
        this.endpoint._switch_dose(0);
        new DRPlot(this.endpoint, "#endpoint_plot");
    }

    _calculate_confidence_intervals() {
        // Calculate 95% confidence intervals
        const {endpoint} = this;
        if (
            endpoint.data === undefined ||
            endpoint.data.data_type === undefined ||
            !endpoint.hasEGdata()
        ) {
            return;
        }
        if (endpoint.data.data_type === "C") {
            /*
            Use t-test z-score of 1.96 for approximation. Note only used during
            input forms;
            */
            endpoint.data.groups
                .filter(d => d.isReported)
                .forEach(v => {
                    if (!v.variance || !v.n) {
                        return;
                    }
                    if (v.stdev === undefined) {
                        endpoint._calculate_stdev(v);
                    }
                    var se = v.stdev / Math.sqrt(v.n),
                        z = Math.inv_tdist_05(v.n - 1) || 1.96;

                    v.lower_ci = v.response - se * z;
                    v.upper_ci = v.response + se * z;
                });
        } else if (endpoint.data.data_type === "P") {
            // no change needed
        } else {
            /*
            Procedure adds confidence intervals to dichotomous datasets.
            Taken from bmds231_manual.pdf, pg 124-5

            LL = {(2np + z2 - 1) - z*sqrt[z2 - (2+1/n) + 4p(nq+1)]}/[2*(n+z2)]
            UL = {(2np + z2 + 1) + z*sqrt[z2 + (2-1/n) + 4p(nq-1)]}/[2*(n+z2)]

            - p = the observed proportion
            - n = the total number in the group in question
            - z = Z(1-alpha/2) is the inverse standard normal cumulative distribution
                    function evaluated at 1-alpha/2
            - q = 1-p.

            The error bars shown in BMDS plots use alpha = 0.05 and so represent
            the 95% confidence intervals on the observed proportions (independent of
            model).
            */
            endpoint.data.groups
                .filter(d => d.isReported)
                .forEach(v => {
                    var p = v.incidence / v.n,
                        q = 1 - p,
                        z = 1.959963986120195;
                    v.lower_ci =
                        (2 * v.n * p +
                            2 * z -
                            1 -
                            z * Math.sqrt(2 * z - (2 + 1 / v.n) + 4 * p * (v.n * q + 1))) /
                        (2 * (v.n + 2 * z));
                    v.upper_ci =
                        (2 * v.n * p +
                            2 * z +
                            1 +
                            z * Math.sqrt(2 * z + (2 + 1 / v.n) + 4 * p * (v.n * q - 1))) /
                        (2 * (v.n + 2 * z));
                });
        }
    }
}

export default EditEndpoint;

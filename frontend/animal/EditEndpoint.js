import _ from "lodash";
import {
    addContinuousConfidenceIntervals,
    addDichotomousConfidenceIntervals,
    addStdev,
} from "shared/utils/math";

import $ from "$";

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

        //update values in doses table
        $("#doses_title").html(`Dose<br>(${firstDoses.name})`);
        $(".doses").each(function(i, v) {
            $(v).html(firstDoses.values[i]);
        });

        // set NOEL, LOEL, FEL
        const {endpoint} = this;
        const options = firstDoses.values.map(
            (v, i) => `<option value="${i}">${v} ${firstDoses.name}</option>`
        );
        options.unshift("<option value=-999>&lt;None&gt;</option>");
        $("#id_NOEL, #id_LOEL, #id_FEL").html(options);
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
        this.endpoint.doseUnits.activateFirst();
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
            addStdev(endpoint);
            addContinuousConfidenceIntervals(endpoint);
        } else if (endpoint.data.data_type === "P") {
            // no change needed
        } else {
            addDichotomousConfidenceIntervals(endpoint);
        }
    }
}

export default EditEndpoint;
export {addContinuousConfidenceIntervals, addDichotomousConfidenceIntervals};

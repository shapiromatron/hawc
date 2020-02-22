import $ from "$";
import _ from "lodash";

import DRPlot from "./DRPlot";
import Endpoint from "./Endpoint";

class EditEndpoint extends Endpoint {
    constructor(settings, data, doses, eg_table, plot) {
        super(data);
        this.settings = settings;
        this.doses = data.doses;
        this.eg_table = eg_table;
        this.plot_div = plot;
        this.inject_doses(doses);
        this.setOELS();
        this.update_endpoint_from_form();
    }

    static getVarianceType(variance_type) {
        // static method used for returning the 'pretty-name' for variance type
        switch (variance_type) {
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
    }

    update_endpoint_from_form() {
        var vals = {
            groups: [],
            noel_names: this.settings.noel_names,
        };

        //save form values
        $("#endpoint :input").each(function() {
            vals[this.name] = $(this).val();
        });
        vals["NOEL"] = $("#id_NOEL option:selected").val();
        vals["LOEL"] = $("#id_LOEL option:selected").val();
        vals["FEL"] = $("#id_FEL option:selected").val();

        //now endpoint-group data
        this.eg_table.find("tbody > tr").each(function(i, tr) {
            var row = {};
            $(tr)
                .find(":input")
                .each(function(i, d) {
                    var name = d.name.split("-").pop();
                    row[name] = parseFloat(d.value, 10);
                });
            row["isReported"] = $.isNumeric(row["response"]) || $.isNumeric(row["incidence"]);
            row["hasVariance"] = $.isNumeric(row["variance"]);
            vals.groups.push(row);
        });
        delete vals[""]; // cleanup
        vals["doses"] = this.doses;
        this.data = vals;
        this.calculate_confidence_intervals();
        this._switch_dose(0);
        new DRPlot(this, "#endpoint_plot").build_plot();
    }

    inject_doses(doses) {
        // add dose-units into endpoint-representation
        this.doses = _.map(doses, function(v) {
            return {
                key: v.id.toString(),
                name: v.name,
                values: v.values.map(function(v2) {
                    return {dose: v2};
                }),
            };
        });
        this._switch_dose(0);
    }

    setOELS() {
        // set NOEL, LOEL, FEL
        var fields = $("#id_NOEL, #id_LOEL, #id_FEL").html(
            "<option value=-999>&lt;None&gt;</option>"
        );

        $(".doses").each(function(i, v) {
            fields.append('<option value="{0}">{1}</option>'.printf(i, v.textContent));
        });

        $('#id_NOEL option[value="{0}"]'.printf(this.data.NOEL)).prop("selected", true);
        $('#id_LOEL option[value="{0}"]'.printf(this.data.LOEL)).prop("selected", true);
        $('#id_FEL option[value="{0}"]'.printf(this.data.FEL)).prop("selected", true);
    }

    calculate_confidence_intervals() {
        // Calculate 95% confidence intervals
        if (this.data !== undefined && this.data.data_type !== undefined && this.hasEGdata()) {
            if (this.data.data_type === "C") {
                this._add_continuous_confidence_intervals();
            } else if (this.data.data_type === "P") {
                // no change needed
            } else {
                this._add_dichotomous_confidence_intervals();
            }
        }
    }

    _add_dichotomous_confidence_intervals() {
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
        _.chain(this.data.groups)
            .filter(function(d) {
                return d.isReported;
            })
            .each(function(v) {
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
            })
            .value();
    }

    _add_continuous_confidence_intervals() {
        /*
        Use t-test z-score of 1.96 for approximation. Note only used during
        input forms;
        */
        var self = this;
        _.chain(this.data.groups)
            .filter(function(d) {
                return d.isReported;
            })
            .each(function(v) {
                if (!v.variance || !v.n) return;
                if (v.stdev === undefined) self._calculate_stdev(v);
                var se = v.stdev / Math.sqrt(v.n),
                    z = Math.inv_tdist_05(v.n - 1) || 1.96;

                v.lower_ci = v.response - se * z;
                v.upper_ci = v.response + se * z;
            })
            .value();
    }
}

export default EditEndpoint;

import $ from "$";
import _ from "lodash";
import TableFootnotes from "shared/utils/TableFootnotes";
import h from "shared/utils/helpers";

class EndpointTable {
    constructor(endpoint, tbl_id) {
        this.endpoint = endpoint;
        this.tbl = $(tbl_id);
        this.footnotes = new TableFootnotes();
        this.build_table();
        this.endpoint.addObserver(this);
    }

    update(_status) {
        this.build_table();
    }

    build_table() {
        if (!this.endpoint.hasEGdata()) {
            this.tbl.html("<p>Dose-response data unavailable.</p>");
        } else {
            this.footnotes.reset();
            this.build_header();
            this.build_body();
            this.build_footer();
            this.build_colgroup();
            this.tbl.html([this.colgroup, this.thead, this.tfoot, this.tbody]);
        }
        return this.tbl;
    }

    hasValues(val) {
        return _.chain(this.endpoint.data.groups)
            .map(function (d) {
                return d[val];
            })
            .some(x => !_.isNil(x))
            .value();
    }

    build_header() {
        var self = this,
            d = this.endpoint.data,
            dose = $(`<th>Dose (${this.endpoint.doseUnits.activeUnit.name})</th>`),
            tr = $("<tr>"),
            txt;

        if (this.endpoint.doseUnits.numUnits() > 1) {
            $(
                '<a class="btn btn-sm btn-light" title="View alternate dose" href="#"><i class="fa fa-chevron-right"></i></a>'
            )
                .on("click", function (e) {
                    e.preventDefault();
                    self.endpoint.doseUnits.next();
                })
                .appendTo(dose);
        }

        tr.append(dose);

        this.hasN = this.hasValues("n");
        if (this.hasN) tr.append("<th>Number of Animals</th>");

        switch (d.data_type) {
            case "D":
            case "DC":
                tr.append("<th>Incidence</th>").append("<th>Percent Incidence</th>");
                break;
            case "P":
                tr.append(`<th>Response (${d.confidence_interval * 100}% CI)</th>`);
                break;
            case "C":
                txt = "Response";
                if (this.endpoint.data.response_units) {
                    txt += ` (${this.endpoint.data.response_units})`;
                }
                tr.append($("<th>").text(txt));
                this.hasVariance = this.hasValues("variance");
                if (this.hasVariance) tr.append(`<th>${d.variance_name}</th>`);
                break;
            default:
                throw "Unknown data type.";
        }
        this.hasTreatmentColumn = this.hasValues("treatment_effect");
        if (this.hasTreatmentColumn) {
            tr.append("<th>Treatment Related Effect</th>");
        }
        this.number_columns = tr.children().length;
        this.thead = $("<thead>").append(tr);
    }

    build_body() {
        this.tbody = $("<tbody></tbody>");
        var self = this;
        this.endpoint.data.groups.forEach(function (v, i) {
            if (!v.isReported) return;

            var tr = $("<tr>"),
                dose = h.ff(v.dose);

            dose = dose + self.endpoint.add_endpoint_group_footnotes(self.footnotes, i);

            tr.append(`<td>${dose}</td>`);

            if (self.hasN) tr.append(`<td>${v.n || "NR"}</td>`);

            if (self.endpoint.data.data_type == "C") {
                tr.append(`<td>${v.response}</td>`);
                if (self.hasVariance) tr.append(`<td>${v.variance || "NR"}</td>`);
            } else if (self.endpoint.data.data_type == "P") {
                tr.append(`<td>${self.endpoint.get_pd_string(v)}</td>`);
            } else {
                tr.append(`<td>${v.incidence}</td>`).append(
                    `<td>${self.endpoint._dichotomous_percent_change_incidence(v)}%</td>`
                );
            }
            if (self.hasTreatmentColumn) {
                tr.append(`<td>${v.treatment_effect || "---"}</td>`);
            }
            self.tbody.append(tr);
        });
    }

    build_footer() {
        var txt = this.footnotes.html_list().join("<br>");
        this.tfoot = $(`<tfoot><tr><td colspan="${this.number_columns}">${txt}</td></tr></tfoot>`);
    }

    build_colgroup() {
        this.colgroup = $("<colgroup></colgroup>");
        var self = this;
        for (var i = 0; i < this.number_columns; i++) {
            self.colgroup.append(`<col style="width:${100 / self.number_columns}%;">`);
        }
    }
}

export default EndpointTable;

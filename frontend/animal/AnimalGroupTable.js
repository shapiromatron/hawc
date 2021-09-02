import $ from "$";
import _ from "lodash";

import BaseTable from "shared/utils/BaseTable";

class AnimalGroupTable {
    constructor(endpoints) {
        this.endpoints = endpoints;
        this.tbl = new BaseTable();
        (this.endpoints_no_dr = this.endpoints.filter(v => !v.hasEGdata())),
            (this.endpoints_dr = this.endpoints.filter(v => v.hasEGdata()));
    }

    static render($div, endpoints) {
        var tbl = new AnimalGroupTable(endpoints);

        $div.append(tbl.build_table());

        if (tbl.endpoints_no_dr.length > 0) {
            $div.append("<h3>Additional endpoints</h3>")
                .append("<p>Endpoints which have no dose-response data extracted.</p>")
                .append(tbl.build_no_dr_ul());
        }
    }

    build_table() {
        if (this.endpoints_dr.length === 0)
            return "<p>No endpoints with dose-response data extracted are available.</p>";

        this._build_header();
        this._build_tbody();
        return this.tbl.getTbl();
    }

    _build_header() {
        var header = this.endpoints[0]._build_ag_dose_rows();
        _.each(header.html, this.tbl.addHeaderRow.bind(this.tbl));
        this.ncols = header.ncols;
    }

    _build_tbody() {
        var tbl = this.tbl,
            ngroups = this._sort_egs_by_n();

        ngroups.forEach(function(endpoints) {
            _.chain(endpoints)
                .each(function(v, i) {
                    if (i === 0) tbl.addRow(v._build_ag_n_row());
                    tbl.addRow(v._build_ag_response_row(tbl.footnotes));
                })
                .value();
        });
    }

    _sort_egs_by_n() {
        /*
        Return an array of arrays of endpoints which have the same
        number of animals, to reduce printing duplicative N rows in table.
        */
        var eps = {},
            key;

        this.endpoints_dr.forEach(function(v) {
            key = v.build_ag_n_key();
            if (eps[key] === undefined) eps[key] = [];
            eps[key].push(v);
        });
        return _.values(eps);
    }

    build_no_dr_ul() {
        var ul = $("<ul>");
        this.endpoints_no_dr.forEach(function(v) {
            ul.append(v.build_ag_no_dr_li());
        });
        return ul;
    }
}

export default AnimalGroupTable;

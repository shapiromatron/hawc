import _ from "lodash";
import BaseTable from "shared/utils/BaseTable";
import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

import IVChemical from "./IVChemical";
import IVEndpointGroup from "./IVEndpointGroup";

class IVEndpoint {
    constructor(data) {
        this.data = data;
        this._build_ivegs();
        this._build_chemical();
    }

    static get_detail_url(id) {
        return `/in-vitro/endpoint/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/in-vitro/api/endpoint/${id}/`, d => cb(new IVEndpoint(d)));
    }

    static displayAsModal(id) {
        IVEndpoint.get_object(id, d => d.displayAsModal());
    }

    static displayAsPage(id, div) {
        IVEndpoint.get_object(id, d => d.displayAsPage(div));
    }

    _build_ivegs() {
        var groups = this.data.groups;
        groups.sort(function(a, b) {
            return a.id - b.id;
        });
        this.egs = groups.map(v => new IVEndpointGroup(v));
        delete this.data.groups;
    }

    _build_chemical() {
        if (this.data.chemical) {
            this.chemical = new IVChemical(this.data.chemical);
            delete this.data.chemical;
        }
    }

    build_hyperlink() {
        return `<a href="${this.data.url}">${this._title_text()}</a>`;
    }

    _title_text() {
        return this.data.name;
    }

    has_egs() {
        return this.egs.length > 0;
    }

    build_title() {
        var el = $("<div class='d-flex'>").append($("<h2>").text(this._title_text()));
        if (window.canEdit) {
            var urls = [
                "Endpoint editing",
                {href: this.data.url_update, text: "Update"},
                {href: this.data.url_delete, text: "Delete"},
            ];
            el.append(HAWCUtils.pageActionsButton(urls));
        }
        return el;
    }

    build_details_table() {
        var self = this,
            tbl = new DescriptiveTable(),
            getBenchmarkText = function(d) {
                return `${d.benchmark}: ${d.value}`;
            },
            getCriticalValue = function(idx) {
                try {
                    return `${self.egs[idx].data.dose} ${self.data.experiment.dose_units.name}`;
                } catch (err) {
                    return undefined;
                }
            },
            getObservationTime = function() {
                if (self.data.observation_time.length > 0)
                    return `${self.data.observation_time} ${self.data.observation_time_units}`;
            },
            getCategory = function(cat) {
                if (cat) return cat.names.join("→");
            };

        tbl.add_tbody_tr("Name", this.data.name)
            .add_tbody_tr("Assay type", this.data.assay_type)
            .add_tbody_tr("Short description", this.data.short_description)
            .add_tbody_tr("Effect category", this.data.effect)
            .add_tbody_tr("Specific category", getCategory(this.data.category))
            .add_tbody_tr("Data location", this.data.data_location)
            .add_tbody_tr("Data type", this.data.data_type)
            .add_tbody_tr("Variance type", this.data.variance_type)
            .add_tbody_tr("Response units", this.data.response_units)
            .add_tbody_tr("Values estimated", HAWCUtils.booleanCheckbox(this.data.values_estimated))
            .add_tbody_tr("Observation time", getObservationTime())
            .add_tbody_tr("NOEL", getCriticalValue(this.data.NOEL))
            .add_tbody_tr("LOEL", getCriticalValue(this.data.LOEL))
            .add_tbody_tr("Monotonicity", this.data.monotonicity)
            .add_tbody_tr("Overall pattern", this.data.overall_pattern)
            .add_tbody_tr("Statistical test notes", this.data.statistical_test_notes)
            .add_tbody_tr("Trend test", this.data.trend_test)
            .add_tbody_tr("Trend test notes", this.data.trend_test_notes)
            .add_tbody_tr("Endpoint notes", this.data.endpoint_notes)
            .add_tbody_tr("Result notes", this.data.result_notes)
            .add_tbody_tr_list("Effects", _.map(this.data.effects, "name"))
            .add_tbody_tr_list("Benchmarks", this.data.benchmarks.map(getBenchmarkText));

        // add additional fields
        _.each(this.data.additional_fields, function(val, key) {
            tbl.add_tbody_tr(HAWCUtils.prettifyVariableName(key), val);
        });

        return tbl.get_tbl();
    }

    build_eg_table() {
        var self = this,
            tbl = new BaseTable(),
            units = this.data.experiment.dose_units.name,
            getAvailableColumns = function() {
                var opts = {
                    hasN: false,
                    hasResponse: false,
                    hasVariance: false,
                    hasDiffControl: false,
                    hasSigControl: false,
                    hasCytotox: false,
                    hasPrecip: false,
                };
                self.egs.forEach(function(v) {
                    if (v.data.n !== null) opts.hasN = true;
                    if (v.data.response !== null) opts.hasResponse = true;
                    if (v.data.variance !== null) opts.hasVariance = true;
                    if (v.data.difference_control !== "not-tested") opts.hasDiffControl = true;
                    if (v.data.significant_control !== "not reported") opts.hasSigControl = true;
                    if (v.data.cytotoxicity_observed !== "not reported") opts.hasCytotox = true;
                    if (v.data.precipitation_observed !== "not reported") opts.hasPrecip = true;
                });
                return opts;
            },
            opts = getAvailableColumns(),
            headers = function(opts) {
                var arr = [`Dose (${units})`];
                if (opts.hasN) arr.push("N");
                if (opts.hasResponse) arr.push("Response");
                if (opts.hasVariance) arr.push("Variance");
                if (opts.hasDiffControl) arr.push("Difference<br>Control");
                if (opts.hasSigControl) arr.push("Significant<br>Control");
                if (opts.hasCytotox) arr.push("Cytotoxicity<br>Observed");
                if (opts.hasPrecip) arr.push("Precipitation<br>Observed");
                return arr;
            };

        tbl.addHeaderRow(headers(opts));
        this.egs.forEach(function(v, i) {
            opts.isLOEL = i === self.data.LOEL;
            opts.isNOEL = i === self.data.NOEL;
            tbl.addRow(v.build_row(tbl, opts));
        });
        return tbl.getTbl();
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            $details = $('<div class="col-md-12">'),
            $eg_tbl = $('<div class="col-md-12">'),
            $content = $('<div class="container-fluid">')
                .append($('<div class="row">').append($details))
                .append($('<div class="row">').append($eg_tbl));

        $details.append(this.build_details_table());

        if (this.has_egs()) {
            $eg_tbl.append(this.build_eg_table());
        }

        modal
            .addTitleLinkHeader(this.data.name, this.data.url)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    }

    displayAsPage($div) {
        $div.append(this.build_title())
            .append(this.build_details_table())
            .append("<h3>Chemical details</h3>")
            .append(this.chemical.build_details_table());

        if (this.has_egs()) {
            $div.append("<h3>Endpoint-group</h3>").append(this.build_eg_table());
        }
    }
}

export default IVEndpoint;

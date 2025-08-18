import $ from "$";
import BmdLine from "bmd/common/BmdLine";
import * as d3 from "d3";
import _ from "lodash";
import BaseTable from "shared/utils/BaseTable";
import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import Observee from "shared/utils/Observee";
import h from "shared/utils/helpers";
import Study from "study/Study";

import AnimalGroup from "./AnimalGroup";
import BMDResult from "./BMDResult";
import EndpointCriticalDose from "./EndpointCriticalDose";
import EndpointPlotContainer from "./EndpointPlotContainer";
import EndpointTable from "./EndpointTable";
import Experiment from "./Experiment";

class ActiveDose {
    constructor(endpoint) {
        this.endpoint = endpoint;
        this.data = this.endpoint.data.animal_group.dosing_regime.doses;
        this.units = _.chain(this.data)
            .map(d => d.dose_units)
            .uniqBy(d => d.id)
            .value();
        this.doseOptions = _.groupBy(this.data, d => d.dose_units.id);
        this.activeUnit = null;
        this.activeDoses = [];
        this.activateFirst();
    }

    activateFirst() {
        const unitId = this.units.length > 0 ? this.units[0].id : null;
        this.activate(unitId);
    }

    numUnits() {
        return this.units.length;
    }

    next() {
        const currentIndex = _.findIndex(this.units, unit => this.activeUnit.id === unit.id),
            numUnits = this.numUnits();

        if (_.isFinite(currentIndex) && numUnits > 1) {
            const nextIndex = currentIndex + 1 === numUnits ? 0 : currentIndex + 1;
            this.activate(this.units[nextIndex].id);
        }
    }

    hasUnits(doseUnitsId) {
        return this.units.filter(d => d.id === doseUnitsId).length > 0;
    }

    activate(doseUnitsId) {
        // set null case
        if (doseUnitsId === null) {
            this.activeUnit = null;
            this.activeDoses = [];
            this.endpoint.data.groups.forEach(eg => {
                eg.dose = -1;
            });
            this.endpoint.notifyObservers({status: "dose_changed"});
            return;
        }
        const unit = _.find(this.units, d => d.id === doseUnitsId);
        if (unit) {
            this.activeUnit = unit;
            this.activeDoses = this.doseOptions[doseUnitsId];
            this.endpoint.data.groups.forEach((eg, i) => {
                // gracefully handle "broken" state where groups != doses; this should never
                // occur but sometimes unfortunately does; log an error so we can investigate
                // the issue.
                const dose = this.activeDoses[i];
                if (_.isUndefined(dose)) {
                    console.error(`Invalid dose mapping: endpoint ${this.endpoint.data.id}`);
                }
                eg.dose = dose ? dose.dose : "<none>";
            });
            this.endpoint.notifyObservers({status: "dose_changed"});
            return;
        }
        // throw error; didn't go as expected
        throw `Unknown doseUnitsId: ${doseUnitsId}`;
    }

    doseChoices() {
        return this.units.map(d => {
            return {id: d.id, label: d.name};
        });
    }

    dosesByDoseIndex(index) {
        return this.data.filter(d => d.dose_group_id === index);
    }
}

class Endpoint extends Observee {
    constructor(data) {
        super();
        if (!data) {
            // added for edit_endpoint prototype extension
            return;
        }
        this.data = data;
        this.doseUnits = new ActiveDose(this);
    }

    static get_detail_url(id) {
        return `/ani/endpoint/${id}/`;
    }

    static get_api_url(id) {
        return `/ani/api/endpoint/${id}/`;
    }

    static get_object(id, cb) {
        const url = Endpoint.get_api_url(id);
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(data => cb(new Endpoint(data)));
    }

    static displayAsModal(id, opts) {
        Endpoint.get_object(id, d => d.displayAsModal(opts));
    }

    static displayInline(id, setTitle, setBody) {
        Endpoint.get_object(id, obj => {
            let title = $("<h4>").html(obj.build_breadcrumbs()),
                plot_div = $('<div style="height:350px; width:350px">'),
                tbl = obj.build_endpoint_table($('<table class="table table-sm table-striped">')),
                content = $('<div class="row">')
                    .append($('<div class="col-md-8">').append(tbl))
                    .append($('<div class="col-md-4">').append(plot_div));

            setTitle(title);
            setBody(content);
            obj.renderPlot(plot_div, {showBmd: true});
        });
    }

    get_name() {
        return this.data.name;
    }

    get_pod() {
        // Get point-of-departure and point-of-departure type.
        if (isFinite(this.get_special_bmd_value("BMDL"))) {
            return {type: "BMDL", value: this.get_special_bmd_value("BMDL")};
        }
        if (isFinite(this.get_special_dose_text("LOEL"))) {
            return {type: "LOEL", value: this.get_special_dose_text("LOEL")};
        }
        if (isFinite(this.get_special_dose_text("NOEL"))) {
            return {type: "NOEL", value: this.get_special_dose_text("NOEL")};
        }
        if (isFinite(this.get_special_dose_text("FEL"))) {
            return {type: "FEL", value: this.get_special_dose_text("FEL")};
        }
        return {type: undefined, value: undefined};
    }

    get_special_dose_text(name) {
        // return the appropriate dose of interest
        try {
            return h.ff(this.data.groups[this.data[name]].dose);
        } catch (_err) {
            return "-";
        }
    }

    get_active_selected_bmd() {
        // get selected bmd given the active dose units or undefined
        const activeDoseUnitId = this.doseUnits.activeUnit.id;
        return _.find(
            this.data.bmds,
            d => d.dose_units_id === activeDoseUnitId && d.model && d.model.output
        );
    }

    get_special_bmd_value(name) {
        const selected = this.get_active_selected_bmd();
        return selected ? h.ff(selected.model.output[name]) : "-";
    }

    build_endpoint_table(tbl_id) {
        this.table = new EndpointTable(this, tbl_id);
        return this.table.tbl;
    }

    build_breadcrumbs() {
        var urls = [
            {
                url: this.data.animal_group.experiment.study.url,
                name: this.data.animal_group.experiment.study.short_citation,
            },
            {
                url: this.data.animal_group.experiment.url,
                name: this.data.animal_group.experiment.name,
            },
            {
                url: this.data.animal_group.url,
                name: this.data.animal_group.name,
            },
            {url: this.data.url, name: this.data.name},
        ];
        return HAWCUtils.build_breadcrumbs(urls);
    }

    get_pd_string(eg) {
        var txt = `${eg.response}%`;
        if (eg.lower_ci && eg.upper_ci) {
            txt += ` (${eg.lower_ci}-${eg.upper_ci})`;
        }
        return txt;
    }

    isDichotomous() {
        return ["D", "DC"].includes(this.data.data_type);
    }

    _calculate_stdev(eg) {
        // stdev is required for plotting; calculate if SE is specified
        var convert = this.data.data_type === "C" && parseInt(this.data.variance_type, 10) === 2;
        if (convert) {
            if (_.isFinite(eg.n)) {
                eg.stdev = eg.variance * Math.sqrt(eg.n);
            } else {
                eg.stdev = undefined;
            }
        } else {
            eg.stdev = eg.variance;
        }
    }

    _endpoint_detail_td() {
        return `
            <a
                class="endpoint-selector"
                href="#">${this.data.name} (${this.data.response_units})</a>
            <a
                class="float-right"
                title="View endpoint details (new window)"
                href="${this.data.url}">
                <i class="fa fa-share-square-o"></i>
            </a>
        `;
    }

    build_details_table(div) {
        var self = this,
            tbl = new DescriptiveTable(),
            critical_dose = function (type) {
                if (self.data[type] < 0) return;
                var span = $("<span>");
                new EndpointCriticalDose(self, span, type);
                return span;
            },
            bmd_response = function (type, showURL) {
                if (self.data.bmds.length === 0) {
                    return;
                }
                var el = $("<div>");
                new BMDResult(self, el, type, showURL);
                return el;
            },
            getTaglist = function (tags, assessment_id) {
                if (tags.length === 0) {
                    return false;
                }
                var div = $("<div>");
                div.append(
                    tags.map(v => {
                        const url = h.getUrlWithParameters(
                            `/ani/assessment/${assessment_id}/endpoints/`,
                            {tags: v.name}
                        );
                        return `<a class="btn btn-light mr-1" href="${url}">${v.name}</a>`;
                    })
                );

                return div;
            },
            isMultigenerational = function (experimentType) {
                return ["Rp", "1r", "2r", "Dv", "Ot"].includes(experimentType);
            };

        tbl.add_tbody_tr("Endpoint name", this.data.name)
            .add_tbody_tr("System", this.data.system)
            .add_tbody_tr("Organ", this.data.organ)
            .add_tbody_tr("Effect", this.data.effect)
            .add_tbody_tr("Effect subtype", this.data.effect_subtype)
            .add_tbody_tr("Diagnostic (as reported)", this.data.diagnostic)
            .add_tbody_tr("Observation time", this.data.observation_time_text)
            .add_tbody_tr("Additional tags", getTaglist(this.data.effects, this.data.assessment))
            .add_tbody_tr("Data reported?", HAWCUtils.booleanCheckbox(this.data.data_reported))
            .add_tbody_tr("Data extracted?", HAWCUtils.booleanCheckbox(this.data.data_extracted))
            .add_tbody_tr(
                "Values estimated?",
                HAWCUtils.booleanCheckbox(this.data.values_estimated)
            )
            .add_tbody_tr("Location in literature", this.data.data_location);

        if (this.data.expected_adversity_direction > 0) {
            tbl.add_tbody_tr(
                "Expected response<br>adversity direction",
                this.data.expected_adversity_direction_text
            );
        }

        tbl.add_tbody_tr(this.data.noel_names.noel, critical_dose("NOEL"))
            .add_tbody_tr(this.data.noel_names.loel, critical_dose("LOEL"))
            .add_tbody_tr("FEL", critical_dose("FEL"))
            .add_tbody_tr("Benchmark dose modeling", bmd_response(null, true));

        let tmp = this.data.monotonicity;
        if (tmp && tmp != "unclear") {
            tbl.add_tbody_tr("Monotonicity", tmp);
        }

        tbl.add_tbody_tr("Statistical test description", this.data.statistical_test);

        tmp = this.data.trend_result;
        if (tmp && tmp != "not applicable") {
            tbl.add_tbody_tr("Trend result", tmp);
        }

        tbl.add_tbody_tr("Trend <i>p</i>-value", this.data.trend_value)
            .add_tbody_tr("Power notes", this.data.power_notes)
            .add_tbody_tr("Results notes", this.data.results_notes);

        if (isMultigenerational(this.data.experiment_type)) {
            tbl.add_tbody_tr("Litter Effects", this.data.litter_effects_display, {
                annotate: this.data.litter_effect_notes,
            });
        }

        $(div).html(tbl.get_tbl());
    }

    build_general_notes(div) {
        if (!h.hasInnerText(this.data.endpoint_notes)) {
            return;
        }
        let tbl = new BaseTable();
        tbl.addHeaderRow(["Methodology"]);
        tbl.setColGroup([100]);
        tbl.tbody.append(`<tr><td>${this.data.endpoint_notes}</td></tr>`);
        $(div).html(tbl.getTbl());
    }

    _dichotomous_percent_change_incidence(eg) {
        return eg.isReported ? Math.round((eg.incidence / eg.n) * 100, 3) : "NR";
    }

    _continuous_percent_difference_from_control(eg, eg_control) {
        var txt = "NR";
        if (eg_control.isReported && eg.isReported && eg_control.response !== 0) {
            txt = Math.round(
                100 * ((eg.response - eg_control.response) / eg_control.response),
                3
            ).toString();
        }
        return txt;
    }

    add_endpoint_group_footnotes(footnote_object, endpoint_group_index) {
        var footnotes = [],
            self = this;
        if (self.data.groups[endpoint_group_index].significant) {
            const sigLevel = self.data.groups[endpoint_group_index].significance_level;
            footnotes.push(`Significantly different from control (<i>p</i> < ${sigLevel})`);
        }
        if (self.data.NOEL == endpoint_group_index) {
            footnotes.push(`${this.data.noel_names.noel} (${this.data.noel_names.noel_help_text})`);
        }
        if (self.data.LOEL == endpoint_group_index) {
            footnotes.push(`${this.data.noel_names.loel} (${this.data.noel_names.loel_help_text})`);
        }
        if (self.data.FEL == endpoint_group_index) {
            footnotes.push("FEL (Frank Effect Level)");
        }
        return footnote_object.add_footnote(footnotes);
    }

    _percent_change_control(index) {
        try {
            if (this.data.data_type == "C") {
                return this._continuous_percent_difference_from_control(
                    this.data.groups[index],
                    this.data.groups[0]
                );
            } else if (this.data.data_type == "P") {
                return this.data.groups[index].response;
            } else if (this.data.data_type == "D") {
                return this._dichotomous_percent_change_incidence(this.data.groups[index]);
            }
        } catch (_err) {
            return "-";
        }
    }

    displayAsModal(opts) {
        var complete = opts ? opts.complete : true,
            modal = new HAWCModal(),
            title = `<h4>${this.build_breadcrumbs()}</h4>`,
            $details = $('<div class="col-md-12">'),
            $plot = $('<div style="height:300px; width:300px">'),
            $tbl = $('<table class="table table-sm table-striped">'),
            $content = $('<div class="container-fluid">'),
            $notes = $('<div class="col-md-12">'),
            $study,
            $exp,
            $ag,
            $end,
            exp,
            ag,
            tabs,
            divs;

        if (complete) {
            tabs = $('<ul class="nav nav-tabs">').append(`
                <li class="nav-item"><a class="nav-link" href="#modalStudy" data-toggle="tab">Study</a></li>
                <li class="nav-item"><a class="nav-link" href="#modalExp" data-toggle="tab">Experiment</a></li>
                <li class="nav-item"><a class="nav-link" href="#modalAG" data-toggle="tab">Animal Group</a></li>
                <li class="nav-item"><a class="nav-link active" href="#modalEnd" data-toggle="tab">Endpoint</a></li>
            `);
            $study = $('<div class="tab-pane" id="modalStudy">');
            Study.render(
                this.data.animal_group.experiment.study.id,
                $study,
                tabs.find('a[href="#modalStudy"]')
            );

            $exp = $('<div class="tab-pane" id="modalExp">');
            exp = new Experiment(this.data.animal_group.experiment);
            exp.render($exp);

            $ag = $('<div class="tab-pane" id="modalAG">');
            ag = new AnimalGroup(this.data.animal_group);
            ag.render($ag);

            $end = $('<div class="tab-pane active" id="modalEnd">');
            divs = $('<div class="tab-content">').append($study, $exp, $ag, $end);
            $content.prepend(tabs, divs);
        } else {
            $end = $content;
        }

        $end.append($('<div class="row">').append($details))
            .append(
                $('<div class="row">')
                    .append($('<div class="col-md-7">').append($tbl))
                    .append($('<div class="col-md-5">').append($plot))
            )
            .append($('<div class="row">').append($notes));

        this.build_details_table($details);
        this.build_endpoint_table($tbl);
        this.build_general_notes($notes);
        modal.getModal().on("shown.bs.modal", () => this.renderPlot($plot, {showBmd: true}));

        modal.addHeader(title).addBody($content).addFooter("").show({maxWidth: 1200});
    }

    hasEGdata() {
        return this.data.groups.length > 0 && _.some(_.map(this.data.groups, "isReported"));
    }

    defaultDoseAxis() {
        var doses = _.chain(this.data.groups)
            .map("dose")
            .filter(d => d > 0)
            .value();
        doses = d3.extent(doses);
        if (doses.length !== 2) return "linear";
        return Math.log10(doses[1]) - Math.log10(doses[0]) >= 3 ? "log" : "linear";
    }

    renderPlot($div, options) {
        const epc = new EndpointPlotContainer(this, $div);
        if (options.showBmd) {
            this.data.bmds
                .filter(d => d.model !== null)
                .forEach(d => {
                    new BmdLine(d.model, epc.scatter, "blue").render();
                });
        }
        return epc;
    }
}

export default Endpoint;

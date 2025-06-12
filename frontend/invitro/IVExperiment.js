import _ from "lodash";
import DescriptiveTable from "shared/utils/DescriptiveTable";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import $ from "$";

import IVEndpoint from "./IVEndpoint";

class IVExperiment {
    constructor(data) {
        this.data = data;
        this.initEndpoints();
    }

    static get_detail_url(id) {
        return `/in-vitro/experiment/${id}/`;
    }

    static get_object(id, cb) {
        $.get(`/in-vitro/api/experiment/${id}/`, d => cb(new IVExperiment(d)));
    }

    static displayAsModal(id) {
        IVExperiment.get_object(id, d => d.displayAsModal());
    }

    static displayAsPage(id, div) {
        IVExperiment.get_object(id, d => d.displayAsPage(div));
    }

    initEndpoints() {
        this.endpoints = [];
        if (this.data.endpoints) {
            this.endpoints = _.map(this.data.endpoints, d => new IVEndpoint(d));
            delete this.data.endpoints;
        }
    }

    build_title() {
        var el = $("<div class='d-flex'>").append($("<h2>").text(this.data.name));
        if (window.canEdit) {
            var urls = [
                "Experiment editing",
                {href: this.data.url_update, text: "Update"},
                {href: this.data.url_delete, text: "Delete"},
                "Endpoint editing",
                {href: this.data.url_create_endpoint, text: "Create endpoint"},
            ];
            el.append(HAWCUtils.pageActionsButton(urls));
        }
        return el;
    }

    build_details_table() {
        var getControlText = function (bool, str) {
                var txt = HAWCUtils.booleanCheckbox(bool);
                if (bool && str) txt = str;
                return txt;
            },
            pos = getControlText(this.data.has_positive_control, this.data.positive_control),
            neg = getControlText(this.data.has_negative_control, this.data.negative_control),
            veh = getControlText(this.data.has_vehicle_control, this.data.vehicle_control),
            naive = getControlText(this.data.has_naive_control, "");

        return new DescriptiveTable()
            .add_tbody_tr("Cell type", this.data.cell_type.cell_type)
            .add_tbody_tr("Tissue", this.data.cell_type.tissue)
            .add_tbody_tr("Species", this.data.cell_type.species)
            .add_tbody_tr("Strain", this.data.cell_type.strain)
            .add_tbody_tr("Sex", this.data.cell_type.sex_symbol)
            .add_tbody_tr("Cell source", this.data.cell_type.source)
            .add_tbody_tr("Culture type", this.data.cell_type.culture_type)
            .add_tbody_tr("Transfection", this.data.transfection)
            .add_tbody_tr("Cell notes", this.data.cell_notes)
            .add_tbody_tr("Dosing notes", this.data.dosing_notes)
            .add_tbody_tr("Metabolic activation", this.data.metabolic_activation)
            .add_tbody_tr("Serum", this.data.serum)
            .add_tbody_tr("Naive control", naive)
            .add_tbody_tr("Positive control", pos)
            .add_tbody_tr("Negative control", neg)
            .add_tbody_tr("Vehicle control", veh)
            .add_tbody_tr("Control notes", this.data.control_notes)
            .add_tbody_tr("Dose units", this.data.dose_units.name)
            .get_tbl();
    }

    build_endpoint_list() {
        var ul = $("<ul>");

        if (this.endpoints.length === 0) {
            ul.append("<li><i>No endpoints available.</i></li>");
        }

        this.endpoints.forEach(function (d) {
            ul.append($("<li>").html(d.build_hyperlink()));
        });

        return ul;
    }

    displayAsModal() {
        var modal = new HAWCModal(),
            $details = $('<div class="col-md-12">'),
            $content = $('<div class="container-fluid">').append(
                $('<div class="row">').append($details)
            );

        $details.append(this.build_details_table());
        modal
            .addTitleLinkHeader(this.data.name, this.data.url)
            .addBody($content)
            .addFooter("")
            .show({maxWidth: 900});
    }

    displayAsPage($div) {
        $div.append(this.build_title())
            .append(this.build_details_table())
            .append("<h3>Available endpoints</h3>")
            .append(this.build_endpoint_list());
    }
}

export default IVExperiment;

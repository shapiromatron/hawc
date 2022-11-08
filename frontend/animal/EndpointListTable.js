import _ from "lodash";
import BaseTable from "shared/utils/BaseTable";

import $ from "$";

import Endpoint from "./Endpoint";

const endpointRow = function(endpoint) {
    const link = `<a href="${endpoint.data.url}" target="_blank">${endpoint.data.name}</a>`,
        detail = $(
            '<i class="fa fa-eye previewModalIcon ml-2" title="preview in a modal">'
        ).click(() => endpoint.displayAsModal({complete: true})),
        ep = $('<span class="previewModalParent">').append(link, detail),
        study = endpoint.data.animal_group.experiment.study,
        experiment = endpoint.data.animal_group.experiment,
        animalGroup = endpoint.data.animal_group,
        row = [
            `<a href="${study.url}" target="_blank">${study.short_citation}</a>`,
            `<a href="${experiment.url}" target="_blank">${experiment.name}</a>`,
            `<a href="${animalGroup.url}" target="_blank">${animalGroup.name}</a>`,
            ep,
            endpoint.doseUnits.activeUnit.name,
            endpoint.get_special_dose_text("NOEL"),
            endpoint.get_special_dose_text("LOEL"),
            endpoint.get_special_bmd_value("BMD"),
            endpoint.get_special_bmd_value("BMDL"),
        ];
    return row;
};

class EndpointListTable {
    constructor(endpoints, dose_id) {
        this.endpoints = endpoints.map(d => new Endpoint(d));
        if (_.isFinite(dose_id)) {
            this.endpoints.forEach(e => e.doseUnits.activate(dose_id));
        }
        this.tbl = new BaseTable();
    }

    build_table() {
        if (this.endpoints.length === 0) return "<p>No endpoints available.</p>";

        var tbl = this.tbl,
            headers = [
                "Study",
                "Experiment",
                "Animal group",
                "Endpoint",
                "Units",
                this.endpoints[0].data.noel_names.noel,
                this.endpoints[0].data.noel_names.loel,
                "BMD",
                "BMDLS",
            ],
            headersToSortKeys = tbl.makeHeaderToSortKeyMapFromOrderByDropdown(
                "select#id_order_by",
                {
                    "experiment name": "experiment",
                    "endpoint name": "endpoint",
                    "dose units": "units",
                }
            );

        tbl.setColGroup([12, 16, 17, 31, 10, 7, 7]);
        tbl.addHeaderRow(headers);
        headersToSortKeys.noael = "-NOEL";
        headersToSortKeys.noel = "-NOEL";
        headersToSortKeys.nel = "-NOEL";
        headersToSortKeys.loael = "-LOEL";
        headersToSortKeys.loel = "-LOEL";
        headersToSortKeys.lel = "-LOEL";
        tbl.enableSortableHeaderLinks($("#initial_order_by").val(), headersToSortKeys);
        this.endpoints.forEach(endpoint => tbl.addRow(endpointRow(endpoint)));
        return tbl.getTbl();
    }
}

export default EndpointListTable;

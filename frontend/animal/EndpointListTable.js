import BaseTable from "utils/BaseTable";

class EndpointListTable {
    constructor(endpoints, dose_id) {
        if (dose_id) {
            endpoints.forEach(e => e.switch_dose_units(dose_id));
        }
        this.endpoints = endpoints;
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

        this.endpoints.forEach(v => tbl.addRow(v.build_endpoint_list_row()));
        return tbl.getTbl();
    }
}

export default EndpointListTable;

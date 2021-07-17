import BaseTable from "utils/BaseTable";
import MetaResult from "./MetaResult";

class MetaResultListTable {
    constructor(endpoint_data) {
        this.endpoints = endpoint_data.map(d => new MetaResult(d));
        this.table = new BaseTable();
    }

    buildTable() {
        if (this.endpoints.length === 0) {
            return "<p>No results available.</p>";
        }

        var table = this.table,
            headers = [
                "Study",
                "Meta result",
                "Protocol",
                "Health outcome",
                "Exposure",
                "Confidence interval",
                "Estimate",
            ];
        table.setColGroup([10, 16, 19, 12, 11, 10, 10]);
        table.addHeaderRow(headers);
        this.endpoints.map(endpoint => {
            table.addRow(endpoint.buildListRow());
        });
        return table.getTbl();
    }
}

export default MetaResultListTable;

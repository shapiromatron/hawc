import BaseTable from "shared/utils/BaseTable";

class MetaResultListTable {
    constructor(endpoints) {
        this.endpoints = endpoints;
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

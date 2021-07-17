import $ from "$";
import BaseTable from "utils/BaseTable";
import Outcome from "./Outcome";

class OutcomeListTable {
    constructor(data) {
        this.outcomes = data.map(d => new Outcome(d));
        this.table = new BaseTable();
    }

    buildTable() {
        if (this.outcomes.length === 0) {
            return "<p>No endpoints available.</p>";
        }

        var table = this.table,
            headers = ["Study", "Study population", "Outcome", "System", "Effect", "Diagnostic"];
        table.setColGroup([12, 25, 16, 17, 10, 13]);
        table.addHeaderRow(headers);

        var headersToSortKeys = table.makeHeaderToSortKeyMapFromOrderByDropdown(
            "select#id_order_by",
            {
                "outcome name": "outcome",
            }
        );

        table.enableSortableHeaderLinks($("#initial_order_by").val(), headersToSortKeys);

        this.outcomes.map(outcome => {
            table.addRow(outcome.buildListRow());
        });
        return table.getTbl();
    }
}

export default OutcomeListTable;
